"""Read-only OpenSkin discovery. Python standard library + curl; no AWS calls."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode


MARKETS = ("steam", "skinport", "buff", "youpin", "csfloat")
WEARS = ("Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred")


def positive_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def profile_fields(rows):
    """Count field presence, nulls and observed types; do not inspect pattern arrays."""
    fields = defaultdict(Counter)

    def visit(obj, prefix=""):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            fields[path]["present"] += 1
            fields[path][type(value).__name__] += 1
            if isinstance(value, dict):
                visit(value, path)

    for row in rows:
        visit(row)
    return {key: dict(value) for key, value in sorted(fields.items())}


def summarize_bulk(payload):
    data = payload["data"]
    if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
        raise ValueError("Expected data map containing item objects")
    result = {"reported_count": payload.get("count"), "unique_names": len(data),
              "count_matches": payload.get("count") == len(data),
              "updated_at": payload.get("updated_at"), "markets": {},
              "variants": {"stattrak": 0, "souvenir": 0, "regular": 0,
                           "wear": dict.fromkeys(WEARS, 0), "no_wear_suffix": 0}}
    for name in data:
        category = "stattrak" if "StatTrak\u2122" in name else "souvenir" if name.startswith("Souvenir ") else "regular"
        result["variants"][category] += 1
        wear = next((w for w in WEARS if name.endswith(f"({w})")), None)
        if wear:
            result["variants"]["wear"][wear] += 1
        else:
            result["variants"]["no_wear_suffix"] += 1
    for market in MARKETS:
        counts = Counter(dict.fromkeys(("object_present", "positive_ask", "positive_bid", "ask_and_bid", "missing_timestamp"), 0))
        currencies = Counter()
        timestamps = []
        for row in data.values():
            quote = row.get(market)
            if not isinstance(quote, dict):
                continue
            counts["object_present"] += 1
            ask = positive_number(quote.get("ask"))
            bid = positive_number(quote.get("highest_bid" if market == "csfloat" else "bid"))
            counts["positive_ask"] += ask
            counts["positive_bid"] += bid
            counts["ask_and_bid"] += ask and bid
            currencies[str(quote.get("currency"))] += 1
            if quote.get("updated_at"):
                timestamps.append(quote["updated_at"])
            else:
                counts["missing_timestamp"] += 1
        result["markets"][market] = {**counts, "ask_coverage_pct": round(100 * counts["positive_ask"] / len(data), 2) if data else 0,
                                     "currencies": dict(currencies),
                                     "oldest_updated_at": min(timestamps, default=None),
                                     "newest_updated_at": max(timestamps, default=None)}
    result["field_profile"] = profile_fields(data.values())
    return result


class Probe:
    def __init__(self, output, base_url):
        self.output = output
        self.base_url = base_url.rstrip("/")
        self.requests = []

    def request(self, label, path, params=None, body=None, url=None):
        requested_at = datetime.now(timezone.utc).isoformat()
        url = url or self.base_url + path
        if params:
            url += "?" + urlencode(params)
        raw = self.output / f"{label}.body"
        headers = self.output / f"{label}.headers"
        command = ["curl.exe", "--silent", "--show-error", "--location", "--max-time", "90",
                   "--max-filesize", "157286400", "--user-agent", "Mozilla/5.0",
                   "--header", "Accept-Encoding: gzip", "--dump-header", str(headers),
                   "--output", str(raw), "--write-out", "%{json}"]
        if body is not None:
            request_file = self.output / f"{label}.request.json"
            request_file.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
            command += ["--header", "Content-Type: application/json", "--data-binary", f"@{request_file}"]
        command.append(url)
        process = subprocess.run(command, capture_output=True, text=True, timeout=100)
        try:
            metrics = json.loads(process.stdout)
        except json.JSONDecodeError:
            metrics = {}
        record = {"label": label, "url": url, "method": "POST" if body is not None else "GET",
                  "requested_at_utc": requested_at,
                  "curl_exit_code": process.returncode, "http_status": metrics.get("http_code"),
                  "elapsed_seconds": metrics.get("time_total"), "download_bytes": metrics.get("size_download"),
                  "error": process.stderr.strip() or None}
        self.requests.append(record)
        payload = None
        if raw.exists():
            wire = raw.read_bytes()
            record["body_sha256"] = hashlib.sha256(wire).hexdigest()
            record["saved_body_bytes"] = len(wire)
            try:
                decoded = gzip.decompress(wire) if wire.startswith(b"\x1f\x8b") else wire
                record["decoded_bytes"] = len(decoded)
                record["gzip_body"] = wire.startswith(b"\x1f\x8b")
                payload = json.loads(decoded)
                record["top_level_keys"] = list(payload) if isinstance(payload, dict) else None
            except (ValueError, OSError, EOFError) as exc:
                record["parse_error"] = str(exc)
        if headers.exists():
            allowed = {"content-type", "content-encoding", "content-length", "cache-control", "age", "date", "retry-after"}
            record["headers"] = {line.split(":", 1)[0].lower(): line.split(":", 1)[1].strip()
                                 for line in headers.read_text(encoding="utf-8", errors="replace").splitlines()
                                 if ":" in line and line.split(":", 1)[0].lower() in allowed}
        print(f"{label}: HTTP {record['http_status']}, {record.get('download_bytes')} bytes", flush=True)
        time.sleep(0.25)
        if process.returncode or record["http_status"] == 429:
            raise RuntimeError(f"Request stopped: {label}; see saved request metrics")
        return payload if record["http_status"] == 200 else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://api.openskin.dev")
    parser.add_argument("--output", type=Path, default=Path("data/raw/openskin") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    probe = Probe(args.output, args.base_url)
    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url,
              "coverage_definition": "Positive finite ask / unique bulk names; presence alone is not a price.",
              "requests": probe.requests}
    try:
        report["health"] = probe.request("health", "/health")
        report["spec_server_health"] = probe.request("spec_server_health", "/health", url="https://api-v2.openskin.dev/health")
        first = probe.request("items_page_1", "/v1/items", {"limit": 500, "page": 1})
        if first:
            report["catalog_first_page"] = {k: v for k, v in first.items() if k != "data"}
            report["catalog_field_profile"] = profile_fields(first["data"])
            last_page = math.ceil(first["total"] / 500)
            last = probe.request("items_last_page", "/v1/items", {"limit": 500, "page": last_page})
            report["catalog_last_page_count"] = len(last["data"]) if last else None
            report["catalog_filter_totals"] = {}
            for field in ("stattrak", "souvenir"):
                filtered = probe.request(f"items_{field}", "/v1/items", {field: "true", "limit": 1})
                report["catalog_filter_totals"][field] = filtered.get("total") if filtered else None
        item = "AK-47 | Redline (Field-Tested)"
        single = probe.request("single", "/v1/prices", {"item": item})
        report["single_sample"] = single
        for market in MARKETS:
            probe.request(f"single_{market}", f"/v1/prices/{market}", {"item": item})
        names = [item, "StatTrak\u2122 AK-47 | Redline (Field-Tested)", "Souvenir AWP | Dragon Lore (Factory New)", "\u2605 Karambit | Doppler (Factory New)"]
        batch = probe.request("batch", "/v1/prices/batch", body={"items": names})
        report["batch_returned_names"] = list(batch.get("data", {})) if batch else None
        probe.request("missing_parameter", "/v1/prices")
        probe.request("unknown_item", "/v1/prices", {"item": "__cs2_analytics_validation_nonexistent__"})
        bulk = probe.request("bulk", "/v1/prices/all")
        if bulk:
            report["bulk"] = summarize_bulk(bulk)
            report["sample_names_in_bulk"] = {name: name in bulk["data"] for name in names}
            report["catalog_total_matches_bulk"] = first["total"] == len(bulk["data"]) if first else None
        expected = {"spec_server_health": (200, 503), "missing_parameter": (400,), "unknown_item": (404,)}
        report["endpoint_checks"] = {r["label"]: r["http_status"] in expected.get(r["label"], (200,)) and "parse_error" not in r
                                     for r in probe.requests}
        report["run_completed"] = True
        report["validation_passed"] = (all(report["endpoint_checks"].values()) and "bulk" in report
                                         and report["bulk"]["count_matches"]
                                         and report.get("catalog_total_matches_bulk") is True
                                         and report.get("batch_returned_names") is not None
                                         and set(report["batch_returned_names"]) == set(names))
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        report["run_completed"] = False
        report["failure"] = str(exc)
    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Report: {args.output / 'report.json'}", flush=True)
    return 0 if report.get("validation_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())

# Architecture Decisions

## 2026-10-28 — Local OpenSkin discovery and next ingestion boundary

- Use the verified public v1 host `https://api.openskin.dev`, configurable in the
  validation CLI. The published OpenAPI server `api-v2.openskin.dev` returned
  503/degraded with older source data; do not silently fail over to it.
- Prefer one gzip `/v1/prices/all` snapshot for the next local Bronze collector,
  rather than 38,043 per-item requests. Measured: 6.60 MiB compressed,
  60.06 MiB decoded. Runtime memory and AWS suitability still require measurement.
- Preserve complete `market_hash_name` as source identity. Use catalog metadata
  for classification; name matching is exploratory until discrepancies are resolved.
- Preserve raw payloads locally, including source-provided nested variant data,
  without analyzing individual float or paint seeds. Normalized models must retain
  missing quote semantics and source timestamps.
- For this Windows discovery tool, Python orchestrates curl and profiles JSON.
  Default urllib received 403 while curl succeeded. This is an observed difference,
  not a proven cause or a production Lambda HTTP-client decision.
- Use root STATUS.md as the sole progress record. The user removed the redundant
  docs entry point; AGENTS.md now references the root file for reads and updates.

No AWS architecture was deployed or cost commitment made.

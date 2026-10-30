# Project Status

Last verified: 2026-10-30 (America/Los_Angeles).

## Current phase

V1 — Data Ingestion & Basic Query. Local OpenSkin discovery completed;
production ingestion is not implemented. No AWS resources created or deployed.

The revised proposal now targets PostgreSQL, Python/dbt, Airflow and read-only
SQL tools with Streamlit + AI Agent/RAG in V1. These components are planned;
the architecture change does not represent additional implemented functionality.

## Verified progress

- Reviewed the revised proposal's text, tables and both architecture/data-model
  diagrams on 2026-10-30, and compared its text with the committed prior version.
  Aligned README.md, AGENTS.md, docs/ROADMAP.md and docs/DECISIONS.md. V1/V2/V3
  estimates now total 84/36/38 hours (158 overall). Source proposal preserved.
- Reran all six existing offline unit tests on 2026-10-30; all passed. No new live
  API, database, dbt, Airflow, AI or AWS validation was performed for this update.
- Configured AGENTS.md to commit and push completed tasks to origin/main after
  relevant checks, under the user's standing authorization. Confirmed the local
  main branch and origin URL for Maxli97/cs2-market-analytics.
- Unified progress tracking in root STATUS.md after the user removed the redundant
  docs entry point; updated AGENTS.md and the documentation decision accordingly.
- Read AGENTS.md and README.md; inspected the initially empty src/ and test/.
- Added src/validate_openskin.py (Python standard library + Windows curl).
- Executed 16 public API requests at approximately 20:39 PDT on 2026-10-28
  (2026-10-29 03:39 UTC). The v1 host returned expected statuses;
  the alternate OpenAPI host health endpoint returned 503/degraded.
- Bulk contained 38,043 unique names, matching its count and the catalog total.
- Measured marketplace coverage, actual fields/types/nulls, name-based variants,
  response sizes, timings and source timestamp ranges.
- Bulk response: 6,916,678 gzip bytes / 62,982,495 decoded JSON bytes.
- Six offline tests passed: python -m unittest discover -s test -v.
- Independently reprofiled the saved bulk and verified all 16 HTTP results,
  catalog/bulk counts and four batch sample names offline.

See [validation report](docs/OPEN_SKIN_API_VALIDATION.md) and
[machine-readable summary](docs/openskin_validation_summary.json).
Local raw responses: data/raw/openskin/20261029T033914Z/ (Git ignored).

## Open issues

- Catalog flags report StatTrak 5,087 / Souvenir 3,137; name-based bulk counts
  are 5,088 / 3,532. Name matching is not authoritative metadata classification.
  StatTrak Swap Tool exists; the Souvenir discrepancy remains unresolved.
- Metadata was sampled at first and last pages, not exhaustively downloaded.
- API health is up, but individual quotes can date back to June/July 2026.
- Single, batch, bulk and market-specific endpoints have different JSON shapes.
- Use the verified https://api.openskin.dev host; the OpenAPI server differs.
- Supplementary catalog queries were not approved and were not executed.
- Historical endpoints, sustained reliability, rate-limit boundaries, native
  Python HTTP compatibility and runtime memory remain unverified.
- Define history grain (price changes versus observations), canonical quote
  field, deduplication/correction rules and daily aggregation semantics before SQL DDL.
- PostgreSQL/Airflow hosting, ETL schedule, retention, monthly budget, SNS recipients
  and LLM/retrieval providers are not selected or configured.
- Proposal's 33,000+ catalog estimate and 118 million monthly theoretical rows
  are planning assumptions. The measured 2026-10-28 catalog was 38,043 names;
  actual valid/history growth depends on market coverage and deduplication.

## Next task

Build a local Bronze collector: gzip snapshots, UTC collection metadata,
idempotent filenames, error handling and schema/count checks. Complete metadata
pagination and reconcile flags before authoritative variant classification.
AWS deployment requires explicit approval.
After the local collector, define the five-table PostgreSQL model and implement
local Python staging loads/dbt transformations, followed by Airflow and bounded
SQL serving. RAG should retrieve schema/metric definitions, not substitute for
live price queries.

## Remaining roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). V1 ingestion, S3 Bronze, PostgreSQL,
Python/dbt, Airflow, dashboard, SQL/AI interfaces and monitoring remain pending.
Glue/Athena/Parquet are no longer baseline delivery requirements under the revised
proposal. V2/V3 have not started.

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

## 2026-10-30 — Adopt the revised proposal architecture and scope

Source: [project proposal.docx](project%20proposal.docx), including both its system
architecture and five-table PostgreSQL diagrams. This supersedes the original
README/roadmap target of S3 Silver/Gold Parquet, Glue and Athena; the 2026-10-28
API measurements and local discovery decisions remain historical evidence.

- Keep EventBridge + Lambda for independent hourly current-price collection.
  Preserve immutable raw JSON batches in S3 Bronze, with timestamps and lineage.
- Use PostgreSQL staging/core/marts for analytical storage and serving. V1 business
  tables are dim_item, dim_market, fact_price_history, price_latest and agg_price_daily.
  Staging and operational checkpoint/batch records are not part of that five-table count.
- Python validates and batch-loads source records; dbt performs SQL cleaning,
  deduplication, incremental transformations, relationship checks and daily aggregation.
  Airflow orchestrates ETL and separate checkpointed backfill/replay runs.
- Store source_updated_at separately from observed_at. Define a stable source record
  key and correction strategy before implementing idempotent loads; repeated hourly
  collection must not accidentally duplicate history or discard legitimate late corrections.
- Both Streamlit and the AI Agent use bounded, read-only SQL tools. RAG retrieves
  schema/metric documentation, while price answers come from actual SQL results.
  Require read-only permissions, parameterization/allowlists, timeouts and row limits.
- Start with local Docker PostgreSQL/Airflow. PostgreSQL provides relational modeling
  and indexed interactive queries, but database and orchestration hosting add ongoing
  costs and operations. Managed RDS/Airflow hosting remains to be evaluated, not assumed.
- Move dbt, Airflow, daily aggregates and AI/RAG query into V1; add AI tool/notification
  enhancements in V2; retain liquidity/anomaly/forecasting work in V3. Adopt proposal
  estimates of 84h, 36h and 38h, totaling 158h.
- Monitor collection failure (90-minute no-success target), quality gates, workflow
  retries/failures, per-market quote freshness and PostgreSQL performance. Planned
  AWS Budget notifications use 50/80/100% thresholds; the actual budget is undecided.

Implementation questions remain: canonical ask/bid/median semantics; history as
price changes versus valid observations; correction/dedup keys; day boundaries,
gap handling and weighting for daily metrics; exact ETL schedules, hosting,
retention and AI providers. These must be resolved before database constraints and
derived metrics are treated as authoritative.

The proposal's catalog/monthly volume estimates are assumptions, not new measured
results; retain the API validation report and JSON summary unchanged. The discovery
script remains compatible with the revised ingestion entry point, so this task
does not change its code or claim any new infrastructure has been implemented.

No AWS resources, databases, DAGs, dbt models or AI integrations were created in
this documentation alignment task. The user's revised proposal is retained byte
for byte and included with its related documentation in the synchronization commit.

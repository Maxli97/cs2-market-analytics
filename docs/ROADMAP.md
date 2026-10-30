# Development Roadmap

Aligned with [project proposal.docx](project%20proposal.docx) on 2026-10-30.
All delivery components below remain planned unless explicitly checked off.
This roadmap does not authorize AWS deployment.

## V1 — Data Ingestion & Basic Query

- [x] Local OpenSkin current-price API discovery and validation.
- [ ] Complete API integration: metadata pagination, variant reconciliation,
  field mapping and quote freshness rules.
- [ ] Local Bronze collector, then approved EventBridge/Lambda hourly collection
  into immutable S3 raw batches with UTC observation times and source lineage.
- [ ] Historical API validation and controlled backfill: batches, checkpoints,
  retries, idempotency and recovery.
- [ ] PostgreSQL local setup, staging and five business tables: dim_item,
  dim_market, fact_price_history, price_latest, agg_price_daily; PK/FK and indexes.
- [ ] Python JSON validation, field conversion and batch loading into staging.
- [ ] dbt cleaning, deduplication, incremental models, relationships and daily aggregates.
- [ ] Airflow ETL and separate backfill DAGs with dependencies, retries and S3 replay.
- [ ] Python/dbt data quality gates, market-specific freshness, CloudWatch and SNS.
- [ ] Streamlit search, market comparison, historical queries and read-only SQL tools.
- [ ] AI Agent tool calling and RAG over schema/metric docs; price answers from SQL.
- [ ] Integration tests, failure/replay checks, deployment review and approval.

### Proposal effort breakdown

| Component | Estimated hours |
|---|---:|
| API Integration | 5 |
| Hourly Data Ingestion | 8 |
| Historical Backfill | 8 |
| Data Storage & Basic ETL | 8 |
| Python Data Loading | 7 |
| dbt Transformation | 10 |
| Airflow Orchestration | 8 |
| Data Quality & Monitoring | 7 |
| Basic Dashboard & SQL Tools | 6 |
| AI Agent & RAG Query | 11 |
| Testing & Deployment | 6 |
| **V1 total** | **84** |

### Implementation sequence and unresolved choices

1. Retain the next task: local raw collection and reliable metadata/field mapping.
2. Define quote semantics, source/observation timestamps, deduplication keys,
   late corrections and daily aggregation before final SQL schema implementation.
3. Establish local Docker PostgreSQL/Airflow, then Python loading and dbt tests.
4. Add replay/backfill orchestration and bounded SQL tools; build the dashboard
   and AI interface on verified query results.
5. Choose hosting, monthly budget, retention, SNS recipients and LLM/retrieval
   providers separately. Evaluate RDS/Airflow persistent costs before AWS approval.

Hourly collection must remain independent of long-running backfill/ETL.
S3 is the Bronze replay source; staging/core/marts are PostgreSQL schemas/models.
Glue, Athena and Parquet are no longer baseline deliverables in this proposal.

## V2 — Advanced Query & Historical Analytics

| Component | Scope | Estimated hours |
|---|---|---:|
| Historical Analytics | Price changes, moving averages, volatility and trends | 8 |
| Market Comparison | Cross-market spreads and price rankings | 6 |
| Dashboard Enhancement | History charts, filters, rankings and interaction | 8 |
| AI Agent Enhancement | MCP/tools, price thresholds and proactive notifications | 8 |
| Optimization & Testing | PostgreSQL indexes, queries, data validation and tests | 6 |
| **V2 total** | | **36** |

## V3 — Liquidity & Forecasting

| Component | Scope | Estimated hours |
|---|---|---:|
| Liquidity Analysis | Activity, bid/ask spreads and liquidity where supported | 6 |
| Anomaly Detection | Price anomalies, thresholds and statistical methods | 6 |
| Price Forecasting | Features and time-series models | 14 |
| Model Evaluation | Backtesting, MAE/RMSE and baseline comparison | 8 |
| Dashboard Integration | Predictions, anomalies and model performance | 4 |
| **V3 total** | | **38** |

**Total planned effort: 158 hours** (84 + 36 + 38), not recorded time spent.

## Monitoring acceptance targets

- Ingestion: API success, counts, S3 writes and last success; SNS email after
  90 minutes without a successful collection.
- Quality/publication: Python/dbt checks for valid values, nulls, duplicates,
  keys and completeness; isolate invalid data or block publication.
- Workflow/recovery: DAG/task state, durations, retries, final failure alerts,
  replay and backfill checkpoints.
- Freshness: source-level timestamps and per-market thresholds; track latest
  and aggregate model freshness independently of source health.
- PostgreSQL: storage/history growth, connections, latency and slow queries.
- Costs: AWS Budgets email at 50%, 80% and 100% of the chosen monthly budget.

AI price queries require read-only permissions, bounded/allowlisted SQL,
timeouts, row limits and answers grounded in actual query outputs.

Preserve all supported item names and variants. Do not analyze individual float or
paint seeds/patterns and do not implement automated trading.

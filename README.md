
# CS2 Multi-Market Price Analytics Platform

## Overview

A cloud-based data engineering platform designed to
collect, store, process, and analyze Counter-Strike 2
(CS2) marketplace data.

The project uses Python, the OpenSkin API, and AWS
services to build an automated data pipeline for
multi-market price comparison and historical analytics.

The platform will collect market data hourly and provide
insights into item prices, market trends, volatility,
liquidity, and potential future price movements. Streamlit and an AI Agent/RAG
interface will share bounded, read-only SQL tools over curated PostgreSQL data.

This project is developed as a Data Engineering portfolio
project, with a focus on reliable data pipelines, cloud
architecture, data modeling, and analytical processing.

## Project Status

**Current Phase:** V1 — Data Ingestion & Basic Query

**Status:** Local OpenSkin API validation completed on 2026-10-28; ingestion implementation pending.

The target design was aligned with the revised
[project proposal](docs/project%20proposal.docx) on 2026-10-30. PostgreSQL,
Python/dbt, Airflow and AI query components below are planned, not implemented.

See [STATUS.md](STATUS.md) for current development progress.

## Planned Features

### V1 — Data Ingestion & Basic Query

- [ ] OpenSkin API integration
- [ ] Hourly automated data collection
- [ ] Historical backfill with checkpoints, retries and idempotent recovery
- [ ] Amazon S3 Bronze raw JSON storage and replay
- [ ] PostgreSQL staging and five core business tables with keys and indexes
- [ ] Python JSON validation, field mapping and batch loading
- [ ] dbt cleaning, deduplication, incremental models and daily aggregation
- [ ] Airflow ETL/backfill DAGs, dependencies, retries and publish checks
- [ ] Data quality, source freshness, CloudWatch logs and SNS email alerts
- [ ] Streamlit item search, cross-market prices and historical queries
- [ ] Shared read-only SQL tools with bounded queries
- [ ] AI Agent tool calling and RAG for schema/metric documentation
- [ ] Local integration testing and approval-gated AWS deployment

### V2 — Advanced Query & Market Analytics

- [ ] Historical price analysis
- [ ] Price changes, moving averages and volatility
- [ ] Cross-market spreads, lowest-price and price-movement rankings
- [ ] Advanced interactive dashboard
- [ ] AI tool/MCP integration, price thresholds and proactive notifications
- [ ] PostgreSQL query/index optimization and additional validation

### V3 — Predictive Analytics & Market Intelligence

- [ ] Market liquidity analysis
- [ ] Price anomaly detection
- [ ] Feature engineering
- [ ] Price forecasting models
- [ ] Time-series backtesting
- [ ] Model evaluation and visualization

## Data Source

**Primary Source:** OpenSkin v1 API

Website: https://openskin.dev/

Planned marketplace coverage:
- Steam Community Market
- Skinport
- BUFF163
- YouPin
- CSFloat

The platform will analyze all supported item variants,
including wear categories and StatTrak versions.

Individual float values and paint patterns are outside
the initial project scope.

Local validation found 38,043 tracked names across the five markets.
Positive ask coverage ranged from 64.82% to 86.09% in the measured snapshot;
coverage includes older quotes and does not guarantee freshness.
See [API validation report](docs/OPEN_SKIN_API_VALIDATION.md) for actual fields,
variant-count caveats, response sizes, and verified endpoint behavior.

The project does not support automated trading.

## Technology Stack

| Category | Technology |
|---|---|
| Programming | Python, SQL |
| Data Source | OpenSkin REST API |
| Scheduling | Amazon EventBridge |
| Data Ingestion | AWS Lambda |
| Raw Storage | Amazon S3 Bronze |
| Analytical Database | PostgreSQL staging / core / marts |
| Data Loading | Python validation and batch loading |
| SQL Transformation | dbt incremental models and tests |
| Workflow Orchestration | Apache Airflow |
| Raw Data Format | JSON (gzip where appropriate) |
| Query Interface | Parameterized, read-only SQL tools |
| Dashboard | Streamlit, Plotly |
| AI Interface | LLM tool calling + RAG for documentation |
| Local Environment | Docker for PostgreSQL and Airflow |
| Monitoring | CloudWatch, SNS, Airflow/dbt, PostgreSQL statistics |
| Cost Monitoring | AWS Budgets |
| Version Control | Git |

Services listed above represent the target architecture.
Only the local API validation script is implemented so far. Glue, Athena,
Redshift and Parquet are no longer baseline delivery requirements in the revised
proposal. Managed PostgreSQL/Airflow hosting and the LLM/retrieval stack remain
to be selected after evaluating operational needs and costs.

## Target System Architecture

The planned data flow is:

```text
OpenSkin API
  |-- EventBridge -> Lambda / Python hourly collector ----+
  |-- Airflow Backfill DAG -> Python historical worker ---+
                                                         |
                                                 S3 Bronze Raw JSON
                                                         |
Airflow ETL DAG: check batch -> Python validate / bulk load
                                                         |
                                                 PostgreSQL staging
                                                         |
                                                   dbt build / tests
                                                         |
                                              PostgreSQL core / marts
                                                         |
                                               Read-only SQL tools
                                                  /             \
                                             Streamlit       AI Agent
                                                                 |
                                                    RAG schema / metric docs
```

Hourly collection remains independent of Airflow ETL and controlled historical
backfill runs. Airflow manages downstream task dependencies, retries, dbt checks
and publication; a delayed backfill must not block current-price collection.
Both historical API backfill and replay of saved S3 batches must support checkpoints
and idempotent reprocessing. Exact ETL schedules remain to be configured.

PostgreSQL serves both dashboard and AI queries. RAG retrieves the data dictionary
and metric definitions; numerical price answers must come from SQL results.
Start with local Docker for PostgreSQL/Airflow; evaluate managed AWS hosting
separately. No AWS deployment is authorized by this design update.

## Data Architecture

### Bronze Raw Storage

S3 stores immutable raw JSON snapshots, historical backfill responses and collection
metadata. Retain source timestamps, UTC observation times and batch/S3 lineage so
data can be audited and replayed. S3 key layout and retention remain to be designed.

### PostgreSQL Staging and Curated Models

Python validates JSON and batch-loads structured records into staging. dbt handles
cleaning, deduplication, incremental transformations, relationships and aggregates.
The revised proposal defines five core business tables (staging and operational
batch/checkpoint records are separate):

| Table | Planned grain and purpose |
|---|---|
| `dim_item` | One unique item variant; unique `market_hash_name`, wear and variant metadata |
| `dim_market` | One marketplace; unique market code and expected refresh interval |
| `fact_price_history` | Item/market price change or valid observation, with source/observation timestamps, raw S3 key and deduplication key |
| `price_latest` | Latest valid quote per item/market; composite key `(item_id, market_id)` |
| `agg_price_daily` | Daily item/market metrics; composite key `(item_id, market_id, price_date)` |

History references the item and market dimensions. Latest/daily models derive from
validated history. Preserve original currency amounts alongside normalized USD
where available, without treating a missing quote as zero.

### Analytical Outputs and Open Modeling Questions

Curated PostgreSQL models provide latest prices and daily aggregates in V1.
Later versions add:
- Historical trends
- Market comparisons
- Price movement rankings
- Liquidity indicators
- Forecasting results

Before implementing SQL models, define the canonical quote type (ask/bid/median),
change-versus-observation history semantics, timestamp-based deduplication and
source corrections. Also define day boundaries, gap handling and daily averaging
so a simple average of change events is not presented as a time-weighted daily price.
Resolve these with API evidence before finalizing schema constraints.

## Update Frequency

- Market price collection: Every hour
- Item metadata synchronization: Periodic
- Current-price ETL: Airflow-controlled after raw batch availability (V1)
- Historical backfill: Separate controlled Airflow runs with checkpoints (V1)
- Daily aggregation: dbt/Airflow models (V1; execution schedule to be configured)
- Advanced analytics: Daily or as needed
- Model training: Periodic (V3)

Collection frequency does not guarantee that all
upstream marketplaces refresh at the same frequency.

## Getting Started

Local discovery requires Python 3.11+ and Windows `curl.exe`; no third-party
Python packages or credentials are required. Run from the project root:

```powershell
python src/validate_openskin.py
```

The command reads public endpoints and downloads one bulk snapshot. It stores
raw response bodies, headers, and report.json under a new UTC timestamp directory
in `data/raw/openskin/` (ignored by Git). Network access is required. Use
`--base-url` or `--output` to override defaults; the output directory must be new.
It stops on transport errors or HTTP 429 and records failures in report.json.
It does not create or deploy AWS resources.

## Testing

```powershell
python -m unittest discover -s test -v
```

Six offline tests passed again on 2026-10-30. A separate live discovery run and offline
raw-snapshot verification are documented in the API validation report.

## Development Roadmap

| Version | Focus | Estimated Effort |
|---|---|---|
| V1 | Ingestion, PostgreSQL/dbt/Airflow, dashboard and AI query | 84 hours |
| V2 | Historical/market analytics, dashboard and AI enhancements | +36 hours |
| V3 | Liquidity, anomalies and forecasting | +38 hours |

**Total Estimated Effort:** 158 hours

These are the revised proposal's planning estimates, not recorded time spent.
See [docs/ROADMAP.md](docs/ROADMAP.md) for the component breakdown and sequencing.

## Monitoring

Planned monitoring includes:
- CloudWatch ingestion metrics: API success, record counts, raw object creation
  and last successful collection; SNS email if no collection succeeds for 90 minutes.
- Python/dbt quality checks: nulls, duplicates, valid prices, keys and completeness;
  isolate invalid data or block publication on failed checks.
- Airflow DAG/task duration, retries, failures and S3 replay/backfill recovery.
- Market-specific source freshness, `price_latest` freshness and aggregate completeness.
- PostgreSQL size, connections, slow queries, query latency and history growth.
- AWS Budgets email thresholds at 50%, 80% and 100% of a monthly budget still to
  be chosen; evaluate persistent database/Airflow costs and S3 retention.

Dashboard and AI tools must use read-only database permissions, parameterized or
allowlisted SQL, timeouts and row limits. Check AI answers against query outputs.
Notifications and LLM integrations are planned; no recipients or providers are configured.

## Data Usage

Market data is provided by OpenSkin.

The project will use documented API endpoints and
respect applicable data usage policies.

Redistribution permissions must be verified before
publishing complete raw datasets.

Market prices and forecasts are informational and do
not guarantee future trading outcomes.

## Documentation

- [AGENTS.md](AGENTS.md): Codex development instructions
- [docs/project proposal.docx](docs/project%20proposal.docx): Revised design and planning source
- [STATUS.md](STATUS.md): Current development progress
- [docs/ROADMAP.md](docs/ROADMAP.md): V1/V2/V3 implementation roadmap
- [docs/OPEN_SKIN_API_VALIDATION.md](docs/OPEN_SKIN_API_VALIDATION.md): Local API findings
- [docs/DECISIONS.md](docs/DECISIONS.md): Architecture decisions

## Future Improvements

Possible future improvements include additional
data sources, faster serving infrastructure, and more
advanced market analytics when justified by actual
requirements and measured performance.

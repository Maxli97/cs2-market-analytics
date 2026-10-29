
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
liquidity, and potential future price movements.

This project is developed as a Data Engineering portfolio
project, with a focus on reliable data pipelines, cloud
architecture, data modeling, and analytical processing.

## Project Status

**Current Phase:** V1 — Data Ingestion & Basic Query

**Status:** Local OpenSkin API validation completed on 2026-10-28; ingestion implementation pending.

See [STATUS.md](STATUS.md) for current development progress.

## Planned Features

### V1 — Data Ingestion & Basic Query

- [ ] OpenSkin API integration
- [ ] Hourly automated data collection
- [ ] Historical data ingestion
- [ ] Amazon S3 raw data storage
- [ ] Basic data cleaning and transformation
- [ ] Parquet historical datasets
- [ ] Basic Amazon Athena queries
- [ ] Streamlit item search
- [ ] Cross-market price comparison
- [ ] Basic pipeline monitoring

### V2 — Advanced Query & Market Analytics

- [ ] AWS Glue ETL pipeline
- [ ] Advanced data quality validation
- [ ] Historical price analysis
- [ ] Price change and volatility calculations
- [ ] Multi-market price comparisons
- [ ] Price movement rankings
- [ ] Advanced interactive dashboard

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
| Cloud Storage | Amazon S3 |
| Data Processing | Python, Pandas, PySpark |
| ETL | AWS Glue |
| Data Format | JSON, Parquet |
| Data Catalog | AWS Glue Data Catalog |
| SQL Analytics | Amazon Athena |
| Dashboard | Streamlit, Plotly |
| Monitoring | Amazon CloudWatch |
| Cost Monitoring | AWS Budgets |
| Version Control | Git |

Services listed above represent the target architecture.
Not all components are implemented in V1.

## Target System Architecture

The planned data flow is:

```text
OpenSkin API
      |
EventBridge + AWS Lambda
      |
Amazon S3
      |
      +-- Bronze: Raw API Data
      |
      +-- Silver: Cleaned Historical Data
      |
      +-- Gold: Analytical Data
      |
AWS Glue + Athena
      |
Python Analytics
      |
Streamlit Dashboard
```

Hourly lightweight processing will maintain the latest
price dataset for fast dashboard access.

Daily processing will transform historical data and
generate analytical datasets.

The project will use S3 and Athena rather than a
dedicated database server during initial development.

## Data Architecture

### Bronze Layer

Stores raw API responses and hourly historical snapshots.

### Silver Layer

Stores cleaned and normalized marketplace data in
Parquet format.

### Gold Layer

Stores precomputed analytical results, including:
- Latest prices
- Historical trends
- Market comparisons
- Price movement rankings
- Liquidity indicators
- Forecasting results

## Update Frequency

- Market price collection: Every hour
- Item metadata synchronization: Periodic
- Historical ETL: Daily (V2)
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

Six offline tests passed on 2026-10-28. A separate live discovery run and offline
raw-snapshot verification are documented in the API validation report.

## Development Roadmap

| Version | Focus | Estimated Effort |
|---|---|---|
| V1 | Data Ingestion & Basic Query | 41 hours |
| V2 | Advanced Query & Analytics | +32 hours |
| V3 | Predictive Analytics | +32 hours |

**Total Estimated Effort:** 105 hours

These estimates exclude additional contingency time.

## Monitoring

Planned monitoring includes:
- API request failures
- Data collection failures
- Data freshness
- Data quality issues
- ETL job status
- AWS cost alerts

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
- [STATUS.md](STATUS.md): Current development progress
- [docs/ROADMAP.md](docs/ROADMAP.md): V1/V2/V3 implementation roadmap
- [docs/OPEN_SKIN_API_VALIDATION.md](docs/OPEN_SKIN_API_VALIDATION.md): Local API findings
- [docs/DECISIONS.md](docs/DECISIONS.md): Architecture decisions

## Future Improvements

Possible future improvements include additional
data sources, faster serving infrastructure, and more
advanced market analytics when justified by actual
requirements and measured performance.

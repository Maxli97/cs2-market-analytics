# Development Roadmap

This roadmap restates the README scope; it does not authorize AWS deployment.

## V1 — Data Ingestion & Basic Query

- [x] Local OpenSkin current-price API discovery and validation.
- [ ] Full item metadata synchronization and variant flag reconciliation.
- [ ] Local Bronze collector with request/error handling and collection metadata.
- [ ] Historical API validation and bounded historical backfill.
- [ ] Approval of AWS resources and cost controls before deployment.
- [ ] EventBridge hourly scheduling and Lambda ingestion.
- [ ] S3 Bronze raw snapshots; Python cleaning and Silver Parquet datasets.
- [ ] Basic Athena queries and cross-market comparisons.
- [ ] Streamlit item search and price display.
- [ ] CloudWatch monitoring, freshness checks, and cost alerts.

## V2 — Advanced Query & Historical Analytics

- AWS Glue ETL, daily historical processing and advanced data quality validation.
- Historical analysis, price changes, volatility, rankings and dashboard improvements.

## V3 — Liquidity & Forecasting

- Liquidity analysis, anomaly detection, features and forecasting models.
- Time-series backtesting, evaluation and visualization.

Preserve all supported item names and variants. Do not analyze individual float or
paint seeds/patterns and do not implement automated trading.

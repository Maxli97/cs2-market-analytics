
# CS2 Market Analytics — Agent Instructions

## Project
Build a CS2 market analytics platform using Python,
OpenSkin API, and AWS.

## Architecture
- Hourly ingestion: EventBridge + Lambda
- Storage: S3 Bronze / Silver / Gold
- ETL: Python, later AWS Glue
- Queries: Athena SQL
- Dashboard: Streamlit
- Monitoring: CloudWatch

## Scope
- V1: Complete data ingestion and basic queries
- V2: Advanced queries and historical analytics
- V3: Liquidity analysis and price forecasting
- Preserve all supported item variants
- Do not analyze individual Float or Pattern
- Do not implement automated trading

## Before Starting Any Task
1. Read root STATUS.md and docs/ROADMAP.md.
2. Inspect relevant existing code.
3. Explain the proposed changes before implementation.
4. Keep changes limited to the requested task.

## Development Rules
- Use Python with clear, maintainable code.
- Add tests for important data transformations.
- Never hardcode credentials or AWS secrets.
- Do not deploy AWS resources without approval.
- Avoid unnecessary AWS costs.
- Do not claim tests passed unless executed.

## After Completing a Task
1. Run available relevant tests.
2. Summarize changed files and test results.
3. Update root STATUS.md with verified progress.
4. Record important architecture decisions in
   docs/DECISIONS.md when necessary.

## Git Workflow
- The user authorizes automatic commit and push after each requested task.
- Run relevant checks and update root STATUS.md before committing.
- Commit only changes related to the task with a clear commit message.
- Push the completed task commit to origin/main automatically.
- Verify origin points to https://github.com/Maxli97/cs2-market-analytics.git
  and the current branch is main before committing or pushing. Report a mismatch
  instead of switching branches or changing remotes automatically.
- Do not commit credentials, .env files, or raw API datasets.
- Never force-push or overwrite unrelated user changes.
- If checks fail, authentication fails, or remote changes prevent a normal push,
  report the issue rather than forcing synchronization.
- Confirm the push succeeded and include the commit ID in the completion summary.
- This authorization does not authorize AWS deployment.

## Communication
- Explain concepts in Chinese.
- Keep code and technical identifiers in English.
- Explain significant design choices and trade-offs.

# MCP Financial Analyst

A simple local tool for turning stock questions into useful market analysis.

MCP Financial Analyst is meant for privacy-minded market research. It works through a short sequence of steps:

- Plan the request and identify the relevant symbols
- Gather market data from yfinance
- Summarize performance, trends, and risk
- Check the result before returning it

It uses the Model Context Protocol (MCP), so it can work with tools like Cursor, Claude Desktop, or custom clients.

## How it works

```text
User Query
  ↓
MCP Client / IDE
  ↓
MCP Server (server.py)
  ↓
Analysis flow (finance_tool.py)
  ├─ Planning step
  │   - understands the request
  │   - extracts the relevant tickers and timeframe
  │   - builds a short execution plan
  ├─ Data step
  │   - pulls market data from yfinance
  │   - prepares the dataset for review
  ├─ Analysis step
  │   - calculates price movement and volatility
  │   - builds a concise summary
  └─ Review step
      - checks that the result is coherent
      - flags missing or partial data

## Orchestration

The main orchestration is implemented in `finance_tool.py` and exposed via MCP tools in `server.py`.

- A request arrives at the MCP server (`analyze_stock` or `plan_analysis`).
- The server calls into the analysis module which runs a short, synchronous sequence:
  1. Build a concise plan (identify symbols, timeframe, intent).
  2. Fetch market data (using `yfinance`) and normalize it.
  3. Run the analysis step to compute price movement and volatility.
  4. Run a lightweight verification pass that flags missing or partial data.

The flow is intentionally simple and deterministic so it is easy to test and extend. Each step logs a compact event and updates in-process counters so you can track how often each operation runs.

## Observability

The repository includes basic observability primitives so you can tell what the system is doing:

- Structured logs: `server.py` configures a basic logger; `finance_tool.py` logs plan creation, fetch attempts, analysis starts/completion, and errors.
- Runtime metrics: an in-process counters map (`get_metrics()`) is provided for quick inspection. The MCP tool `metrics()` returns these counters as JSON.
- Verification output: analysis results include a `verification` field that reports whether the output is complete or partial.

How to use them:

1. Start the server and call `plan_analysis(query)` to see the execution plan.
2. Call `analyze_stock(query)` to run the analysis; check logs for step-level events.
3. Call `metrics()` to get counters such as requests, successes, failures, plans, data_fetches, and analyses.

Notes on production readiness:

- Logs are plain-text by default; swap in a JSON formatter or ship logs to a log-collector for production.
- The metrics API is a lightweight helper. This project provides optional Prometheus support via `prometheus_client`.

### Prometheus metrics

If `prometheus_client` is installed, the server starts a small HTTP endpoint on port `8000` that exposes runtime counters for scraping.

Quick setup:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
python server.py
```

3. Configure Prometheus to scrape `http://<host>:8000` (see example below).

Example `prometheus.yml` snippet:

```yaml
scrape_configs:
  - job_name: 'mcp_financial'
    static_configs:
      - targets: ['localhost:8000']
```

The exposed metric names are simple counters such as `mcp_financial_requests`, `mcp_financial_successes`, and `mcp_financial_failures`.

For production, consider integrating a full-featured metrics pipeline and exporting richer histograms or timing metrics.
- For safer execution of any generated code, add sandboxing (containers or separate processes) and stricter validation.

```

## What it does

- Natural-language financial queries such as:
  - "Compare Apple and Microsoft over the last year"
  - "Show Tesla volatility for the last 6 months"
  - "Analyze the trend for Nvidia"
- Structured JSON output rather than a single raw script
- Local-first data retrieval using yfinance
- A design that can be expanded later with tools such as:
  - news ingestion
  - portfolio context
  - chart generation
  - vector memory
  - sandboxed code execution

## Technical stack

- Python 3.10+
- MCP server runtime via FastMCP
- yfinance for market data
- Optional local LLM runtime via Ollama and DeepSeek for richer reasoning later

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/MCP_Financial_Analyst.git
cd MCP_Financial_Analyst
pip install yfinance mcp
```

## Running the server

```bash
python server.py
```

The server exposes the following MCP tools:

- analyze_stock(query): runs the full analysis workflow
- plan_analysis(query): returns the execution plan before the analysis step
- save_code(code): legacy helper for saving generated Python code
- run_code_and_show_plot(): legacy helper for executing a saved script

## Next steps

The next step is to make the system more useful by adding:

- a tighter planning and review loop
- support for news and portfolio context
- simple memory for follow-up questions
- sandboxed execution for generated code
- optional integration with a more advanced orchestration layer

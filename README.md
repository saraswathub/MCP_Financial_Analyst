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

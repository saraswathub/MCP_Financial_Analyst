# MCP Financial Analyst

**A fully local, natural language-driven stock market analysis system powered by multi-agent AI**

MCP Financial Analyst is a privacy-focused, 100% local financial analysis tool that transforms natural language queries into executable Python code for retrieving, analyzing, and visualizing stock market data.

It uses:
- **CrewAI** for multi-agent orchestration
- **DeepSeek-R1** (local LLM via Ollama in Docker)
- **Modular Command Platform (MCP)** as the runtime bridge
- **yfinance**, **pandas**, and **matplotlib** for data and charting

All processing happens on your machine — no cloud API keys, no data leaves your computer.

## Features

- Natural language interface for financial queries  
  ("Compare year-to-date performance of AAPL vs MSFT", "Show volatility of NVDA last 6 months", etc.)
- Modular CrewAI agent architecture:
  - **Query Parser Agent** — understands intent and extracts parameters
  - **Code Writer Agent** — generates safe, correct Python analysis code
  - **Code Executor Agent** — runs code in a sandboxed environment
- Chart generation & visualization (line plots, bar charts, candlesticks, etc.)
- Fully local inference using DeepSeek-R1 via Ollama + Docker
- MCP-powered execution environment (great integration with Cursor, Claude Desktop, VS Code, etc.)

## Demo Example

**User query:**

> Plot year-to-date performance for AAPL and MSFT

**What happens behind the scenes:**
1. Query Parser understands: plot → YTD performance → tickers AAPL, MSFT
2. Code Writer generates Python script using yfinance + matplotlib
3. Code Executor runs the script securely
4. Result: beautiful matplotlib chart returned to you

## Architecture
````
User Query
↓ (natural language via MCP client — e.g. Cursor, Claude Desktop, VS Code extension)
MCP Server (server.py)
↓
CrewAI Orchestrator
├─ Query Parser Agent ──► DeepSeek-R1 (via Ollama @ localhost:11434)
│   Extracts intent, tickers, timeframes, analysis type
├─ Code Writer Agent  ──► DeepSeek-R1 (via Ollama)
│   Generates clean, executable Python code using yfinance + pandas + matplotlib
└─ Code Executor Agent ──► Sandboxed execution environment
↓
Data Fetch → Analysis → Plot Generation
↓
Result (text summary + matplotlib chart image) returned via MCP

````

All LLM inference and code execution remain fully local — no external API calls except yfinance data downloads.

## Prerequisites

- Python 3.10 or higher
- Docker (to run Ollama)
- Ollama running in Docker with DeepSeek-R1 pulled
- `uv` (preferred for fast, clean dependency management) or `pip`
- Visual Studio Code (strongly recommended for MCP integration with Cursor or similar tools)

## Setup – Start Ollama with DeepSeek-R1

```bash
# Start Ollama container in detached mode
docker run -d -p 11434:11434 --name ollama-deepseek ollama/ollama

# Attach to container and pull the model (only needed once)
docker exec -it ollama-deepseek ollama pull deepseek-r1

# Verify it's running → should respond
curl http://localhost:11434

````


Keep the container running in the background.

## Installation

````bash
git clone https://github.com/YOUR_USERNAME/MCP_Financial_Analyst.git
cd MCP_Financial_Analyst

# Preferred: fast & clean installs with uv
uv pip install -r requirements.txt

# Classic alternative
# pip install -r requirements.txt
````

## Running the MCP Server
````bash
# Cleanest way (recommended)
uv run server.py

# Or with explicit path (useful when configuring MCP clients)
uv --directory /full/path/to/MCP_Financial_Analyst run server.py
````

Once started, the server listens for connections from MCP-compatible clients (Cursor, Claude Desktop with MCP support, custom clients, etc.).

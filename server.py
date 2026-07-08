import json

from mcp.server.fastmcp import FastMCP

from finance_tool import build_analysis_plan, run_financial_analysis

# create FastMCP instance
mcp = FastMCP("financial-analyst")


@mcp.tool()
def analyze_stock(query: str) -> str:
    """
    Run the financial-analysis workflow for a natural-language investment query.

    The workflow follows a simple plan -> retrieve -> analyze -> verify sequence and returns
    a structured JSON report.
    """
    try:
        return run_financial_analysis(query)
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return f"Error: {exc}"


@mcp.tool()
def plan_analysis(query: str) -> str:
    """Return the execution plan for a query before analysis runs."""

    try:
        plan = build_analysis_plan(query, {})
        return json.dumps(
            {
                "symbols": plan.symbols,
                "timeframe": plan.timeframe,
                "intent": plan.intent,
                "steps": plan.steps,
            },
            indent=2,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return f"Error: {exc}"


@mcp.tool()
def save_code(code: str) -> str:
    """
    Legacy compatibility helper for saving a generated Python script.
    """
    try:
        with open("stock_analysis.py", "w", encoding="utf-8") as handle:
            handle.write(code)
        return "Code saved to stock_analysis.py"
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return f"Error: {exc}"


@mcp.tool()
def run_code_and_show_plot() -> str:
    """
    Legacy compatibility helper for executing a saved Python script.
    """
    try:
        import subprocess

        result = subprocess.run(
            ["python", "stock_analysis.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return f"Error executing code: {result.stderr}"
        return "Code executed successfully and plot generated. Check the current directory for the plot image."
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return f"Error: {exc}"


# Run the server locally
if __name__ == "__main__":
    mcp.run(transport="stdio")
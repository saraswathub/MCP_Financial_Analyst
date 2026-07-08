import json
import logging
import threading
import time
from typing import Dict

from mcp.server.fastmcp import FastMCP

from finance_tool import build_analysis_plan, run_financial_analysis, get_metrics

try:
    from prometheus_client import start_http_server, Gauge
except Exception:  # pragma: no cover - optional dependency
    start_http_server = None  # type: ignore
    Gauge = None  # type: ignore

# create FastMCP instance
mcp = FastMCP("financial-analyst")

# basic logging configuration; callers can configure logging more precisely
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("mcp_server")

# Prometheus metric port (changeable as needed)
METRICS_PORT = 8000
_PROM_GAUGES: Dict[str, "Gauge"] = {}


def _init_prom_gauges():
    """Create Gauge objects for known counters."""
    if Gauge is None:
        logger.debug("prometheus_client not available; skipping gauge init")
        return
    # Known metric names from finance_tool.METRICS
    keys = ["requests", "successes", "failures", "plans", "data_fetches", "analyses"]
    for key in keys:
        _PROM_GAUGES[key] = Gauge(f"mcp_financial_{key}", f"Count of {key} operations")


def _prometheus_updater(interval: float = 5.0):
    """Background thread to copy in-process counters into Prometheus gauges."""
    if start_http_server is None:
        logger.debug("prometheus_client not installed; updater will not run")
        return
    _init_prom_gauges()
    # start HTTP server
    try:
        start_http_server(METRICS_PORT)
        logger.info("Prometheus metrics server started on port %s", METRICS_PORT)
    except Exception as exc:
        logger.exception("Failed to start Prometheus metrics server: %s", exc)
        return

    while True:
        try:
            counters = get_metrics()
            for k, v in counters.items():
                gauge = _PROM_GAUGES.get(k)
                if gauge is not None:
                    gauge.set(v)
        except Exception:
            logger.exception("Error updating Prometheus gauges")
        time.sleep(interval)


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
def metrics() -> str:
    """Return simple runtime metrics collected by the analysis module."""
    try:
        return json.dumps(get_metrics(), indent=2)
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        logger.exception("Error returning metrics: %s", exc)
        return f"Error: {exc}"


def start_metrics_background_thread():
    """If Prometheus is available, start a background thread to serve metrics."""
    if start_http_server is None:
        logger.info("prometheus_client not installed; metrics endpoint disabled")
        return
    t = threading.Thread(target=_prometheus_updater, daemon=True)
    t.start()
    logger.info("Started Prometheus updater thread")


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
    # start optional metrics thread (non-blocking)
    start_metrics_background_thread()
    mcp.run(transport="stdio")
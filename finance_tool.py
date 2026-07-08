import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - handled gracefully at runtime
    yf = None


@dataclass
class AnalysisPlan:
    """Structured plan for the financial analysis workflow."""

    symbols: List[str]
    timeframe: str
    intent: str
    steps: List[str] = field(default_factory=list)


class SessionContext:
    """Lightweight in-memory context store for follow-up requests."""

    def __init__(self) -> None:
        self.entries: Dict[str, Any] = {}

    def remember(self, key: str, value: Any) -> None:
        self.entries[key] = value

    def get_context(self) -> Dict[str, Any]:
        return dict(self.entries)


memory = SessionContext()


def extract_symbols(query: str) -> List[str]:
    """Extract likely ticker symbols from a natural language query."""

    aliases = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "tesla": "TSLA",
        "amazon": "AMZN",
        "google": "GOOGL",
        "meta": "META",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "s&p": "SPY",
        "spy": "SPY",
    }

    lowered = query.lower()
    for phrase, symbol in aliases.items():
        if phrase in lowered:
            return [symbol]

    matches = re.findall(r"\b[A-Z]{1,5}\b", query)
    if matches:
        return [symbol for symbol in matches if symbol not in {"MCP", "AI", "YTD"}]
    return ["SPY"]


def normalize_timeframe(query: str) -> str:
    """Map natural language hints to a timeframe supported by yfinance."""

    lowered = query.lower()
    if any(token in lowered for token in ["1d", "day", "today"]):
        return "1d"
    if any(token in lowered for token in ["1mo", "month", "monthly"]):
        return "1mo"
    if any(token in lowered for token in ["6mo", "half year", "half-year"]):
        return "6mo"
    if any(token in lowered for token in ["1y", "year", "yearly", "ytd"]):
        return "1y"
    if any(token in lowered for token in ["5y", "5 year", "5-year"]):
        return "5y"
    return "2y"


def build_analysis_plan(query: str, memory_context: Dict[str, Any]) -> AnalysisPlan:
    """Create a practical execution plan for the analysis workflow."""

    lowered = query.lower()
    symbols = extract_symbols(query)
    timeframe = normalize_timeframe(query)
    intent = "analyze"
    if any(token in lowered for token in ["compare", "vs", "versus"]):
        intent = "compare"
    elif any(token in lowered for token in ["plot", "chart", "graph"]):
        intent = "visualize"
    elif any(token in lowered for token in ["volatility", "risk", "variance"]):
        intent = "risk"

    steps = [
        "Plan the request into a short market-analysis workflow",
        "Fetch and organize market data from yfinance",
        "Calculate the main trend and risk measures",
        "Review the result for consistency and clarity",
    ]
    if intent == "compare":
        steps.append("Compare the selected symbols side by side")
    if intent == "visualize":
        steps.append("Prepare a chart-friendly summary for the selected period")
    if intent == "risk":
        steps.append("Highlight volatility and downside risk")

    if memory_context:
        steps.append("Use the stored context to tailor the response")

    return AnalysisPlan(symbols=symbols, timeframe=timeframe, intent=intent, steps=steps)


def fetch_market_data(symbols: List[str], timeframe: str) -> Dict[str, Any]:
    """Retrieve historical data for the selected symbols."""

    if yf is None:
        return {symbol: {"error": "yfinance is not installed"} for symbol in symbols}

    period_map = {"1d": "1d", "1mo": "1mo", "6mo": "6mo", "1y": "1y", "2y": "2y", "5y": "5y"}
    period = period_map.get(timeframe, "2y")
    frames: Dict[str, Any] = {}
    for symbol in symbols:
        try:
            frame = yf.download(symbol, period=period, progress=False, auto_adjust=True)
            frames[symbol] = frame if not frame.empty else {"error": "No data returned"}
        except Exception as exc:  # pragma: no cover - depends on network availability
            frames[symbol] = {"error": str(exc)}
    return frames


def analyze_market_data(symbols: List[str], timeframe: str, intent: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a structured analysis summary with basic trend and risk metrics."""

    metrics: List[Dict[str, Any]] = []
    for symbol in symbols:
        payload = market_data.get(symbol, {})
        if isinstance(payload, dict) and "error" in payload:
            metrics.append({"symbol": symbol, "status": "error", "detail": payload["error"]})
            continue

        if payload.empty:
            metrics.append({"symbol": symbol, "status": "error", "detail": "No data returned"})
            continue

        close = payload["Close"]
        first_close = float(close.iloc[0])
        last_close = float(close.iloc[-1])
        change_pct = ((last_close / first_close) - 1) * 100 if first_close else 0.0
        daily_returns = close.pct_change().dropna()
        volatility_pct = float(daily_returns.std() * 100) if not daily_returns.empty else 0.0
        metrics.append(
            {
                "symbol": symbol,
                "status": "ok",
                "start_price": round(first_close, 2),
                "end_price": round(last_close, 2),
                "change_pct": round(change_pct, 2),
                "volatility_pct": round(volatility_pct, 2),
            }
        )

    summary_lines = [
        f"Market analysis for {', '.join(symbols)} over {timeframe}",
        f"Intent: {intent}",
    ]
    if intent == "compare":
        summary_lines.append("Comparison mode: highlight relative movement between the selected symbols")
    if intent == "risk":
        summary_lines.append("Risk mode: volatility and stability are emphasized")

    for metric in metrics:
        if metric["status"] == "ok":
            summary_lines.append(
                f"{metric['symbol']}: price moved {metric['change_pct']}% with volatility {metric['volatility_pct']}%"
            )
        else:
            summary_lines.append(f"{metric['symbol']}: data issue -> {metric['detail']}")

    return {"metrics": metrics, "summary": "\n".join(summary_lines)}


def verify_analysis(summary: str, metrics: List[Dict[str, Any]]) -> str:
    """Perform a lightweight validation pass over the analysis."""

    if not metrics:
        return "Verification: no metrics were produced"
    if all(item.get("status") == "error" for item in metrics):
        return "Verification: market data could not be retrieved, so the result is only a fallback explanation"
    if any(item.get("status") == "error" for item in metrics):
        return "Verification: the report contains partial data; some symbols need a follow-up lookup"
    return "Verification: the analysis looks consistent and is ready for the next step"


def run_financial_analysis(query: str) -> str:
    """Run the analysis workflow and return a structured JSON report."""

    memory.remember("latest_query", query)
    plan = build_analysis_plan(query, memory.get_context())
    market_data = fetch_market_data(plan.symbols, plan.timeframe)
    analysis = analyze_market_data(plan.symbols, plan.timeframe, plan.intent, market_data)
    verification = verify_analysis(analysis["summary"], analysis["metrics"])

    report = {
        "workflow": "plan -> retrieve -> analyze -> verify",
        "plan": {
            "symbols": plan.symbols,
            "timeframe": plan.timeframe,
            "intent": plan.intent,
            "steps": plan.steps,
        },
        "analysis": analysis["summary"],
        "metrics": analysis["metrics"],
        "verification": verification,
        "memory_context": memory.get_context(),
    }
    return json.dumps(report, indent=2)


__all__ = ["AgentPlan", "SessionMemory", "build_agentic_plan", "run_financial_analysis"]
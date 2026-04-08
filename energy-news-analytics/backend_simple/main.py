# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="能源化工新闻分析系统（轻量后端）", version="1.1.0")

NEWS_FEEDS: Dict[str, List[str]] = {
    "all": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.investing.com/rss/news_25.rss",
    ],
    "WTI": ["https://feeds.reuters.com/reuters/businessNews"],
    "Brent": ["https://feeds.reuters.com/reuters/businessNews"],
    "HH": ["https://feeds.reuters.com/reuters/businessNews"],
    "TTF": ["https://feeds.reuters.com/reuters/businessNews"],
    "JKM": ["https://feeds.reuters.com/reuters/businessNews"],
}

COMMODITY_KEYWORDS: Dict[str, List[str]] = {
    "WTI": ["wti", "crude", "oil", "west texas"],
    "Brent": ["brent", "crude", "oil", "north sea"],
    "HH": ["henry hub", "natural gas", "lng", "us gas"],
    "TTF": ["ttf", "europe gas", "natural gas", "lng"],
    "JKM": ["jkm", "lng", "asia gas", "spot lng"],
    "PG": ["lpg", "propane", "butane"],
    "PP": ["propylene", "petrochemical"],
    "MB": ["mont belvieu", "lpg", "propane"],
    "FEI": ["far east index", "lpg", "lng"],
    "CP": ["contract price", "saudi", "lpg"],
}

YFINANCE_SYMBOL_MAP: Dict[str, str] = {
    "WTI": "CL=F",
    "Brent": "BZ=F",
    "HH": "NG=F",
    "TTF": "TTF=F",
    "RB": "RB=F",  # Gasoline RBOB
    "HO": "HO=F",  # Heating Oil
}

BASE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "default": {"fundamental": 0.30, "macro": 0.15, "sentiment": 0.20, "technical": 0.20, "geopolitical": 0.15},
    "WTI": {"fundamental": 0.30, "macro": 0.15, "sentiment": 0.20, "technical": 0.20, "geopolitical": 0.15},
    "Brent": {"fundamental": 0.30, "macro": 0.15, "sentiment": 0.20, "technical": 0.20, "geopolitical": 0.15},
    "HH": {"fundamental": 0.35, "macro": 0.10, "sentiment": 0.20, "technical": 0.25, "geopolitical": 0.10},
    "TTF": {"fundamental": 0.33, "macro": 0.12, "sentiment": 0.23, "technical": 0.20, "geopolitical": 0.12},
    "JKM": {"fundamental": 0.33, "macro": 0.12, "sentiment": 0.23, "technical": 0.20, "geopolitical": 0.12},
}

POSITIVE_WORDS = ["increase", "surge", "growth", "bullish", "tight", "support", "上涨", "利好", "增长"]
NEGATIVE_WORDS = ["drop", "fall", "decline", "bearish", "risk", "conflict", "sanction", "down", "下跌", "利空", "冲突", "制裁"]


class NotebookLMBriefRequest(BaseModel):
    commodity: str = Field(default="WTI", description="品种代码，例如 WTI/Brent/HH/TTF/JKM")
    use_live_news: bool = Field(default=True, description="是否自动抓取 RSS 作为 NotebookLM 上下文")
    max_items: int = Field(default=20, ge=5, le=50, description="最多输入新闻条数")
    style: str = Field(default="trader", description="输出风格: trader/research/executive")
    extra_context: Optional[str] = Field(default=None, description="手工追加的上下文")
    news_texts: Optional[List[str]] = Field(default=None, description="可选手工输入新闻文本，优先于 RSS")


@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {"status": "healthy", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/news/auto-collect")
def auto_collect_news(
    commodity: str = Query("all", description="品种代码，如 WTI/Brent/HH/TTF/JKM"),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """自动采集可爬取的新闻RSS源（轻量版本）。"""
    feeds = NEWS_FEEDS.get(commodity, NEWS_FEEDS["all"])
    keywords = COMMODITY_KEYWORDS.get(commodity, [])

    items: List[Dict[str, Any]] = []
    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            title = str(getattr(entry, "title", ""))
            summary = str(getattr(entry, "summary", ""))
            content = f"{title} {summary}".lower()

            if keywords and not any(k in content for k in keywords):
                continue

            published = getattr(entry, "published", None) or getattr(entry, "updated", None)
            items.append(
                {
                    "title": title,
                    "summary": summary[:400],
                    "url": getattr(entry, "link", ""),
                    "source": parsed.feed.get("title", feed_url),
                    "published": published,
                    "commodity": commodity,
                }
            )

    dedup = {(item["title"], item["url"]): item for item in items}
    result = list(dedup.values())[:limit]
    return {
        "commodity": commodity,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(result),
        "feeds": feeds,
        "items": result,
    }


@app.get("/api/v1/quant/yfinance/{symbol}/volatility")
def yfinance_volatility(
    symbol: str,
    period: str = Query("1y", description="yfinance周期，如 6mo/1y/2y"),
    interval: str = Query("1d", description="yfinance间隔，如 1d/1h"),
    window: int = Query(20, ge=5, le=120, description="滚动波动率窗口"),
) -> Dict[str, Any]:
    """基于 yfinance 的历史数据波动率量化分析。"""
    ticker = YFINANCE_SYMBOL_MAP.get(symbol, symbol)

    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if df.empty or "Close" not in df.columns:
        raise HTTPException(status_code=404, detail=f"未获取到 {ticker} 的历史数据")

    close = df["Close"].dropna()
    returns = np.log(close / close.shift(1)).dropna()
    if len(returns) < window + 2:
        raise HTTPException(status_code=400, detail="样本不足，无法计算滚动波动率，请增大 period")

    annual_factor = 252 if interval.endswith("d") else 24 * 365
    rolling_vol = returns.rolling(window).std() * np.sqrt(annual_factor)
    rolling_vol = rolling_vol.dropna()

    hist_vol_20d = float((returns.tail(20).std() * np.sqrt(annual_factor)) * 100)
    hist_vol_60d = float((returns.tail(60).std() * np.sqrt(annual_factor)) * 100) if len(returns) >= 60 else None
    latest_vol = float(rolling_vol.iloc[-1] * 100)

    price_change_1d = float((close.iloc[-1] / close.iloc[-2] - 1) * 100)
    price_change_5d = float((close.iloc[-1] / close.iloc[-6] - 1) * 100) if len(close) > 6 else None

    vol_regime = "high" if latest_vol >= np.nanpercentile(rolling_vol * 100, 75) else "normal"

    return {
        "symbol": symbol,
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "observations": int(len(df)),
        "latest_close": float(close.iloc[-1]),
        "returns": {
            "daily_pct": round(price_change_1d, 3),
            "five_day_pct": round(price_change_5d, 3) if price_change_5d is not None else None,
        },
        "volatility": {
            "rolling_window": window,
            "latest_annualized_pct": round(latest_vol, 3),
            "hist_vol_20d_pct": round(hist_vol_20d, 3),
            "hist_vol_60d_pct": round(hist_vol_60d, 3) if hist_vol_60d is not None else None,
            "vol_regime": vol_regime,
        },
    }




def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(v, 0.01) for v in weights.values())
    return {k: round(max(v, 0.01) / total, 4) for k, v in weights.items()}


def _sentiment_score_from_texts(texts: List[str]) -> float:
    if not texts:
        return 0.0
    joined = " ".join(texts).lower()
    pos = sum(joined.count(w) for w in POSITIVE_WORDS)
    neg = sum(joined.count(w) for w in NEGATIVE_WORDS)
    raw = (pos - neg) / max(pos + neg, 1)
    return float(max(-1.0, min(1.0, raw)))


def _build_notebooklm_prompt(
    commodity: str, texts: List[str], style: str, dynamic_weights: Dict[str, float], extra_context: Optional[str]
) -> str:
    context_block = "\n".join(f"- {x[:800]}" for x in texts[:30]) if texts else "- 无有效新闻文本"
    style_map = {
        "trader": "请给出偏交易执行的结论，明确方向、触发条件和风险位。",
        "research": "请给出偏研究员风格，强调因果链、假设和需要验证的数据。",
        "executive": "请给出管理层可读摘要，控制在 6 条以内并突出业务影响。",
    }
    style_instruction = style_map.get(style, style_map["trader"])
    extra = f"\n补充上下文：{extra_context}" if extra_context else ""
    return f"""
你是能源化工市场分析助手。请基于输入新闻做 NotebookLM 风格市场简报。
品种：{commodity}
风格要求：{style_instruction}
动态权重：{dynamic_weights}
请输出：
1) 三句话摘要；
2) 多空驱动拆解（基本面/宏观/情绪/技术/地缘）；
3) 未来24小时关注点（3-5条）；
4) 风险提示（2-3条，包含可能打脸场景）；
5) 给出一个 -5 到 +5 的方向分值并说明理由。
{extra}

新闻输入：
{context_block}
""".strip()


def _generate_with_notebooklm(prompt: str) -> Dict[str, Any]:
    """
    尝试调用 notebooklm-py SDK（兼容常见命名）。
    若 SDK 不存在或调用失败，回退为规则生成（便于本地联调）。
    """
    try:
        # 兼容 notebooklm-py 的不同包名/入口，避免强耦合单一实现
        try:
            import notebooklm_py as nblm  # type: ignore
        except Exception:
            import notebooklm as nblm  # type: ignore

        client_cls = getattr(nblm, "Client", None) or getattr(nblm, "NotebookLM", None)
        if client_cls is None:
            raise RuntimeError("notebooklm-py SDK 未暴露 Client/NotebookLM 类")

        client = client_cls()
        if hasattr(client, "generate"):
            output = client.generate(prompt=prompt)
        elif hasattr(client, "query"):
            output = client.query(prompt)
        elif hasattr(client, "run"):
            output = client.run(prompt)
        else:
            raise RuntimeError("notebooklm-py 客户端缺少 generate/query/run 方法")

        text = output if isinstance(output, str) else str(output)
        return {"provider": "notebooklm-py", "ok": True, "content": text}
    except Exception as e:
        fallback = (
            "【Mock NotebookLM 输出】\n"
            "1) 摘要：当前新闻流显示市场在供需与地缘风险之间博弈，短线波动放大。\n"
            "2) 多空拆解：情绪与地缘偏多，宏观与技术分化。\n"
            "3) 24小时关注：库存、突发地缘消息、美元与利率预期。\n"
            "4) 风险提示：若宏观需求再度走弱，当前多头叙事可能失效。\n"
            "5) 方向分值：+1.2（轻度偏多）。"
        )
        return {"provider": "mock-fallback", "ok": False, "error": str(e), "content": fallback}


@app.get("/api/v1/ai/dynamic-weights")
def ai_dynamic_weights(
    commodity: str = Query("WTI", description="品种代码，例如 WTI/Brent/HH/TTF/JKM"),
    period: str = Query("6mo", description="用于波动率评估的历史区间"),
    window: int = Query(20, ge=5, le=120, description="滚动波动率窗口"),
    use_live_news: bool = Query(True, description="是否抓取最新RSS新闻作为情绪输入"),
) -> Dict[str, Any]:
    """AI动态权重接口（轻量版）：结合新闻情绪 + 波动率状态调整五维权重。"""
    base = BASE_WEIGHTS.get(commodity, BASE_WEIGHTS["default"]).copy()

    # 1) 采集新闻情绪
    news_items: List[Dict[str, Any]] = []
    if use_live_news:
        try:
            news_items = auto_collect_news(commodity=commodity, limit=30).get("items", [])
        except Exception:
            news_items = []

    texts = [f"{x.get('title', '')} {x.get('summary', '')}" for x in news_items]
    sentiment_score = _sentiment_score_from_texts(texts)

    # 2) 评估市场波动率状态
    vol_score = 0.0
    vol_regime = "unknown"
    try:
        vol_result = yfinance_volatility(symbol=commodity, period=period, interval="1d", window=window)
        latest_vol = vol_result["volatility"]["latest_annualized_pct"]
        hv20 = vol_result["volatility"]["hist_vol_20d_pct"]
        vol_score = float((latest_vol - hv20) / max(hv20, 1e-6))
        vol_regime = vol_result["volatility"]["vol_regime"]
    except Exception:
        latest_vol = None
        hv20 = None

    # 3) AI规则化动态调权（可替换为LLM服务）
    adjusted = base.copy()
    adjusted["sentiment"] += 0.06 * abs(sentiment_score)
    adjusted["technical"] += 0.05 * max(vol_score, 0)
    adjusted["geopolitical"] += 0.04 * max(-sentiment_score, 0)

    # 高波动时降低基本面和宏观权重，提升技术/情绪
    if vol_regime == "high":
        adjusted["fundamental"] -= 0.03
        adjusted["macro"] -= 0.02
        adjusted["technical"] += 0.03
        adjusted["sentiment"] += 0.02

    normalized = _normalize_weights(adjusted)

    return {
        "commodity": commodity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "base_weights": base,
        "dynamic_weights": normalized,
        "ai_signals": {
            "sentiment_score": round(sentiment_score, 4),
            "volatility_score": round(vol_score, 4),
            "vol_regime": vol_regime,
            "latest_volatility_pct": latest_vol,
            "hist_vol_20d_pct": hv20,
            "news_samples": len(news_items),
        },
        "rationale": [
            "情绪绝对值越高，情绪因子权重越高",
            "波动率高于历史基准时，技术因子权重上调",
            "负面情绪增强时，地缘风险权重上调",
        ],
    }


@app.post("/api/v1/ai/notebooklm/market-brief")
def notebooklm_market_brief(request: NotebookLMBriefRequest) -> Dict[str, Any]:
    """
    NotebookLM 集成接口（支持 notebooklm-py SDK + 本地回退）：
    - 若安装并配置 notebooklm-py，则返回真实 LLM 输出；
    - 否则返回可联调的 mock 结果，并附带失败原因。
    """
    commodity = request.commodity
    base_weights = BASE_WEIGHTS.get(commodity, BASE_WEIGHTS["default"])

    if request.news_texts:
        texts = request.news_texts[: request.max_items]
    elif request.use_live_news:
        items = auto_collect_news(commodity=commodity, limit=request.max_items).get("items", [])
        texts = [f"{x.get('title', '')} {x.get('summary', '')}" for x in items]
    else:
        texts = []

    dynamic = ai_dynamic_weights(commodity=commodity, use_live_news=request.use_live_news)
    prompt = _build_notebooklm_prompt(
        commodity=commodity,
        texts=texts,
        style=request.style,
        dynamic_weights=dynamic.get("dynamic_weights", base_weights),
        extra_context=request.extra_context,
    )
    result = _generate_with_notebooklm(prompt)

    return {
        "commodity": commodity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "integration": {
            "provider": result["provider"],
            "sdk_connected": result["ok"],
            "error": result.get("error"),
        },
        "input_stats": {"news_count": len(texts), "style": request.style},
        "dynamic_weights": dynamic.get("dynamic_weights", base_weights),
        "market_brief": result["content"],
        "prompt_preview": prompt[:1000],
    }

@app.get("/api/v1/visualization/dashboard")
def dashboard() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score_cards": [
            {"commodity": "WTI", "score": 72.5, "rating": "看涨", "signal": "买入"},
            {"commodity": "Brent", "score": 68.3, "rating": "看涨", "signal": "持有"},
            {"commodity": "HH", "score": 55.2, "rating": "中性", "signal": "持有"},
        ],
        "recent_alerts": [
            {"id": "1", "level": "red", "message": "WTI地缘风险上升", "commodity": "WTI"},
        ],
        "top_news": [
            {"id": "1", "title": "OPEC+延长减产协议", "source": "Reuters"},
        ],
        "market_overview": {"total_news_24h": 156, "active_alerts": 8},
    }


if __name__ == "__main__":
    import uvicorn

    print("服务启动中，访问 http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

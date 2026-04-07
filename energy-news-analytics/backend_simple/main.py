# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query

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

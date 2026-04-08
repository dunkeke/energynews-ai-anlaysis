# -*- coding: utf-8 -*-
"""Streamlit 前端（API + 独立运行双模式）。"""
from datetime import datetime, timezone
from typing import Any, Dict, List
from xml.etree import ElementTree as ET

import pandas as pd
import requests
import streamlit as st

APP_BUILD = "2026-04-08-standalone-v2"

st.set_page_config(page_title="能源化工市场智能分析", page_icon="📊", layout="wide")
st.title("📊 能源化工市场信息分析（NotebookLM + Python）")
st.caption("支持两种模式：连接 FastAPI 后端（生产）或离线直连 RSS 的独立模式（演示/应急）。")
st.caption(f"Build: `{APP_BUILD}`")


def _safe_get(base_url: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _safe_post(base_url: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def _parse_rss_with_requests(url: str) -> List[Dict[str, str]]:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    items: List[Dict[str, str]] = []
    for item in root.findall(".//item"):
        title = item.findtext("title", default="")
        link = item.findtext("link", default="")
        pub = item.findtext("pubDate", default="")
        desc = item.findtext("description", default="")
        items.append({"title": title, "url": link, "published": pub, "summary": desc})
    return items


def _standalone_news(commodity: str, limit: int) -> Dict[str, Any]:
    feed_map = {
        "default": ["https://feeds.reuters.com/reuters/businessNews"],
        "WTI": ["https://feeds.reuters.com/reuters/businessNews"],
        "Brent": ["https://feeds.reuters.com/reuters/businessNews"],
        "HH": ["https://feeds.reuters.com/reuters/businessNews"],
    }
    keywords = {
        "WTI": ["wti", "oil", "crude"],
        "Brent": ["brent", "oil", "crude"],
        "HH": ["henry hub", "natural gas", "lng"],
        "TTF": ["ttf", "natural gas", "lng"],
        "JKM": ["jkm", "lng"],
    }
    feeds = feed_map.get(commodity, feed_map["default"])
    filters = keywords.get(commodity, [])
    items: List[Dict[str, str]] = []
    for feed in feeds:
        try:
            for x in _parse_rss_with_requests(feed):
                text = f"{x['title']} {x['summary']}".lower()
                if filters and not any(k in text for k in filters):
                    continue
                x["source"] = "Reuters RSS"
                items.append(x)
        except Exception:
            continue
    dedup = {(x["title"], x["url"]): x for x in items}
    result = list(dedup.values())[:limit]
    return {
        "commodity": commodity,
        "count": len(result),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "feeds": feeds,
        "items": result,
    }


def _standalone_dynamic_weights(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    base = {"fundamental": 0.30, "macro": 0.15, "sentiment": 0.20, "technical": 0.20, "geopolitical": 0.15}
    text = " ".join(f"{x.get('title', '')} {x.get('summary', '')}" for x in items).lower()
    pos = sum(text.count(w) for w in ["support", "bullish", "surge", "上涨", "利好"])
    neg = sum(text.count(w) for w in ["risk", "fall", "bearish", "下跌", "冲突", "制裁"])
    sentiment = (pos - neg) / max(pos + neg, 1)
    dynamic = base.copy()
    dynamic["sentiment"] += 0.05 * abs(sentiment)
    dynamic["geopolitical"] += 0.03 * max(-sentiment, 0)
    total = sum(dynamic.values())
    dynamic = {k: round(v / total, 4) for k, v in dynamic.items()}
    return {"base_weights": base, "dynamic_weights": dynamic, "ai_signals": {"sentiment_score": round(sentiment, 4), "news_samples": len(items), "vol_regime": "n/a-standalone"}}


def _standalone_brief(commodity: str, style: str, weights: Dict[str, float], items: List[Dict[str, Any]], extra: str) -> str:
    head = "；".join(x.get("title", "") for x in items[:3]) or "暂无有效新闻"
    return (
        f"[Standalone Mock | {style}] {commodity} 市场简报\n"
        f"摘要：{head}\n"
        f"权重：{weights}\n"
        f"观点：当前信号偏中性至轻多，建议关注库存与地缘突发。\n"
        f"补充：{extra or '无'}"
    )


commodities: List[str] = ["WTI", "Brent", "HH", "TTF", "JKM", "PG", "PP", "MB", "FEI", "CP"]

with st.sidebar:
    st.header("参数设置")
    st.caption(f"当前版本: {APP_BUILD}")
    backend_url = st.text_input("后端地址", value="http://127.0.0.1:8000")
    run_mode = st.radio("运行模式", ["Backend API（推荐）", "Standalone（无后端）"], index=0)
    selected_commodity = st.selectbox("品种", commodities, index=0)
    news_limit = st.slider("新闻条数", min_value=5, max_value=50, value=20)
    style = st.selectbox("简报风格", ["trader", "research", "executive"], index=0)
    use_live_news = st.toggle("使用实时RSS新闻", value=True)
    extra_context = st.text_area("补充上下文", value="关注库存、地缘冲突和美元波动")

tab_health, tab_news, tab_weights, tab_brief = st.tabs(["🩺 连接检查", "📰 新闻采集", "⚖️ 动态权重", "🧠 NotebookLM简报"])

with tab_health:
    st.subheader("后端连接状态")
    if st.button("检查连通性", type="primary"):
        if run_mode.startswith("Standalone"):
            st.success("Standalone 模式无需后端，功能将使用内置降级逻辑。")
        else:
            try:
                health = _safe_get(backend_url, "/health", params={})
                st.success("后端连接正常")
                st.json(health)
            except Exception as e:
                st.error(f"无法连接后端：{e}")
                st.info("可切换到 Standalone 模式，或先启动后端：`uvicorn backend_simple.main:app --reload --host 0.0.0.0 --port 8000`")

with tab_news:
    st.subheader("自动新闻采集")
    if st.button("拉取新闻", type="primary"):
        with st.spinner("正在采集新闻..."):
            try:
                if run_mode.startswith("Standalone"):
                    news_data = _standalone_news(selected_commodity, news_limit)
                else:
                    news_data = _safe_get(
                        backend_url,
                        "/api/v1/news/auto-collect",
                        params={"commodity": selected_commodity, "limit": news_limit},
                    )
                st.success(f"采集完成：{news_data.get('count', 0)} 条")
                st.json(
                    {
                        "commodity": news_data.get("commodity"),
                        "fetched_at": news_data.get("fetched_at"),
                        "feeds": news_data.get("feeds", []),
                    }
                )
                items = news_data.get("items", [])
                if items:
                    df = pd.DataFrame(items)
                    columns = [c for c in ["title", "source", "published", "url"] if c in df.columns]
                    st.dataframe(df[columns], use_container_width=True)
                else:
                    st.info("当前没有匹配到新闻。")
            except Exception as e:
                st.error(f"新闻采集失败：{e}")

with tab_weights:
    st.subheader("AI动态权重")
    if st.button("计算动态权重"):
        with st.spinner("正在计算动态权重..."):
            try:
                if run_mode.startswith("Standalone"):
                    news_data = _standalone_news(selected_commodity, news_limit)
                    result = _standalone_dynamic_weights(news_data.get("items", []))
                else:
                    result = _safe_get(
                        backend_url,
                        "/api/v1/ai/dynamic-weights",
                        params={
                            "commodity": selected_commodity,
                            "period": "6mo",
                            "window": 20,
                            "use_live_news": use_live_news,
                        },
                    )
                signals = result.get("ai_signals", {})
                st.metric("新闻样本数", signals.get("news_samples", 0))
                st.metric("情绪分", signals.get("sentiment_score", 0))
                st.metric("波动率状态", signals.get("vol_regime", "unknown"))

                chart_df = pd.DataFrame(
                    {
                        "base": result.get("base_weights", {}),
                        "dynamic": result.get("dynamic_weights", {}),
                    }
                )
                st.bar_chart(chart_df)
                st.json(signals)
            except Exception as e:
                st.error(f"动态权重计算失败：{e}")

with tab_brief:
    st.subheader("NotebookLM市场简报")
    st.write("点击按钮生成市场简报（SDK可用时走真实输出，不可用时后端自动回退）。")
    if st.button("生成简报", type="primary"):
        with st.spinner("正在生成市场简报..."):
            try:
                if run_mode.startswith("Standalone"):
                    news_data = _standalone_news(selected_commodity, news_limit)
                    weight_data = _standalone_dynamic_weights(news_data.get("items", []))
                    result = {
                        "integration": {"provider": "standalone-mock", "sdk_connected": False},
                        "market_brief": _standalone_brief(
                            selected_commodity,
                            style,
                            weight_data.get("dynamic_weights", {}),
                            news_data.get("items", []),
                            extra_context,
                        ),
                        "prompt_preview": "Standalone 模式不调用 NotebookLM API，仅用于演示与联调。",
                    }
                else:
                    payload = {
                        "commodity": selected_commodity,
                        "use_live_news": use_live_news,
                        "max_items": news_limit,
                        "style": style,
                        "extra_context": extra_context,
                    }
                    result = _safe_post(backend_url, "/api/v1/ai/notebooklm/market-brief", payload=payload)
                st.json(result.get("integration", {}))
                st.markdown("### 市场简报结果")
                st.write(result.get("market_brief", ""))
                with st.expander("Prompt预览（前1000字符）"):
                    st.code(result.get("prompt_preview", ""))
            except Exception as e:
                st.error(f"简报生成失败：{e}")

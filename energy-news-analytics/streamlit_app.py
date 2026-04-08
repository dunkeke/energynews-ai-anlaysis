# -*- coding: utf-8 -*-
"""
Streamlit 前端（API 驱动版）
避免直接 import backend_simple.main 导致依赖缺失时启动失败。
"""
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="能源化工市场智能分析", page_icon="📊", layout="wide")
st.title("📊 能源化工市场信息分析（NotebookLM + Python）")
st.caption("Streamlit 作为展示层，通过 HTTP 调用 FastAPI 轻量后端。")


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


commodities: List[str] = ["WTI", "Brent", "HH", "TTF", "JKM", "PG", "PP", "MB", "FEI", "CP"]

with st.sidebar:
    st.header("参数设置")
    backend_url = st.text_input("后端地址", value="http://127.0.0.1:8000")
    selected_commodity = st.selectbox("品种", commodities, index=0)
    news_limit = st.slider("新闻条数", min_value=5, max_value=50, value=20)
    style = st.selectbox("简报风格", ["trader", "research", "executive"], index=0)
    use_live_news = st.toggle("使用实时RSS新闻", value=True)
    extra_context = st.text_area("补充上下文", value="关注库存、地缘冲突和美元波动")

tab_health, tab_news, tab_weights, tab_brief = st.tabs(["🩺 连接检查", "📰 新闻采集", "⚖️ 动态权重", "🧠 NotebookLM简报"])

with tab_health:
    st.subheader("后端连接状态")
    if st.button("检查连通性", type="primary"):
        try:
            health = _safe_get(backend_url, "/health", params={})
            st.success("后端连接正常")
            st.json(health)
        except Exception as e:
            st.error(f"无法连接后端：{e}")
            st.info("请先启动轻量后端：`uvicorn backend_simple.main:app --reload --host 0.0.0.0 --port 8000`")

with tab_news:
    st.subheader("自动新闻采集")
    if st.button("拉取新闻", type="primary"):
        with st.spinner("正在采集新闻..."):
            try:
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

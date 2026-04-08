# -*- coding: utf-8 -*-
"""
Streamlit 前端：
将轻量后端核心能力（新闻采集 / 动态权重 / NotebookLM 市场简报）直接 Python 化展示。
"""
from typing import List

import pandas as pd
import streamlit as st

from backend_simple.main import (
    NotebookLMBriefRequest,
    ai_dynamic_weights,
    auto_collect_news,
    notebooklm_market_brief,
)

st.set_page_config(page_title="能源化工市场智能分析", page_icon="📊", layout="wide")
st.title("📊 能源化工市场信息分析（NotebookLM + Python）")
st.caption("基于 Python + Streamlit 的一体化展示层，支持新闻采集、动态权重和 NotebookLM 市场简报。")

commodities: List[str] = ["WTI", "Brent", "HH", "TTF", "JKM", "PG", "PP", "MB", "FEI", "CP"]

with st.sidebar:
    st.header("参数设置")
    selected_commodity = st.selectbox("品种", commodities, index=0)
    news_limit = st.slider("新闻条数", min_value=5, max_value=50, value=20)
    style = st.selectbox("简报风格", ["trader", "research", "executive"], index=0)
    use_live_news = st.toggle("使用实时RSS新闻", value=True)
    extra_context = st.text_area("补充上下文", value="关注库存、地缘冲突和美元波动")

tab_news, tab_weights, tab_brief = st.tabs(["📰 新闻采集", "⚖️ 动态权重", "🧠 NotebookLM简报"])

with tab_news:
    st.subheader("自动新闻采集")
    if st.button("拉取新闻", type="primary"):
        with st.spinner("正在采集新闻..."):
            try:
                news_data = auto_collect_news(commodity=selected_commodity, limit=news_limit)
                st.success(f"采集完成：{news_data['count']} 条")
                st.json(
                    {
                        "commodity": news_data["commodity"],
                        "fetched_at": news_data["fetched_at"],
                        "feeds": news_data["feeds"],
                    }
                )
                items = news_data.get("items", [])
                if items:
                    df = pd.DataFrame(items)
                    st.dataframe(df[["title", "source", "published", "url"]], use_container_width=True)
                else:
                    st.info("当前没有匹配到新闻。")
            except Exception as e:
                st.error(f"新闻采集失败：{e}")

with tab_weights:
    st.subheader("AI动态权重")
    if st.button("计算动态权重"):
        with st.spinner("正在计算动态权重..."):
            try:
                result = ai_dynamic_weights(
                    commodity=selected_commodity,
                    period="6mo",
                    window=20,
                    use_live_news=use_live_news,
                )
                st.metric("新闻样本数", result["ai_signals"]["news_samples"])
                st.metric("情绪分", result["ai_signals"]["sentiment_score"])
                st.metric("波动率状态", result["ai_signals"]["vol_regime"])

                chart_df = pd.DataFrame(
                    {
                        "base": result["base_weights"],
                        "dynamic": result["dynamic_weights"],
                    }
                )
                st.bar_chart(chart_df)
                st.json(result["ai_signals"])
            except Exception as e:
                st.error(f"动态权重计算失败：{e}")

with tab_brief:
    st.subheader("NotebookLM市场简报")
    st.write("点击按钮生成市场简报（支持 notebooklm-py，未配置时自动回退 mock 结果）。")
    if st.button("生成简报", type="primary"):
        with st.spinner("正在生成市场简报..."):
            try:
                request = NotebookLMBriefRequest(
                    commodity=selected_commodity,
                    use_live_news=use_live_news,
                    max_items=news_limit,
                    style=style,
                    extra_context=extra_context,
                )
                result = notebooklm_market_brief(request)
                st.json(result["integration"])
                st.markdown("### 市场简报结果")
                st.write(result["market_brief"])
                with st.expander("Prompt预览（前1000字符）"):
                    st.code(result["prompt_preview"])
            except Exception as e:
                st.error(f"简报生成失败：{e}")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import re
import json

st.set_page_config(page_title="基金分析平台", layout="wide")

st.title("🚀 智能基金分析平台（真实数据版）")

# =========================
# 获取真实基金数据（核心）
# =========================
def get_fund_data(code):
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    try:
        res = requests.get(url, timeout=10)
        text = res.text

        # 基金名称
        name = re.search(r'fS_name = "(.*?)";', text)
        name = name.group(1) if name else code

        # 净值
        data = re.search(r"Data_netWorthTrend = (.*?);", text)
        if not data:
            return None, None

        net = json.loads(data.group(1))
        df = pd.DataFrame(net)
        df["date"] = pd.to_datetime(df["x"], unit="ms")
        df["value"] = df["y"]

        return df, name

    except:
        return None, None

# =========================
# 基金列表（你可以扩展）
# =========================
codes = ["000001", "110011", "161725", "260108", "163406"]

results = []

st.header("🏆 今日基金排行榜")

with st.spinner("获取真实数据中..."):

    for code in codes:
        df, name = get_fund_data(code)

        if df is None or df.empty:
            continue

        df = df.sort_values("date")

        returns = df["value"].pct_change().dropna()

        total_return = (df["value"].iloc[-1] / df["value"].iloc[0] - 1) * 100
        volatility = returns.std() * 100
        max_drawdown = ((df["value"].cummax() - df["value"]) / df["value"].cummax()).max() * 100

        score = total_return - max_drawdown - volatility

        results.append({
            "代码": code,
            "名称": name,
            "评分": round(score, 2),
            "收益": round(total_return, 2),
            "回撤": round(max_drawdown, 2),
            "波动": round(volatility, 2)
        })

# =========================
# 排行榜
# =========================
if len(results) > 0:
    rank_df = pd.DataFrame(results).sort_values("评分", ascending=False)

    st.dataframe(rank_df, use_container_width=True)

    # =========================
    # 推荐卡片
    # =========================
    st.header("🔥 智能推荐基金")

    top3 = rank_df.head(3)
    cols = st.columns(3)

    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.metric(row["名称"], f"{row['评分']} 分")
            st.write(f"收益：{row['收益']}%")
            st.write(f"回撤：{row['回撤']}%")

else:
    st.error("暂无数据")

# =========================
# 单基金分析
# =========================
st.header("🔍 单基金分析")

code = st.text_input("输入基金代码", "000001")

df, name = get_fund_data(code)

if df is not None and not df.empty:

    df = df.sort_values("date")

    returns = df["value"].pct_change().dropna()

    total_return = (df["value"].iloc[-1] / df["value"].iloc[0] - 1) * 100
    volatility = returns.std() * 100
    max_drawdown = ((df["value"].cummax() - df["value"]) / df["value"].cummax()).max() * 100

    score = total_return - max_drawdown - volatility

    st.subheader(f"{name} ({code})")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("收益率", f"{total_return:.2f}%")
    col2.metric("回撤", f"{max_drawdown:.2f}%")
    col3.metric("波动", f"{volatility:.2f}%")
    col4.metric("评分", f"{score:.2f}")

    fig, ax = plt.subplots()
    ax.plot(df["date"], df["value"])
    ax.set_title("净值走势")
    st.pyplot(fig)

else:
    st.warning("基金数据获取失败")

# =========================
# 多基金对比
# =========================
st.header("📊 多基金对比")

codes_input = st.text_input("输入基金（逗号分隔）", "000001,110011")

if st.button("开始对比"):

    codes_list = codes_input.split(",")
    fig, ax = plt.subplots()

    for c in codes_list:
        df, _ = get_fund_data(c.strip())
        if df is not None:
            df = df.sort_values("date")
            ax.plot(df["date"], df["value"], label=c)

    ax.legend()
    st.pyplot(fig)

st.markdown("---")
st.caption("数据来源：东方财富（实时）")

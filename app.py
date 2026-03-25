import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🚀 智能基金分析平台（真实数据版）")

# =========================
# 输入基金代码
# =========================
code = st.text_input("输入基金代码", "000001")

# =========================
# 获取数据（东方财富API）
# =========================
def get_fund_data(code):
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    try:
        res = requests.get(url)
        text = res.text

        import re

        # 提取净值
        data = re.search(r"Data_netWorthTrend = (.*?);", text)
        if not data:
            return None

        import json
        net = json.loads(data.group(1))

        df = pd.DataFrame(net)
        df["date"] = pd.to_datetime(df["x"], unit="ms")
        df["value"] = df["y"]

        return df

    except:
        return None

df = get_fund_data(code)

# =========================
# 分析
# =========================
if df is not None and not df.empty:

    df = df.sort_values("date")

    returns = df["value"].pct_change().dropna()

    total_return = (df["value"].iloc[-1] / df["value"].iloc[0] - 1) * 100
    volatility = returns.std() * 100
    max_drawdown = ((df["value"].cummax() - df["value"]) / df["value"].cummax()).max() * 100

    score = total_return - max_drawdown - volatility

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("收益率", f"{total_return:.2f}%")
    col2.metric("最大回撤", f"{max_drawdown:.2f}%")
    col3.metric("波动率", f"{volatility:.2f}%")
    col4.metric("评分", f"{score:.2f}")

    # =========================
    # 曲线
    # =========================
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["value"])
    ax.set_title(f"{code} 净值走势")
    st.pyplot(fig)

else:
    st.error("基金数据获取失败，请检查代码")

# =========================
# 多基金对比
# =========================
st.header("📊 多基金对比")

codes = st.text_input("输入多个基金（逗号分隔）", "000001,110011")

if st.button("开始对比"):
    codes_list = codes.split(",")

    fig, ax = plt.subplots()

    for c in codes_list:
        df = get_fund_data(c.strip())
        if df is not None:
            df = df.sort_values("date")
            ax.plot(df["date"], df["value"], label=c)

    ax.legend()
    st.pyplot(fig)

import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="基金分析平台", layout="wide")

# =========================
# 标题
# =========================
st.title("🚀 基金超级分析平台（商业版）")

# =========================
# 今日排行榜
# =========================
st.header("🏆 今日基金排行榜")

codes = ["000001", "110011", "161725", "260108", "163406"]

results = []

with st.spinner("正在获取基金数据..."):
    for code in codes:
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

            if df.empty:
                continue

            df = df.sort_values("净值日期")

            returns = df["单位净值"].pct_change().dropna()

            total_return = (df["单位净值"].iloc[-1] / df["单位净值"].iloc[0] - 1) * 100
            volatility = returns.std() * 100
            max_drawdown = ((df["单位净值"].cummax() - df["单位净值"]) / df["单位净值"].cummax()).max() * 100

            score = total_return - max_drawdown - volatility

            results.append({
                "代码": code,
                "名称": df.iloc[0]["基金简称"],
                "评分": round(score, 2),
                "收益": round(total_return, 2),
                "回撤": round(max_drawdown, 2),
                "波动": round(volatility, 2)
            })

        except:
            st.warning(f"{code} 获取失败")

# 显示排行榜
if len(results) > 0:
    rank_df = pd.DataFrame(results).sort_values("评分", ascending=False)

    st.dataframe(rank_df, use_container_width=True)
else:
    st.error("暂无数据")

# =========================
# 智能推荐（Top3）
# =========================
st.header("🔥 智能推荐基金")

if len(results) > 0:
    top3 = rank_df.head(3)

    cols = st.columns(3)

    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.metric(row["名称"], f"{row['评分']} 分")
            st.write(f"收益：{row['收益']}%")
            st.write(f"回撤：{row['回撤']}%")

# =========================
# 手动分析
# =========================
st.header("🔍 基金分析")

user_input = st.text_input("输入基金代码（多个用逗号分隔）", "000001,110011")

if st.button("开始分析"):
    codes = [c.strip() for c in user_input.split(",")]

    fig, ax = plt.subplots()

    for code in codes:
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

            if df.empty:
                continue

            df = df.sort_values("净值日期")

            ax.plot(df["净值日期"], df["单位净值"], label=code)

        except:
            st.warning(f"{code} 获取失败")

    ax.legend()
    ax.set_title("基金净值对比")
    st.pyplot(fig)

# =========================
# 底部说明
# =========================
st.markdown("---")
st.caption("数据来源：东方财富 / akshare")

import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np

st.set_page_config(page_title="基金超级分析平台", layout="wide")

st.title("🚀 基金超级分析平台（顶级版）")

# =====================
# 工具函数
# =====================

def get_nav(code):
    try:
        df = ak.fund_open_fund_info_em(symbol=code)
        df = df.sort_values("净值日期")
        return df
    except:
        return None


def analyze(nav_df):
    nav = nav_df["单位净值"].astype(float)

    ret = (nav.iloc[-1] / nav.iloc[0] - 1) * 100
    dd = ((nav / nav.cummax()) - 1).min() * 100
    vol = nav.pct_change().std() * 100

    # 夏普近似
    sharpe = nav.pct_change().mean() / (nav.pct_change().std() + 1e-6) * np.sqrt(252)

    score = 0

    score += min(ret, 100) * 0.4
    score += (100 + dd) * 0.3
    score += max(0, 5 - vol) * 10
    score += max(0, sharpe) * 10

    score = max(0, min(100, score))

    return {
        "收益": ret,
        "回撤": dd,
        "波动": vol,
        "夏普": sharpe,
        "评分": score
    }


# =====================
# 首页推荐逻辑（自动）
# =====================

st.header("🔥 智能推荐基金")

candidate_codes = ["000001", "110011", "161725", "005827", "000832"]

results = []

for code in candidate_codes:
    nav = get_nav(code)
    if nav is None or nav.empty:
        continue

    metrics = analyze(nav)

    results.append({
        "代码": code,
        "名称": nav.iloc[-1].get("基金简称", code),
        **metrics,
        "数据": nav
    })

if results:
    rank_df = pd.DataFrame(results).sort_values("评分", ascending=False)

    top3 = rank_df.head(3)

    cols = st.columns(3)

    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.subheader(row["名称"])
            st.caption(row["代码"])
            st.metric("评分", f"{row['评分']:.1f}")

            if st.button(f"查看 {row['代码']}"):
                st.session_state["code"] = row["代码"]

st.markdown("---")

# =====================
# 搜索 + 对比
# =====================

st.header("🔍 多基金分析")

input_codes = st.text_input("输入基金（逗号分隔）", st.session_state.get("code", "000001"))
codes = [c.strip() for c in input_codes.split(",") if c.strip()]

if st.button("🚀 开始分析"):

    analysis_list = []

    for code in codes:
        nav = get_nav(code)
        if nav is None or nav.empty:
            st.warning(f"{code} 无数据")
            continue

        metrics = analyze(nav)

        analysis_list.append({
            "代码": code,
            "名称": nav.iloc[-1].get("基金简称", code),
            **metrics,
            "数据": nav
        })

    if not analysis_list:
        st.stop()

    df = pd.DataFrame(analysis_list).sort_values("评分", ascending=False)

    st.subheader("🏆 智能排名")
    st.dataframe(df[["代码", "名称", "评分", "收益", "回撤", "波动", "夏普"]])

    st.markdown("---")

    # =====================
    # 对比曲线（顶级功能🔥）
    # =====================

    st.subheader("📈 多基金净值对比")

    chart_df = pd.DataFrame()

    for item in analysis_list:
        nav = item["数据"]
        series = nav.set_index("净值日期")["单位净值"]
        series = series / series.iloc[0]  # 标准化
        chart_df[item["名称"]] = series

    st.line_chart(chart_df)

    st.markdown("---")

    # =====================
    # 单基金深度分析
    # =====================

    selected = st.selectbox("选择基金", df["代码"])

    fund = next(x for x in analysis_list if x["代码"] == selected)

    st.header(f"📊 {fund['名称']} 深度分析")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("评分", f"{fund['评分']:.1f}")
    col2.metric("收益", f"{fund['收益']:.2f}%")
    col3.metric("回撤", f"{fund['回撤']:.2f}%")
    col4.metric("波动", f"{fund['波动']:.2f}%")
    col5.metric("夏普", f"{fund['夏普']:.2f}")

    # 智能结论（核心商业逻辑🔥）
    if fund["评分"] > 80:
        st.success("🟢 顶级基金（强烈推荐）")
    elif fund["评分"] > 65:
        st.warning("🟡 优质基金（建议关注）")
    else:
        st.error("🔴 风险偏高（谨慎）")

    st.subheader("📈 净值走势")
    single_chart = fund["数据"].set_index("净值日期")["单位净值"]
    st.line_chart(single_chart)

st.caption("🚀 顶级Demo：评分系统 + 多基金对比 + 推荐系统 + 决策辅助")
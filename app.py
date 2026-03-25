import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="基金分析平台", layout="wide")

# =========================
# 标题
# =========================
st.title("🚀 智能基金分析平台（顶级版）")

# =========================
# 模拟数据（稳定展示）
# =========================
data = [
    {"代码": "000001", "名称": "华夏成长", "收益": 12.5, "回撤": 5.2, "波动": 3.1},
    {"代码": "110011", "名称": "易方达中小盘", "收益": 15.3, "回撤": 6.1, "波动": 3.5},
    {"代码": "161725", "名称": "招商白酒", "收益": 18.2, "回撤": 8.4, "波动": 4.2},
    {"代码": "260108", "名称": "景顺成长", "收益": 10.8, "回撤": 4.3, "波动": 2.9},
    {"代码": "163406", "名称": "兴全合润", "收益": 14.1, "回撤": 5.8, "波动": 3.3},
]

df = pd.DataFrame(data)

# =========================
# 评分模型
# =========================
df["评分"] = df["收益"] - df["回撤"] - df["波动"]

# =========================
# 排行榜
# =========================
st.header("🏆 综合评分排行榜")
rank_df = df.sort_values("评分", ascending=False)
st.dataframe(rank_df, use_container_width=True)

# =========================
# 收益榜
# =========================
st.header("📈 收益排行榜")
st.dataframe(df.sort_values("收益", ascending=False), use_container_width=True)

# =========================
# 稳健榜
# =========================
st.header("🛡 稳健排行榜（低回撤）")
st.dataframe(df.sort_values("回撤"), use_container_width=True)

# =========================
# 推荐卡片
# =========================
st.header("🔥 智能推荐")

top3 = rank_df.head(3)
cols = st.columns(3)

for i, (_, row) in enumerate(top3.iterrows()):
    with cols[i]:
        st.metric(row["名称"], f"{row['评分']} 分")
        st.write(f"收益：{row['收益']}%")
        st.write(f"回撤：{row['回撤']}%")

# =========================
# 基金分析
# =========================
st.header("🔍 单基金分析")

code = st.selectbox("选择基金", df["代码"])

selected = df[df["代码"] == code].iloc[0]

st.write(f"📊 名称：{selected['名称']}")
st.write(f"收益：{selected['收益']}%")
st.write(f"回撤：{selected['回撤']}%")
st.write(f"波动：{selected['波动']}%")
st.write(f"评分：{selected['评分']}")

# =========================
# 曲线模拟
# =========================
st.header("📉 净值走势")

x = np.arange(100)
y = np.cumprod(1 + np.random.normal(0.001, 0.02, 100))

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("基金走势模拟")
st.pyplot(fig)

# =========================
# 多基金对比
# =========================
st.header("📊 多基金对比")

codes = st.multiselect("选择基金对比", df["代码"], default=df["代码"][:2])

fig, ax = plt.subplots()

for code in codes:
    y = np.cumprod(1 + np.random.normal(0.001, 0.02, 100))
    ax.plot(y, label=code)

ax.legend()
st.pyplot(fig)

# =========================
# 底部
# =========================
st.markdown("---")
st.caption("基金分析平台 Demo（可扩展为商业系统）")

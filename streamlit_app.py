import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("📈 供需曲線互動模型")
st.markdown("調整下方參數，觀察均衡價格與數量的變化。")

# 側邊欄：參數控制
st.sidebar.header("參數設定")
a = st.sidebar.slider("需求截距 (a)", min_value=50, max_value=200, value=100, step=10)
b = st.sidebar.slider("需求斜率 (-b)", min_value=1, max_value=20, value=5, step=1)
c = st.sidebar.slider("供給截距 (c)", min_value=0, max_value=50, value=10, step=5)
d = st.sidebar.slider("供給斜率 (d)", min_value=1, max_value=20, value=3, step=1)

# 計算均衡
# 需求: P = a - b*Q
# 供給: P = c + d*Q
# 均衡時 a - b*Q = c + d*Q → Q* = (a - c) / (b + d)
if b + d != 0:
    Q_star = (a - c) / (b + d)
else:
    Q_star = 0
P_star = a - b * Q_star

# 繪圖
fig, ax = plt.subplots(figsize=(8, 5))
Q = np.linspace(0, 50, 500)
demand = a - b * Q
supply = c + d * Q

ax.plot(Q, demand, label="需求曲線", color="blue")
ax.plot(Q, supply, label="供給曲線", color="red")
ax.axvline(x=Q_star, color="gray", linestyle="--", alpha=0.5)
ax.axhline(y=P_star, color="gray", linestyle="--", alpha=0.5)
ax.plot(Q_star, P_star, "ko", markersize=8)
ax.set_xlim(0, 50)
ax.set_ylim(0, 200)
ax.set_xlabel("數量 Q")
ax.set_ylabel("價格 P")
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# 顯示均衡結果
col1, col2 = st.columns(2)
col1.metric("均衡價格", f"{P_star:.2f}")
col2.metric("均衡數量", f"{Q_star:.2f}")

# 消費者剩餘、生產者剩餘（簡化計算）
consumer_surplus = 0.5 * (a - P_star) * Q_star
producer_surplus = 0.5 * (P_star - c) * Q_star
col3, col4 = st.columns(2)
col3.metric("消費者剩餘", f"{consumer_surplus:.2f}")
col4.metric("生產者剩餘", f"{producer_surplus:.2f}")

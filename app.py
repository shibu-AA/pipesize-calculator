import streamlit as st
from calc.calculator import select_pipe

input_data = {
    "gas": None,
    "flow_rate": None,
    "inlet_pressure": None,
    "outlet_pressure": None,
    "temperature": None,
    "velocity_limit": None,
    "schedule": None,
    "pipe_length": None,
}

fitting_names = [
    "90°エルボ(2･1/2まで)",
    '90°エルボ(3"～6")',
    "90°ベント",
    "45°エルボ",
    "チーズ",
    "弁(2･1/2まで)",
    '弁(3"～6")',
]

st.set_page_config(page_title="配管サイズ自動算定", page_icon="🛠️", layout="centered")

st.title("配管サイズ自動算定")

st.markdown("### 入力条件")

# ① ガス名
gas = st.selectbox("① ガス名", ["Air"])

# ② 流量
flow_rate = st.number_input("② 流量 (Nm³/h)", min_value=0.0, value=1000.0, step=10.0)

# ③ 入口圧力
inlet_pressure = st.number_input("③ 入口圧力 (MPa)", min_value=0.0, value=0.9, step=0.1)

# ④ 出口圧力
outlet_pressure = st.number_input(
    "④ 出口圧力 (MPa)", min_value=0.0, value=0.7, step=0.1
)

# ⑤ 基準温度
temperature = st.number_input("⑤ 基準温度 (℃)", value=20.0, step=1.0)

# ⑥ 許容流速
velocity_limit = st.number_input("⑥ 許容流速 (m/s)", min_value=0.0, value=8.0, step=0.5)

# ⑦ 配管規格
schedule = st.selectbox("⑦ 配管規格", ["BA", "sch5", "sch10"])

# ⑧ 管の長さ
pipe_length = st.number_input(
    "⑧ 管の長さ (mm)", min_value=0.0, value=1000.0, step=100.0
)

st.markdown("### 継手入力")

# 継ぎ手の数量
fitting_counts = []

for i, name in enumerate(fitting_names):
    val = st.number_input(name, min_value=0, step=1, value=0, key=i)
    fitting_counts.append(val)

# 計算ボタン
if st.button("計算"):

    input_data = {
        "gas": gas,
        "flow_rate": flow_rate,
        "inlet_pressure": inlet_pressure,
        "outlet_pressure": outlet_pressure,
        "temperature": temperature,
        "velocity_limit": velocity_limit,
        "schedule": schedule,
        "pipe_length": pipe_length,
        "fitting_counts": fitting_counts,
    }

    pipe_name = select_pipe(input_data)

    st.write("### 推奨配管サイズ")
    st.success(pipe_name)

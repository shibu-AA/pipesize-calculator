import streamlit as st
import pandas as pd
from calc.calculator import select_pipe

fitting_names = [
    "90°エルボ(2･1/2まで)",
    '90°エルボ(3"～6")',
    "90°ベント",
    "45°エルボ",
    "チーズ",
    "弁(2･1/2まで)",
    '弁(3"～6")',
]

gas_table = pd.read_csv("data/gas/properties.csv")

st.set_page_config(page_title="配管サイズ自動算定", page_icon="🛠️", layout="centered")

st.title("配管サイズ自動算定")

st.markdown("#### 入力条件")

# ① ガス名
input_type = st.radio("① ガスの種類", ["名称", "化学式", "分子量指定"])
if input_type == "名称":
    gas = st.selectbox("名称", gas_table["名称"].tolist())
    molecular_weight = gas_table.loc[gas_table["名称"] == gas, "分子量"].iloc[0]
    gas_properties = gas_table.loc[
        gas_table["名称"] == gas, ["可燃性", "自燃性", "支燃性", "毒性", "腐食性"]
    ].iloc[0]
elif input_type == "化学式":
    gas = st.selectbox("化学式", gas_table["化学式"].tolist())
    molecular_weight = gas_table.loc[gas_table["化学式"] == gas, "分子量"].iloc[0]
    gas_properties = gas_table.loc[
        gas_table["化学式"] == gas, ["可燃性", "自燃性", "支燃性", "毒性", "腐食性"]
    ].iloc[0]
elif input_type == "分子量指定":
    molecular_weight = st.number_input("分子量", min_value=0.0, value=28.0, step=1.0)
    gas_properties = pd.Series(
        [0, 0, 0, 0, 0], index=["可燃性", "自燃性", "支燃性", "毒性", "腐食性"]
    )

st.write("気体の性質 ")
properties = ["可燃性", "自燃性", "支燃性", "毒性", "腐食性"]
selected = [name for name in properties if gas_properties[name] == 1]
st.info("・".join(selected))

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

# ⑨ 係数
coefficient = st.number_input("⑨ 係数", min_value=0.0, value=1.0, step=0.1)

st.markdown("#### 継手入力")

# 継ぎ手の数量
fitting_counts = []

for i, name in enumerate(fitting_names):
    val = st.number_input(name, min_value=0, step=1, value=0, key=i)
    fitting_counts.append(val)

# 計算ボタン
if st.button("計算"):

    input_data = {
        "molecular_weight": molecular_weight,
        "flow_rate": flow_rate,
        "inlet_pressure": inlet_pressure,
        "outlet_pressure": outlet_pressure,
        "temperature": temperature,
        "velocity_limit": velocity_limit,
        "schedule": schedule,
        "pipe_length": pipe_length,
        "coefficient": coefficient,
        "fitting_counts": fitting_counts,
    }

    recommended_pipe_name, delta_P, optimal_pipe_name = select_pipe(input_data)

    if recommended_pipe_name is None:
        st.error("Error")
    else:
        st.write("#### 推奨配管サイズ")
        st.info(recommended_pipe_name)

        st.write("#### 圧力損失")
        st.info(f"{delta_P:.2f} kg/cm²")

        st.write("#### 最適配管サイズ")
        st.success(optimal_pipe_name)

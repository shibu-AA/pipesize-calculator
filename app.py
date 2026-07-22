import streamlit as st
import pandas as pd
from calc.calculator import select_pipe
from pdf.report import create_pdf

fitting_names = [
    "90°エルボ(2･1/2まで)",
    '90°エルボ(3"～6")',
    "90°ベンド",
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
input_type = st.radio("① ガスの種類", ["リスト", "その他"])
if input_type == "リスト":
    gas = st.selectbox("気体名", gas_table["気体名＋化学式"].tolist())
    gas_name = gas_table.loc[gas_table["気体名＋化学式"] == gas, "気体名"].iloc[0]
    molecular_weight = gas_table.loc[gas_table["気体名＋化学式"] == gas, "分子量"].iloc[
        0
    ]
    gas_properties = gas_table.loc[
        gas_table["気体名＋化学式"] == gas,
        ["可燃性", "自燃性", "支燃性", "毒性", "腐食性"],
    ].iloc[0]

    st.write("気体の性質 ")
    properties = ["可燃性", "自燃性", "支燃性", "毒性", "腐食性"]
    selected = [name for name in properties if gas_properties[name] == 1]
    st.info("・".join(selected))
elif input_type == "その他":
    molecular_weight = st.number_input("分子量", min_value=0.0, value=28.0, step=1.0)
    gas_name = "分子量(" + str(molecular_weight) + ")"
    gas_properties = pd.Series(
        [0, 0, 0, 0, 0], index=["可燃性", "自燃性", "支燃性", "毒性", "腐食性"]
    )

# ② 流量
max_flow_rate = st.number_input(
    "② 流量 (L/min)", min_value=0.0, value=1000.0, step=10.0
)

# ③ 入口圧力
inlet_pressure = st.number_input("③ 入口圧力 (MPa)", min_value=0.0, value=0.9, step=0.1)

# ④ 出口圧力
outlet_pressure = st.number_input(
    "④ 出口圧力 (MPa)", min_value=0.0, value=0.7, step=0.1
)

# ⑤ 基準温度
temperature = st.number_input("⑤ 基準温度 (℃)", value=20.0, step=1.0)

# ⑥ 許容流速
velocity_limit = st.number_input(
    "⑥ 許容流速 (m/s)", min_value=0.0, value=10.0, step=0.5
)

# ⑦ 配管規格
schedule = st.selectbox("⑦ 配管規格", ["sch10", "sch5", "BA"])

# ⑧ 管の長さ
pipe_length = st.number_input("⑧ 管の長さ (m)", min_value=0.0, value=1000.0, step=100.0)

# ⑨ 係数
coefficient = st.number_input(
    "⑨ 稼働率(%)", min_value=0, max_value=100, value=40, step=10
)

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
        "max_flow_rate": max_flow_rate,
        "inlet_pressure": inlet_pressure,
        "outlet_pressure": outlet_pressure,
        "temperature": temperature,
        "velocity_limit": velocity_limit,
        "schedule": schedule,
        "pipe_length": pipe_length,
        "coefficient": coefficient,
        "fitting_counts": fitting_counts,
    }

    result = select_pipe(input_data)

    if result is None:
        st.error("Error")
    else:
        st.write("#### 最大流量の推奨配管サイズ")
        st.info(result["recommended_pipe_name_max"])

        st.write("#### 実流量の推奨配管サイズ")
        st.info(result["recommended_pipe_name_design"])

        st.write("#### 最適配管サイズ")
        st.success(result["optimal_pipe_name"])

        st.write("#### 最適配管サイズの圧力損失")
        st.info(f"{result['delta_P']:.2f} kg/cm²")

        pdf = create_pdf(gas_name, input_data, result)

        st.download_button(
            "PDFダウンロード",
            data=pdf,
            file_name="配管計算結果.pdf",
            mime="application/pdf",
        )

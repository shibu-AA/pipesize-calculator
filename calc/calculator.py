import math
import pandas as pd

PIPE_FILES = {
    "BA": "data/pipe/BA.csv",
    "sch5": "data/pipe/sch5.csv",
    "sch10": "data/pipe/sch10.csv",
}

fitting_equivalent_lengths = [30, 40, 15, 18, 60, 45, 60]


def select_pipe(input_data):

    gas = input_data["gas"]
    flow_rate = input_data["flow_rate"]
    inlet_pressure = input_data["inlet_pressure"]
    outlet_pressure = input_data["outlet_pressure"]
    temperature = input_data["temperature"]
    velocity_limit = input_data["velocity_limit"]
    schedule = input_data["schedule"]
    pipe_length = input_data["pipe_length"]
    fitting_counts = input_data["fitting_counts"]

    gas_table = pd.read_csv("data/gas/properties.csv")
    M = gas_table.loc[gas_table["化学式"] == gas, "分子量(Kg/Kmol)"].iloc[0]

    actual_flow = (
        (flow_rate / (1000 * 60))
        * (101.3 / (101.3 + outlet_pressure * 1000))
        * ((273 + temperature) / 273)
    )
    required_diameter = math.sqrt((4 * actual_flow) / (math.pi * velocity_limit)) * 1000

    pipe_table = pd.read_csv(PIPE_FILES[schedule])

    filtered = pipe_table[pipe_table["内径(D)(mm)"] >= required_diameter]

    for _, row in filtered.iterrows():
        fluid_density = ((inlet_pressure * 10.1972 + 1.033) / 1.033 * 101325) / (
            8314.3 * 293 / M
        )
        n = sum(
            [
                fitting_counts[i] * fitting_equivalent_lengths[i]
                for i in range(len(fitting_counts))
            ]
        )
        Ln = row["内径(D)(mm)"] * n / 1000
        delta_P = (
            (
                ((row["摩擦係数"]) * (pipe_length + Ln) * fluid_density)
                * (velocity_limit**2)
            )
            / (row["内径(D)(mm)"] * 0.001 * 2 * 9.8)
            * 0.0001
        )

        if outlet_pressure < inlet_pressure - delta_P * 0.0980665:
            return row["呼び径"]
    return "ERROR"

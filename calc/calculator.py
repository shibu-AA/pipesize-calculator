import math
import pandas as pd

PIPE_FILES = {
    "BA": "data/pipe/BA.csv",
    "sch5": "data/pipe/sch5.csv",
    "sch10": "data/pipe/sch10.csv",
}

fitting_equivalent_length_factors = [32, 40, 24, 15, 80, 300, 300]


def select_pipe(input_data):

    molecular_weight = input_data["molecular_weight"]
    max_flow_rate = input_data["max_flow_rate"]
    inlet_pressure = input_data["inlet_pressure"]
    outlet_pressure = input_data["outlet_pressure"]
    temperature = input_data["temperature"]
    velocity_limit = input_data["velocity_limit"]
    schedule = input_data["schedule"]
    pipe_length = input_data["pipe_length"]
    coefficient = input_data["coefficient"]
    fitting_counts = input_data["fitting_counts"]

    pipe_table = pd.read_csv(PIPE_FILES[schedule])

    # 最大流量の推奨配管サイズを求める
    actual_flow_rate = (
        (max_flow_rate / (1000 * 60))
        * (101.3 / (101.3 + outlet_pressure * 1000))
        * ((273 + temperature) / 273)
    )
    required_diameter_max = (
        math.sqrt((4 * actual_flow_rate) / (math.pi * velocity_limit)) * 1000
    )

    candidate = pipe_table[pipe_table["内径(D)(mm)"] >= required_diameter_max]
    if candidate.empty:
        return None

    recommended_pipe_name_max = candidate.iloc[0]["呼び径"]

    # 係数をかけた流量の推奨配管サイズを求める
    design_flow_rate = (
        (max_flow_rate * (coefficient / 100) / (1000 * 60))
        * (101.3 / (101.3 + outlet_pressure * 1000))
        * ((273 + temperature) / 273)
    )
    required_diameter_design = (
        math.sqrt((4 * design_flow_rate) / (math.pi * velocity_limit)) * 1000
    )

    candidate = pipe_table[pipe_table["内径(D)(mm)"] >= required_diameter_design]
    if candidate.empty:
        return None

    recommended_pipe_name_design = candidate.iloc[0]["呼び径"]

    # 係数をかけた流量の最適配管サイズを求める
    for _, row in candidate.iterrows():
        inner_diameter = row["内径(D)(mm)"]
        friction = row["摩擦係数"]
        fluid_density = ((inlet_pressure * 10.1972 + 1.033) / 1.033 * 101325) / (
            8314.3 * 293 / molecular_weight
        )
        equivalent_length_factor = sum(
            [
                fitting_counts[i] * fitting_equivalent_length_factors[i]
                for i in range(len(fitting_counts))
            ]
        )
        equivalent_pipe_length = row["内径(D)(mm)"] * equivalent_length_factor / 1000

        velocity = 4 * design_flow_rate / (math.pi * ((inner_diameter / 1000) ** 2))

        delta_P = (
            (
                (friction * (pipe_length + equivalent_pipe_length) * fluid_density)
                * (velocity**2)
            )
            / (row["内径(D)(mm)"] * 0.001 * 2 * 9.8)
            * 0.0001
        )

        if outlet_pressure < inlet_pressure - delta_P * 0.0980665:
            return {
                "actual_flow_rate": actual_flow_rate,
                "recommended_pipe_name_max": recommended_pipe_name_max,
                "design_flow_rate": design_flow_rate,
                "recommended_pipe_name_design": recommended_pipe_name_design,
                "inner_diameter": inner_diameter,
                "friction": friction,
                "fluid_density": fluid_density,
                "equivalent_length_factor": equivalent_length_factor,
                "equivalent_pipe_length": equivalent_pipe_length,
                "velocity": velocity,
                "delta_P": delta_P,
                "optimal_pipe_name": row["呼び径"],
            }
    return None

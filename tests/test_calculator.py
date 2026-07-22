from calc.calculator import select_pipe


def test_select_pipe_air_basic():
    input_data = {
        "molecular_weight": 28.97,
        "max_flow_rate": 4000,
        "inlet_pressure": 0.8,
        "outlet_pressure": 0.7,
        "temperature": 20,
        "velocity_limit": 8,
        "schedule": "sch10",
        "pipe_length": 1000,
        "coefficient": 40,
        "fitting_counts": [50, 0, 0, 0, 0, 30, 0],
    }

    result = select_pipe(input_data)

    assert result["recommended_pipe_name_max"] == "40A"
    assert result["recommended_pipe_name_design"] == "25A"
    assert result["optimal_pipe_name"] == "32A"
    assert round(result["delta_P"], 2) == 0.46

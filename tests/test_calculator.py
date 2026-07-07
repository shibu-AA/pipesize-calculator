from calc.calculator import select_pipe


def test_select_pipe_air_basic():
    input_data = {
        "molecular_weight": 28.97,
        "flow_rate": 1000,
        "inlet_pressure": 0.9,
        "outlet_pressure": 0.7,
        "temperature": 20,
        "velocity_limit": 8,
        "schedule": "sch5",
        "pipe_length": 1000,
        "coefficient": 1.0,
        "fitting_counts": [100, 0, 0, 0, 30, 10, 0],
    }

    recommended_pipe_name, delta_p, optimal_pipe_name = select_pipe(input_data)

    assert optimal_pipe_name == "40A"

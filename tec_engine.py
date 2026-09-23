
import numpy as np
import pandas as pd


def load_database():
    """Read the Tark TEC database."""

    df = pd.read_csv("tec_database.csv")

    required_columns = [
        "model", "stages", "Th_C",
        "Qcmax_W", "dTmax_C",
        "Imax_A", "Vmax_V", "R_ohm"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    return df


def interpolate_tec(model, Th, database):
    """
    Interpolate catalog parameters at a given
    hot-side temperature.

    Extrapolation is not permitted.
    """

    data = database[
        (database["model"] == model)
        & (database["stages"] == 1)
    ].copy()

    if data.empty:
        raise ValueError("TEC model not found.")

    data = data.sort_values("Th_C")

    temperatures = data["Th_C"].to_numpy()

    if len(np.unique(temperatures)) != len(temperatures):
        raise ValueError("Duplicate temperature entries.")

    if Th < temperatures.min() or Th > temperatures.max():
        raise ValueError(
            "Temperature is outside the catalog range."
        )

    parameters = [
        "Qcmax_W",
        "dTmax_C",
        "Imax_A",
        "Vmax_V",
        "R_ohm"
    ]

    result = {
        "model": model,
        "Th_C": Th
    }

    for parameter in parameters:

        result[parameter] = float(
            np.interp(
                Th,
                temperatures,
                data[parameter].to_numpy()
            )
        )

    return result

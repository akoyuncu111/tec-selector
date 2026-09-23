
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


# ==========================================
# Multi-TEC COP Optimization
# ==========================================

def optimize_multi_tec(
    performance_df,
    model,
    Th,
    dT,
    Qload,
    max_tec
):
    """
    Optimize identical TECs operating in parallel.

    All TECs have the same Th, dT and current.
    Uses manufacturer performance data.
    """

    data = performance_df[
        (performance_df["model"] == model)
        & (performance_df["Th_C"] == Th)
        & (performance_df["dT_C"] == dT)
    ].copy()

    if data.empty:
        raise ValueError(
            "No manufacturer data for selected conditions."
        )

    data = data.sort_values("I_A")

    currents = data["I_A"].to_numpy(dtype=float)
    voltages = data["V_V"].to_numpy(dtype=float)
    cooling = data["Qc_W"].to_numpy(dtype=float)

    if len(currents) < 2:
        raise ValueError(
            "At least two data points are required."
        )

    if (
        len(np.unique(currents)) != len(currents)
        or np.any(np.diff(cooling) <= 0)
        or np.any(voltages <= 0)
    ):
        raise ValueError(
            "Invalid or non-monotonic performance data."
        )

    results = []

    for n in range(1, int(max_tec) + 1):

        required_qc = Qload / n

        # Do not extrapolate beyond manufacturer data
        if (
            required_qc < cooling.min()
            or required_qc > cooling.max()
        ):
            continue

        # Interpolate required current
        current = float(
            np.interp(
                required_qc,
                cooling,
                currents
            )
        )

        # Interpolate voltage at that current
        voltage = float(
            np.interp(
                current,
                currents,
                voltages
            )
        )

        power_per_tec = current * voltage
        total_power = n * power_per_tec

        if total_power <= 0:
            continue

        cop = Qload / total_power

        results.append({
            "Model": model,
            "TEC Count": n,
            "Qc per TEC (W)": required_qc,
            "Current per TEC (A)": current,
            "Voltage per TEC (V)": voltage,
            "Total Power (W)": total_power,
            "System COP": cop,
            "Total Qh (W)": Qload + total_power
        })

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results).sort_values(
        "System COP",
        ascending=False
    ).reset_index(drop=True)

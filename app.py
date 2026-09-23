
import streamlit as st

import pandas as pd


from tec_engine import (
    load_database,
    interpolate_tec,
    optimize_multi_tec
)

st.set_page_config(
    page_title="TEC Selector",
    page_icon="❄️",
    layout="wide"
)

st.title("❄️ TEC Selector")
st.subheader("Laird / Tark TEC Selection Tool")

st.info(
    "Single-stage TEC selection and COP optimization"
)

st.divider()

st.header("1. Operating Conditions")

col1, col2 = st.columns(2)

with col1:
    q_load = st.number_input(
        "Total Heat Load (W)",
        min_value=0.1,
        value=40.0,
        step=1.0
    )

    delta_t = st.number_input(
        "TEC Temperature Difference (°C)",
        min_value=0.0,
        value=20.0,
        step=1.0
    )

with col2:
    t_hot = st.number_input(
        "Hot Side Temperature (°C)",
        value=50.0,
        step=1.0
    )

    t_cold = t_hot - delta_t

    st.metric(
        "Cold Side Temperature",
        f"{t_cold:.1f} °C"
    )

st.divider()

st.header("2. Mechanical Constraints")

col3, col4, col5 = st.columns(3)

with col3:
    max_length = st.number_input(
        "Maximum Length (mm)",
        min_value=1.0,
        value=100.0
    )

with col4:
    max_width = st.number_input(
        "Maximum Width (mm)",
        min_value=1.0,
        value=100.0
    )

with col5:
    max_height = st.number_input(
        "Maximum Height (mm)",
        min_value=0.1,
        value=10.0
    )

max_tec = st.number_input(
    "Maximum Number of TECs",
    min_value=1,
    max_value=100,
    value=4,
    step=1
)

st.divider()

st.header("3. TEC Configuration")

st.checkbox(
    "Single-stage TEC only",
    value=True,
    disabled=True
)

st.checkbox(
    "Allow multiple TECs",
    value=True,
    disabled=True
)

st.divider()

if st.button(
    "Find Optimal TEC",
    type="primary",
    use_container_width=True
):
    st.warning(
        "TEC optimization engine is not connected yet."
    )

    st.write("Selected operating conditions:")

    st.write(f"Heat Load: {q_load} W")
    st.write(f"Delta T: {delta_t} °C")
    st.write(f"Hot Side: {t_hot} °C")
    st.write(f"Cold Side: {t_cold} °C")

    st.write(
        f"Maximum Dimensions: "
        f"{max_length} x {max_width} x {max_height} mm"
    )

    st.write(f"Maximum TEC Count: {max_tec}")


st.divider()

st.header("4. Tark TEC Database")

try:
    df = pd.read_csv("tec_database.csv")

    st.success(
        f"Database loaded successfully: "
        f"{df['model'].nunique()} TEC model(s)"
    )

    selected_model = st.selectbox(
        "Select TEC Model",
        df["model"].unique()
    )

    model_data = df[
        df["model"] == selected_model
    ]

    st.dataframe(
        model_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Qcmax vs Hot Side Temperature")

    st.line_chart(
        model_data.set_index("Th_C")["Qcmax_W"]
    )
except Exception as e:
    st.error(f"Database error: {e}")

st.divider()

st.header("5. TEC Performance Calculation")

try:
    database = load_database()

    model_names = database["model"].unique()

    selected_tec = st.selectbox(
        "TEC Model for Calculation",
        model_names,
        key="calculation_model"
    )

    if st.button("Calculate TEC Parameters"):

        result = interpolate_tec(
            selected_tec,
            t_hot,
            database
        )

        st.success(
            "Catalog interpolation completed."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Qcmax",
                f"{result['Qcmax_W']:.2f} W"
            )

        with col2:
            st.metric(
                "Delta Tmax",
                f"{result['dTmax_C']:.2f} °C"
            )

        with col3:
            st.metric(
                "Imax",
                f"{result['Imax_A']:.2f} A"
            )

        st.write("Interpolated catalog parameters:")

        st.dataframe(
            pd.DataFrame([result]),
            hide_index=True
        )

        if delta_t >= result["dTmax_C"]:
            st.error(
                "Requested Delta T reaches or exceeds "
                "the catalog maximum. The required "
                "positive cooling load cannot be met "
                "at this operating condition."
            )
        else:
            st.info(
                "Temperature range check passed. "
                "Cooling capacity at the requested "
                "Delta T still requires calculation."
            )

except Exception as e:
    st.error(str(e))
except Exception as e:
    st.error(f"Database error: {e}")

# ==========================================
# 6. Manufacturer Performance Curves
# ==========================================

st.divider()

st.header("6. Manufacturer Performance Curves")

try:
    performance_df = pd.read_csv("tec_performance.csv")

    # Select only the required operating conditions
    perf = performance_df[
        (performance_df["model"] == selected_tec)
        & (performance_df["Th_C"] == t_hot)
        & (performance_df["dT_C"] == delta_t)
    ].copy()

    if perf.empty:
        st.warning(
            "No manufacturer performance data available "
            "for the selected model, Th and Delta T."
        )

    else:
        perf = perf.sort_values("I_A")

        # Electrical power
        perf["P_W"] = (
            perf["I_A"] * perf["V_V"]
        )

        # COP calculation
        perf["COP"] = (
            perf["Qc_W"] / perf["P_W"]
        )

        # Heat rejected to hot side
        perf["Qh_W"] = (
            perf["Qc_W"] + perf["P_W"]
        )

        st.success(
            f"{len(perf)} manufacturer data points loaded."
        )

        # Performance table
        st.subheader("Performance Data")

        st.dataframe(
            perf[
                ["I_A", "V_V", "Qc_W",
                 "P_W", "COP", "Qh_W"]
            ].style.format({
                "I_A": "{:.2f}",
                "V_V": "{:.2f}",
                "Qc_W": "{:.2f}",
                "P_W": "{:.2f}",
                "COP": "{:.3f}",
                "Qh_W": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        # COP vs Current
        st.subheader("COP vs Current")

        st.line_chart(
            perf.set_index("I_A")["COP"],
            x_label="Current (A)",
            y_label="COP"
        )

        # Cooling capacity vs Current
        st.subheader("Cooling Capacity vs Current")

        st.line_chart(
            perf.set_index("I_A")["Qc_W"],
            x_label="Current (A)",
            y_label="Qc (W)"
        )

        # Electrical power vs Current
        st.subheader("Electrical Power vs Current")

        st.line_chart(
            perf.set_index("I_A")["P_W"],
            x_label="Current (A)",
            y_label="Electrical Power (W)"
        )

        # Maximum COP among sampled points
        best_idx = perf["COP"].idxmax()
        best = perf.loc[best_idx]

        st.subheader("Highest COP Among Sampled Points")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "COP",
            f"{best['COP']:.3f}"
        )

        c2.metric(
            "Current",
            f"{best['I_A']:.2f} A"
        )

        c3.metric(
            "Cooling Capacity",
            f"{best['Qc_W']:.2f} W"
        )

        st.caption(
            "This result considers only the sampled "
            "manufacturer data points. It does not "
            "yet account for the requested total heat "
            "load, mechanical constraints or multiple TECs."
        )

except Exception as e:
    st.error(f"Performance data error: {e}")

# ==========================================
# 7. Multi-TEC Optimization
# ==========================================

st.divider()

st.header("7. Multi-TEC COP Optimization")

st.info(
    "Identical single-stage TECs operating "
    "at the same hot-side temperature and Delta T."
)

if st.button(
    "Optimize Multi-TEC Configuration",
    type="primary",
    use_container_width=True
):

    try:
        performance_df = pd.read_csv(
            "tec_performance.csv"
        )

        optimization = optimize_multi_tec(
            performance_df=performance_df,
            model=selected_tec,
            Th=t_hot,
            dT=delta_t,
            Qload=q_load,
            max_tec=max_tec
        )

        if optimization.empty:

            st.warning(
                "No configuration found within "
                "the available manufacturer data."
            )

        else:

            st.success(
                f"{len(optimization)} configurations evaluated."
            )

            st.subheader("Configuration Comparison")

            st.dataframe(
                optimization.style.format({
                    "Qc per TEC (W)": "{:.2f}",
                    "Current per TEC (A)": "{:.3f}",
                    "Voltage per TEC (V)": "{:.3f}",
                    "Total Power (W)": "{:.2f}",
                    "System COP": "{:.3f}",
                    "Total Qh (W)": "{:.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )

            st.subheader("COP vs TEC Count")

            chart_data = optimization.sort_values(
                "TEC Count"
            )

            st.line_chart(
                chart_data.set_index(
                    "TEC Count"
                )["System COP"],
                x_label="Number of TECs",
                y_label="System COP"
            )

            best = optimization.iloc[0]

            st.subheader("Highest COP Configuration")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "TEC Count",
                f"{int(best['TEC Count'])}"
            )

            c2.metric(
                "System COP",
                f"{best['System COP']:.3f}"
            )

            c3.metric(
                "Total Power",
                f"{best['Total Power (W)']:.2f} W"
            )

            st.write(
                f"Current per TEC: "
                f"{best['Current per TEC (A)']:.3f} A"
            )

            st.write(
                f"Voltage per TEC: "
                f"{best['Voltage per TEC (V)']:.3f} V"
            )

            st.write(
                f"Total heat rejection: "
                f"{best['Total Qh (W)']:.2f} W"
            )

            st.caption(
                "Preliminary electrical optimization. "
                "Mechanical fit and thermal interfaces "
                "have not yet been evaluated."
            )

    except Exception as e:

        st.error(
            f"Optimization error: {e}"
        )


import streamlit as st

import pandas as pd
from tec_engine import load_database, interpolate_tec

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

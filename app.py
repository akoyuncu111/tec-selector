
import streamlit as st

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

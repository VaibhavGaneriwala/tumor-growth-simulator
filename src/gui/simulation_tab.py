# Author: Karthik Mudenahalli Ashoka
# Description: Streamlit tab for interactive tumor growth simulation.

import plotly.graph_objects as go
import streamlit as st

from src.core.growth import (simulate_exponential, simulate_linear, simulate_gompertz, simulate_with_scenario)
from src.ml.growth_predictor import is_model_available, predict_growth_rate

def render(patients, nifti_root):
    """Render the Simulation tab."""
    st.header("Simulation")
    st.caption("Explore how a tumor's volume evolves over time under different growth models. Adjust the parameters on the left and the chart updates live.")

    col_params, col_chart = st.columns([1, 2])

    with col_params:
        st.subheader("Parameters")
        model = st.selectbox("Growth model", options=["Exponential", "Gompertz", "Linear"], index=0, key="sim_model", help=("Exponential: unbounded growth. Gompertz: more realistic, flattens near a maximum. Linear: simple straight-line baseline."))
        v0 = st.slider("Initial volume V₀ (mm³)", min_value=100, max_value=20000, value=1000, step=100, key="sim_v0")
        days = st.slider("Simulation length (days)", min_value=30, max_value=730, value=180, step=10, key="sim_days")

        if model == "Exponential":
            use_ml_prediction = False
            ml_predicted_k = None
            if is_model_available():
                use_ml_prediction = st.checkbox("Use ML-predicted growth rate", key="sim_use_ml", value=False, help=("Predict the growth rate using a Random Forest model."))

            if use_ml_prediction:
                pred_age = 60
                pred_sex = "Female"
                pred_volume = float(v0)

                selected_id = st.session_state.get("selected_patient_id")
                if selected_id is not None and patients is not None:
                    for p in patients:
                        if p.patient_id == selected_id:
                            age_window = p.age_range()
                            if age_window is not None:
                                pred_age = age_window[0]
                            if p.sex is not None:
                                pred_sex = p.sex
                            break

                ml_predicted_k = predict_growth_rate(age=pred_age, sex=pred_sex, initial_volume_mm3=pred_volume)

                if ml_predicted_k is not None:
                    clamped_k = max(-0.05, min(0.05, ml_predicted_k))
                    st.caption(
                        f"ML prediction for "
                        f"age={pred_age}, sex={pred_sex}, "
                        f"V₀={pred_volume:,.0f} mm³ → "
                        f"k = **{ml_predicted_k:.5f} / day**"
                    )
                    default_k = clamped_k
                else:
                    st.warning("Model unavailable — falling back to manual slider.")
                    default_k = 0.01
            else:
                default_k = 0.01
            k = st.slider("Growth rate k (per day)", min_value=-0.05, max_value=0.05, value=default_k, step=0.001, format="%.3f", key="sim_k_exp", help="Positive = growing, negative = shrinking.")
            slope = None
            carrying_capacity = None
        elif model == "Gompertz":
            k = st.slider("Growth rate k (per day)", min_value=0.001, max_value=0.1, value=0.02, step=0.001, format="%.3f", key="sim_k_gomp")
            carrying_capacity = st.slider("Carrying capacity K (mm³)", min_value=1000, max_value=100000, value=50000, step=1000, key="sim_carrying_cap", help="Maximum volume the tumor can reach.")
            slope = None
        else:
            slope = st.slider("Slope (mm³ per day)", min_value=-200, max_value=200, value=20, step=5, key="sim_slope")
            k = None
            carrying_capacity = None

        st.divider()

        enable_whatif = st.checkbox("Enable what-if treatment overlay", value=False, disabled=(model != "Exponential"), key="sim_enable_whatif", help="Only available for the Exponential model.")

        if enable_whatif and model == "Exponential":
            treatment_day = st.slider("Treatment start day", min_value=0, max_value=days, value=min(60, days), step=1, key="sim_treatment_day")
            post_k = st.slider("Post-treatment growth rate (per day)", min_value=-0.1, max_value=0.05, value=-0.02, step=0.001, format="%.3f", key="sim_post_k", help="Typically negative for shrinkage.")
        else:
            treatment_day = None
            post_k = None

        if st.button("Reset to defaults", key="sim_reset_btn"):
            keys_to_clear = [
                "sim_model", "sim_v0", "sim_days",
                "sim_use_ml", "sim_k_exp",
                "sim_k_gomp", "sim_carrying_cap",
                "sim_slope",
                "sim_enable_whatif", "sim_treatment_day", "sim_post_k",
            ]
            for k_name in keys_to_clear:
                if k_name in st.session_state:
                    del st.session_state[k_name]
            st.rerun()

    if model == "Exponential" and k is not None and k * days > 20:
        st.warning(
            f"k × days = {k * days:.1f} — exponential growth will produce unphysically large volumes. "
            "Consider reducing the growth rate or simulation length."
        )

    if model == "Exponential":
        base_days, base_volumes = simulate_exponential(v0, k, days)
    elif model == "Gompertz":
        base_days, base_volumes = simulate_gompertz(v0, k, carrying_capacity, days)
    else:
        base_days, base_volumes = simulate_linear(v0, slope, days)

    # what-if curve
    scenario_days, scenario_volumes = None, None
    if enable_whatif and model == "Exponential":
        scenario_days, scenario_volumes = simulate_with_scenario( v0=v0, k=k, days=days, treatment_start_day=treatment_day, post_treatment_k=post_k)

    with col_chart:
        st.subheader("Projected volume over time")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=base_days, y=base_volumes, mode="lines", name=f"{model} baseline", line=dict(width=3)))

        if scenario_days is not None:
            fig.add_trace(go.Scatter(x=scenario_days, y=scenario_volumes, mode="lines", name="With treatment", line=dict(width=3, dash="dash")))
            fig.add_vline(x=treatment_day, line_dash="dot", line_color="gray", annotation_text="Treatment start", annotation_position="top")

        fig.update_layout(xaxis_title="Days from start", yaxis_title="Tumor volume (mm³)", hovermode="x unified", height=500, margin=dict(l=40, r=20, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

        # Quick summary numbers
        final_volume = base_volumes[-1]
        fold_change = final_volume / v0 if v0 > 0 else 0
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Start volume", f"{v0:,.0f} mm³")
        metric_col2.metric("Final volume", f"{final_volume:,.0f} mm³")
        metric_col3.metric("Fold change", f"{fold_change:.2f}×")

        if scenario_volumes is not None:
            st.caption(
                f"With treatment on day {treatment_day}: final volume "
                f"{scenario_volumes[-1]:,.0f} mm³ "
                f"({scenario_volumes[-1] / v0:.2f}× start)."
            )
        st.divider()

        csv_lines = []
        if scenario_volumes is not None:
            csv_lines.append("day,baseline_volume_mm3,scenario_volume_mm3")
            for day, base_v, scen_v in zip(base_days, base_volumes, scenario_volumes):
                csv_lines.append(f"{day},{base_v:.4f},{scen_v:.4f}")
        else:
            csv_lines.append("day,volume_mm3")
            for day, vol in zip(base_days, base_volumes):
                csv_lines.append(f"{day},{vol:.4f}")
        csv_content = "\n".join(csv_lines)

        filename = f"simulation_{model.lower()}_{days}days.csv"

        st.download_button(label="Download results as CSV", data=csv_content, file_name=filename, mime="text/csv", key="sim_download_btn", help="Save the current simulation curves to a CSV file.")
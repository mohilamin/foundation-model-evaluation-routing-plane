"""Streamlit dashboard for the model routing control plane."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.routing_plane_core import DATA, route_request, run_pipeline

st.set_page_config(page_title="Model Routing Control Plane", layout="wide")


def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV and run the pipeline if data is missing."""
    if not path.exists():
        run_pipeline()
    return pd.read_csv(path)


st.title("Foundation Model Evaluation & Routing Control Plane")
st.caption("Deterministic enterprise model evaluation, routing, scorecards, canary/shadow analysis, and deployment readiness.")

leaderboard = load_csv(DATA / "scorecards" / "model_leaderboard.csv")
routing = load_csv(DATA / "routing" / "routing_decisions.csv")
monitoring = load_csv(DATA / "monitoring" / "model_monitoring_report.csv")

tabs = st.tabs(
    [
        "Executive Overview",
        "Model Registry",
        "Model Leaderboard",
        "Evaluation Slices",
        "Routing Lab",
        "Pareto Frontier",
        "Canary and Shadow",
        "Monitoring",
        "Scorecards",
        "Deployment Readiness",
    ]
)

with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Models", len(leaderboard))
    c2.metric("Routing Decisions", len(routing))
    c3.metric("Avg Utility", f"{routing['utility_score'].mean():.2f}")
    c4.metric("Fallback Rate", f"{(routing['selected_model_id'] == 'fallback_model').mean():.1%}")
    c5.metric("Portfolio Health", f"{monitoring['model_health_score'].mean():.1f}")
    st.dataframe(leaderboard[["rank", "model_id", "stage", "quality_score", "safety_pass_rate", "average_latency_ms", "average_cost_usd", "overall_model_utility_score"]])

with tabs[1]:
    registry = load_csv(DATA / "model_outputs" / "model_registry.csv")
    st.dataframe(registry)

with tabs[2]:
    st.bar_chart(leaderboard.set_index("model_id")["overall_model_utility_score"])
    st.dataframe(leaderboard)

with tabs[3]:
    slices = load_csv(DATA / "scorecards" / "model_slice_report.csv")
    task_type = st.selectbox("Task type", sorted(slices["task_type"].unique()))
    st.dataframe(slices[slices["task_type"] == task_type].head(100))

with tabs[4]:
    with st.form("routing_lab"):
        task_type = st.selectbox("Task type", sorted(load_csv(DATA / "evaluation" / "evaluation_tasks.csv")["task_type"].unique()))
        domain = st.selectbox("Domain", sorted(load_csv(DATA / "evaluation" / "evaluation_tasks.csv")["domain"].unique()))
        risk_level = st.selectbox("Risk", ["low", "medium", "high"])
        safety_required = st.checkbox("Safety required", value=risk_level == "high")
        max_latency_ms = st.number_input("Max latency ms", value=1200, min_value=100)
        max_cost_usd = st.number_input("Max cost USD", value=0.004, format="%.6f")
        min_quality_score = st.slider("Min quality", 0.0, 1.0, 0.7)
        submitted = st.form_submit_button("Route request")
    if submitted:
        st.json(
            route_request(
                {
                    "task_type": task_type,
                    "domain": domain,
                    "risk_level": risk_level,
                    "safety_required": safety_required,
                    "max_latency_ms": max_latency_ms,
                    "max_cost_usd": max_cost_usd,
                    "min_quality_score": min_quality_score,
                }
            )
        )

with tabs[5]:
    pareto = load_csv(DATA / "scorecards" / "pareto_frontier_report.csv")
    st.scatter_chart(pareto, x="average_cost_usd", y="quality_score", color="pareto_efficient_flag")
    st.dataframe(pareto)

with tabs[6]:
    canary = load_csv(DATA / "canary" / "canary_evaluation_report.csv")
    rollout = load_csv(DATA / "scorecards" / "canary_rollout_decision.csv")
    st.dataframe(rollout)
    st.dataframe(canary.head(100))

with tabs[7]:
    st.dataframe(monitoring)
    st.bar_chart(monitoring.set_index("model_id")["model_health_score"])

with tabs[8]:
    st.write(sorted(path.name for path in (DATA / "scorecards").glob("*")))

with tabs[9]:
    readiness = load_csv(DATA / "scorecards" / "deployment_readiness_report.csv")
    st.dataframe(readiness)

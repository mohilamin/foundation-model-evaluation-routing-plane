"""Tests for the model evaluation and routing control plane."""

from pathlib import Path

import duckdb
import pandas as pd
from fastapi.testclient import TestClient

from src.api.main import app
from src.evaluation.metrics import weighted_utility
from src.evaluation.regression_eval import regression_flag
from src.evaluation.reliability_eval import reliability_status
from src.evaluation.safety_eval import passes_safety
from src.monitoring.alerting import should_alert
from src.monitoring.model_health import health_status
from src.optimization.budget_policy import within_budget
from src.optimization.cost_latency_optimizer import latency_score
from src.routing.constraint_filter import satisfies_constraint
from src.routing.fallback_policy import choose_fallback
from src.routing.request_classifier import classify_request
from src.routing.utility_scorer import route_utility
from src.routing_plane_core import DATA, compare_models, deployment_readiness, model_specs, route_request, run_pipeline


def test_task_generation_count() -> None:
    assert len(pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")) == 2000


def test_routing_demo_request_count() -> None:
    assert len(pd.read_csv(DATA / "evaluation" / "routing_demo_requests.csv")) == 250


def test_high_risk_safety_tasks_exist() -> None:
    tasks = pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")
    assert int(tasks["safety_required"].sum()) >= 100


def test_latency_sensitive_tasks_exist() -> None:
    tasks = pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")
    assert int(tasks["latency_sensitive_flag"].sum()) >= 100


def test_cost_sensitive_tasks_exist() -> None:
    tasks = pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")
    assert int(tasks["cost_sensitive_flag"].sum()) >= 100


def test_domain_specialized_tasks_exist() -> None:
    tasks = pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")
    assert int(tasks["domain_specialized_flag"].sum()) >= 100


def test_golden_answers_exist() -> None:
    assert (DATA / "evaluation" / "golden_answers.json").exists()


def test_evaluation_slices_exist() -> None:
    assert len(pd.read_csv(DATA / "evaluation" / "evaluation_slices.csv")) > 20


def test_model_specs_count() -> None:
    assert len(model_specs()) == 10


def test_model_registry_csv_count() -> None:
    assert len(pd.read_csv(DATA / "model_outputs" / "model_registry.csv")) == 10


def test_model_registry_yaml_exists() -> None:
    assert Path("config/model_registry.yaml").exists()


def test_model_cards_exist() -> None:
    assert len(list((DATA / "model_outputs" / "model_cards").glob("*.md"))) == 10


def test_simulated_outputs_count() -> None:
    assert len(pd.read_csv(DATA / "model_outputs" / "simulated_model_outputs.csv")) == 20000


def test_simulated_outputs_have_quality_range() -> None:
    outputs = pd.read_csv(DATA / "model_outputs" / "simulated_model_outputs.csv")
    assert outputs["simulated_quality_score"].between(0, 1).all()


def test_simulated_outputs_have_safety_range() -> None:
    outputs = pd.read_csv(DATA / "model_outputs" / "simulated_model_outputs.csv")
    assert outputs["simulated_safety_score"].between(0, 1).all()


def test_fast_small_model_lower_high_risk_quality() -> None:
    outputs = pd.read_csv(DATA / "model_outputs" / "simulated_model_outputs.csv")
    tasks = pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")
    merged = outputs.merge(tasks[["task_id", "risk_level"]], on="task_id")
    high = merged[(merged["model_id"] == "fast_small_model") & (merged["risk_level"] == "high")]["simulated_quality_score"].mean()
    low = merged[(merged["model_id"] == "fast_small_model") & (merged["risk_level"] == "low")]["simulated_quality_score"].mean()
    assert high < low


def test_finance_domain_model_finance_strength() -> None:
    slices = pd.read_csv(DATA / "scorecards" / "model_slice_report.csv")
    finance = slices[(slices["model_id"] == "finance_domain_model") & (slices["domain"] == "finance")]["quality_score"].mean()
    assert finance > 0.85


def test_healthcare_domain_model_healthcare_strength() -> None:
    slices = pd.read_csv(DATA / "scorecards" / "model_slice_report.csv")
    healthcare = slices[(slices["model_id"] == "healthcare_domain_model") & (slices["domain"] == "healthcare")]["quality_score"].mean()
    assert healthcare > 0.86


def test_code_specialist_code_strength() -> None:
    outputs = pd.read_csv(DATA / "model_outputs" / "simulated_model_outputs.csv")
    tasks = pd.read_csv(DATA / "evaluation" / "evaluation_tasks.csv")
    merged = outputs.merge(tasks[["task_id", "task_type"]], on="task_id")
    code = merged[(merged["model_id"] == "code_specialist_model") & (merged["task_type"] == "code_assistance")]["simulated_quality_score"].mean()
    assert code > 0.9


def test_model_evaluation_report_exists() -> None:
    assert (DATA / "scorecards" / "model_evaluation_report.csv").exists()


def test_model_evaluation_report_rows() -> None:
    assert len(pd.read_csv(DATA / "scorecards" / "model_evaluation_report.csv")) == 10


def test_model_leaderboard_exists() -> None:
    assert (DATA / "scorecards" / "model_leaderboard.csv").exists()


def test_model_leaderboard_ranked() -> None:
    leaderboard = pd.read_csv(DATA / "scorecards" / "model_leaderboard.csv")
    assert leaderboard.iloc[0]["rank"] == 1


def test_slice_report_exists() -> None:
    assert len(pd.read_csv(DATA / "scorecards" / "model_slice_report.csv")) > 100


def test_model_cards_summary_exists() -> None:
    assert (DATA / "scorecards" / "model_cards_summary.csv").exists()


def test_weighted_utility_range() -> None:
    score = weighted_utility(0.8, 0.9, 0.95, 0.7, 0.8)
    assert 0 <= score <= 1


def test_safety_eval_required() -> None:
    assert passes_safety(0.91, True)


def test_safety_eval_blocks_low_score() -> None:
    assert not passes_safety(0.7, True)


def test_reliability_status() -> None:
    assert reliability_status(0.96) == "healthy"


def test_regression_eval() -> None:
    assert regression_flag(-0.04)


def test_request_classifier() -> None:
    result = classify_request({"task_type": "classification", "domain": "finance", "risk_level": "high"})
    assert result["domain"] == "finance"


def test_constraint_filter() -> None:
    assert satisfies_constraint(100, 200)


def test_utility_scorer() -> None:
    assert route_utility(0.8, 0.9, 0.95, 0.7, 0.8) > 0.7


def test_fallback_policy() -> None:
    assert choose_fallback() == "fallback_model"


def test_routing_decisions_exist() -> None:
    assert len(pd.read_csv(DATA / "routing" / "routing_decisions.csv")) == 250


def test_routing_decisions_have_selected_model() -> None:
    routing = pd.read_csv(DATA / "routing" / "routing_decisions.csv")
    assert routing["selected_model_id"].notna().all()


def test_routing_decisions_have_fallback_model() -> None:
    routing = pd.read_csv(DATA / "routing" / "routing_decisions.csv")
    assert (routing["fallback_model_id"] == "fallback_model").all()


def test_routing_explanations_exist() -> None:
    assert (DATA / "routing" / "routing_decision_explanations.json").exists()


def test_fallback_decisions_exist() -> None:
    assert (DATA / "routing" / "fallback_decisions.csv").exists()


def test_route_request_returns_model() -> None:
    result = route_request({"task_type": "summarization", "domain": "general_business"})
    assert "selected_model" in result


def test_high_risk_healthcare_route_safe() -> None:
    result = route_request({"task_type": "healthcare_claim_review", "domain": "healthcare", "risk_level": "high", "safety_required": True, "min_quality_score": 0.8, "max_latency_ms": 1500, "max_cost_usd": 0.006})
    assert result["estimated_safety_score"] >= 0.9


def test_finance_route_prefers_allowed_model() -> None:
    result = route_request({"task_type": "finance_explanation", "domain": "finance", "risk_level": "medium", "max_latency_ms": 1200, "max_cost_usd": 0.004})
    assert result["selected_model"] in {"finance_domain_model", "balanced_general_model", "fallback_model", "safety_guarded_model"}


def test_code_route_selects_code_or_fallback() -> None:
    result = route_request({"task_type": "code_assistance", "domain": "software_engineering", "risk_level": "low", "max_latency_ms": 900, "max_cost_usd": 0.004})
    assert result["selected_model"] in {"code_specialist_model", "balanced_general_model", "fallback_model"}


def test_cheap_batch_route() -> None:
    result = route_request({"task_type": "batch_low_risk_summary", "domain": "general_business", "risk_level": "low", "max_latency_ms": 1000, "max_cost_usd": 0.002})
    assert result["selected_model"] in {"cheap_batch_model", "fast_small_model", "fallback_model", "balanced_general_model"}


def test_routing_quality_report_exists() -> None:
    assert (DATA / "scorecards" / "routing_quality_report.csv").exists()


def test_routing_quality_score_range() -> None:
    report = pd.read_csv(DATA / "scorecards" / "routing_quality_report.csv")
    assert report.iloc[0]["overall_routing_quality_score"] >= 0


def test_pareto_frontier_report_exists() -> None:
    assert (DATA / "scorecards" / "pareto_frontier_report.csv").exists()


def test_pareto_frontier_has_flags() -> None:
    frontier = pd.read_csv(DATA / "scorecards" / "pareto_frontier_report.csv")
    assert "pareto_efficient_flag" in frontier.columns


def test_pareto_by_task_type_exists() -> None:
    assert (DATA / "scorecards" / "pareto_frontier_by_task_type.csv").exists()


def test_latency_score_range() -> None:
    assert 0 <= latency_score(500, 1000) <= 1


def test_budget_policy() -> None:
    assert within_budget(0.001, 0.002)


def test_canary_report_exists() -> None:
    assert (DATA / "canary" / "canary_evaluation_report.csv").exists()


def test_canary_report_rows() -> None:
    assert len(pd.read_csv(DATA / "canary" / "canary_evaluation_report.csv")) == 50


def test_shadow_report_exists() -> None:
    assert (DATA / "shadow" / "shadow_traffic_report.csv").exists()


def test_rollout_decision_exists() -> None:
    assert (DATA / "scorecards" / "canary_rollout_decision.csv").exists()


def test_canary_has_regression_flag() -> None:
    canary = pd.read_csv(DATA / "canary" / "canary_evaluation_report.csv")
    assert "regression_flag" in canary.columns


def test_monitoring_report_exists() -> None:
    assert (DATA / "monitoring" / "model_monitoring_report.csv").exists()


def test_routing_monitoring_report_exists() -> None:
    assert (DATA / "monitoring" / "routing_monitoring_report.csv").exists()


def test_model_health_scorecard_exists() -> None:
    assert (DATA / "scorecards" / "model_health_scorecard.csv").exists()


def test_health_status() -> None:
    assert health_status(90) == "healthy"


def test_should_alert() -> None:
    assert should_alert(70)


def test_deployment_readiness_report_exists() -> None:
    assert (DATA / "scorecards" / "deployment_readiness_report.csv").exists()


def test_deployment_readiness_score() -> None:
    assert deployment_readiness()["deployment_readiness_score"] >= 90


def test_pipeline_summary_exists() -> None:
    assert (DATA / "scorecards" / "pipeline_summary.json").exists()


def test_duckdb_warehouse_exists() -> None:
    assert (DATA / "warehouse" / "model_routing_plane.duckdb").exists()


def test_duckdb_tables_exist() -> None:
    con = duckdb.connect(str(DATA / "warehouse" / "model_routing_plane.duckdb"), read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    con.close()
    assert {"evaluation_tasks", "model_registry", "routing_decisions", "pareto_frontier"}.issubset(tables)


def test_compare_models() -> None:
    result = compare_models(["balanced_general_model", "accurate_large_model"])
    assert len(result) == 2


def test_api_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_api_model_registry() -> None:
    client = TestClient(app)
    assert client.get("/model-registry").status_code == 200


def test_api_model_detail() -> None:
    client = TestClient(app)
    assert client.get("/models/balanced_general_model").json()["model_id"] == "balanced_general_model"


def test_api_model_leaderboard() -> None:
    client = TestClient(app)
    assert client.get("/model-leaderboard").status_code == 200


def test_api_evaluation_summary() -> None:
    client = TestClient(app)
    assert client.get("/evaluation-summary").status_code == 200


def test_api_routing_decisions() -> None:
    client = TestClient(app)
    assert client.get("/routing-decisions").status_code == 200


def test_api_pareto_frontier() -> None:
    client = TestClient(app)
    assert client.get("/pareto-frontier").status_code == 200


def test_api_canary_report() -> None:
    client = TestClient(app)
    assert client.get("/canary-report").status_code == 200


def test_api_monitoring_summary() -> None:
    client = TestClient(app)
    assert client.get("/monitoring-summary").status_code == 200


def test_api_scorecards() -> None:
    client = TestClient(app)
    assert client.get("/scorecards").status_code == 200


def test_api_route_request() -> None:
    client = TestClient(app)
    response = client.post("/route-request", json={"task_type": "summarization", "domain": "general_business"})
    assert response.status_code == 200
    assert "selected_model" in response.json()


def test_api_evaluate_model() -> None:
    client = TestClient(app)
    response = client.post("/evaluate-model", json={"model_id": "balanced_general_model"})
    assert response.status_code == 200
    assert response.json()["model_id"] == "balanced_general_model"


def test_api_simulate_routing_batch() -> None:
    client = TestClient(app)
    response = client.post("/simulate-routing-batch")
    assert response.status_code == 200


def test_api_compare_models() -> None:
    client = TestClient(app)
    response = client.post("/compare-models", json={"model_ids": ["balanced_general_model", "accurate_large_model"]})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_dashboard_file_exists() -> None:
    assert Path("src/dashboard/app.py").exists()


def test_api_file_exists() -> None:
    assert Path("src/api/main.py").exists()


def test_dockerfile_exists() -> None:
    assert Path("Dockerfile").exists()


def test_streamlit_config_exists() -> None:
    assert Path(".streamlit/config.toml").exists()


def test_requirements_exists() -> None:
    assert Path("requirements.txt").exists()


def test_readme_has_deployment_section() -> None:
    assert "Streamlit Community Cloud Deployment" in Path("README.md").read_text(encoding="utf-8")


def test_no_external_api_required_in_readme() -> None:
    assert "No secrets are required" in Path("README.md").read_text(encoding="utf-8")


def test_pipeline_execution_fixture(generated_artifacts: dict) -> None:
    assert generated_artifacts["tasks"]["evaluation_tasks"] == 2000


def test_pipeline_warehouse_loaded(generated_artifacts: dict) -> None:
    assert generated_artifacts["warehouse"]["tables_loaded"] >= 10


def test_scorecard_files_count() -> None:
    assert len(list((DATA / "scorecards").glob("*"))) >= 12


def test_run_pipeline_returns_summary() -> None:
    summary = run_pipeline()
    assert summary["model_registry"]["models"] == 10

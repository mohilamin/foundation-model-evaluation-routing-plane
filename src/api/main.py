"""FastAPI service for the model routing control plane."""

from fastapi import FastAPI

from src.api.schemas import CompareModelsRequest, EvaluateModelRequest, RouteRequest
from src.routing_plane_core import DATA, compare_models, read_csv_records, route_request, run_pipeline

app = FastAPI(title="Foundation Model Evaluation & Routing Control Plane")


@app.get("/health")
def health() -> dict:
    """Return service health."""
    return {"status": "ok", "external_apis_required": False}


@app.get("/model-registry")
def model_registry() -> list[dict]:
    """Return model registry records."""
    return read_csv_records(DATA / "model_outputs" / "model_registry.csv")


@app.get("/models/{model_id}")
def model_detail(model_id: str) -> dict:
    """Return one model registry record."""
    records = read_csv_records(DATA / "model_outputs" / "model_registry.csv")
    return next((record for record in records if record["model_id"] == model_id), {"error": "model not found"})


@app.get("/model-leaderboard")
def model_leaderboard() -> list[dict]:
    """Return model leaderboard."""
    return read_csv_records(DATA / "scorecards" / "model_leaderboard.csv")


@app.get("/evaluation-summary")
def evaluation_summary() -> list[dict]:
    """Return model evaluation summary."""
    return read_csv_records(DATA / "scorecards" / "model_evaluation_report.csv")


@app.get("/routing-decisions")
def routing_decisions() -> list[dict]:
    """Return routing decisions."""
    return read_csv_records(DATA / "routing" / "routing_decisions.csv", limit=250)


@app.get("/pareto-frontier")
def pareto_frontier() -> list[dict]:
    """Return Pareto frontier report."""
    return read_csv_records(DATA / "scorecards" / "pareto_frontier_report.csv")


@app.get("/canary-report")
def canary_report() -> list[dict]:
    """Return canary report."""
    return read_csv_records(DATA / "canary" / "canary_evaluation_report.csv")


@app.get("/monitoring-summary")
def monitoring_summary() -> list[dict]:
    """Return monitoring summary."""
    return read_csv_records(DATA / "monitoring" / "model_monitoring_report.csv")


@app.get("/scorecards")
def scorecards() -> dict:
    """Return available scorecard files."""
    if not (DATA / "scorecards").exists():
        run_pipeline()
    return {"scorecards": sorted(path.name for path in (DATA / "scorecards").glob("*"))}


@app.post("/route-request")
def post_route_request(request: RouteRequest) -> dict:
    """Route a request."""
    return route_request(request.model_dump())


@app.post("/evaluate-model")
def evaluate_model(request: EvaluateModelRequest) -> dict:
    """Return scorecard record for a model."""
    records = read_csv_records(DATA / "scorecards" / "model_evaluation_report.csv")
    return next((record for record in records if record["model_id"] == request.model_id), {"error": "model not found"})


@app.post("/simulate-routing-batch")
def simulate_routing_batch() -> dict:
    """Run the pipeline and return routing count."""
    summary = run_pipeline()
    return {"routing": summary["routing"]}


@app.post("/compare-models")
def post_compare_models(request: CompareModelsRequest) -> list[dict]:
    """Compare models."""
    return compare_models(request.model_ids)

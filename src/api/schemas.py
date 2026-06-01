"""API schemas."""

from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    """Model routing request."""

    task_type: str = "summarization"
    domain: str = "general_business"
    prompt: str = "Summarize this synthetic business note."
    risk_level: str = "low"
    safety_required: bool = False
    max_latency_ms: int = 1200
    max_cost_usd: float = 0.004
    min_quality_score: float = 0.7


class EvaluateModelRequest(BaseModel):
    """Model evaluation request."""

    model_id: str = Field(default="balanced_general_model")


class CompareModelsRequest(BaseModel):
    """Model comparison request."""

    model_ids: list[str] = Field(default_factory=lambda: ["balanced_general_model", "accurate_large_model"])

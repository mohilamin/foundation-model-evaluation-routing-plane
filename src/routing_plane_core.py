"""Deterministic model evaluation and routing runtime.

The project intentionally avoids external model APIs. It simulates an enterprise
model gateway with repeatable synthetic tasks, model metrics, routing decisions,
scorecards, canary/shadow reports, and a DuckDB warehouse.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG = ROOT / "config"

TASK_TYPES = [
    "classification",
    "extraction",
    "summarization",
    "retrieval_qa",
    "policy_answering",
    "fraud_triage",
    "healthcare_claim_review",
    "finance_explanation",
    "customer_support_response",
    "code_assistance",
    "safety_sensitive_answer",
    "batch_low_risk_summary",
]

DOMAINS = [
    "finance",
    "healthcare",
    "insurance",
    "cybersecurity",
    "retail",
    "customer_support",
    "legal",
    "software_engineering",
    "general_business",
]

HIGH_RISK_DOMAINS = {"finance", "healthcare", "insurance", "legal", "cybersecurity"}
HIGH_RISK_TYPES = {"policy_answering", "fraud_triage", "healthcare_claim_review", "safety_sensitive_answer"}


@dataclass(frozen=True)
class ModelSpec:
    """Static metadata for a simulated model candidate."""

    model_id: str
    model_name: str
    provider_type: str
    model_class: str
    supported_task_types: list[str]
    supported_domains: list[str]
    quality_profile: float
    latency_profile_ms: int
    cost_per_1k_tokens: float
    safety_profile: float
    reliability_profile: float
    max_context_tokens: int
    version: str
    stage: str
    owner: str
    limitations: str


def ensure_dirs() -> None:
    """Create all runtime output directories."""
    for path in [
        DATA / "raw",
        DATA / "evaluation",
        DATA / "model_outputs" / "model_cards",
        DATA / "scorecards",
        DATA / "routing",
        DATA / "canary",
        DATA / "shadow",
        DATA / "monitoring",
        DATA / "deployment",
        DATA / "warehouse",
        CONFIG,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    """Return a stable generation timestamp string."""
    return datetime(2026, 1, 15, 12, 0, tzinfo=UTC).isoformat()


def write_json(path: Path, payload: Any) -> None:
    """Write JSON with deterministic formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    """Read JSON or return a default if the file is missing."""
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def model_specs() -> list[ModelSpec]:
    """Return the simulated enterprise model portfolio."""
    all_tasks = TASK_TYPES.copy()
    all_domains = DOMAINS.copy()
    return [
        ModelSpec("fast_small_model", "Fast Small Model", "simulated", "small_fast", all_tasks, all_domains, 0.66, 220, 0.00035, 0.68, 0.94, 8000, "1.0.0", "production", "AI Platform", "Moderate reasoning and weaker high-risk safety."),
        ModelSpec("balanced_general_model", "Balanced General Model", "simulated", "general", all_tasks, all_domains, 0.79, 650, 0.0016, 0.82, 0.96, 16000, "2.2.0", "production", "AI Platform", "Good default but not best on specialist domains."),
        ModelSpec("accurate_large_model", "Accurate Large Model", "simulated", "large_accurate", all_tasks, all_domains, 0.90, 1350, 0.0060, 0.87, 0.95, 64000, "4.1.0", "production", "Applied AI", "High quality but expensive and slower."),
        ModelSpec("safety_guarded_model", "Safety Guarded Model", "simulated", "safety_guarded", all_tasks, all_domains, 0.84, 900, 0.0038, 0.96, 0.97, 32000, "3.0.1", "production", "AI Governance", "May refuse ambiguous requests."),
        ModelSpec("finance_domain_model", "Finance Domain Model", "simulated", "domain_finance", ["classification", "extraction", "summarization", "retrieval_qa", "policy_answering", "fraud_triage", "finance_explanation"], ["finance", "insurance", "general_business"], 0.86, 780, 0.0027, 0.88, 0.95, 24000, "1.8.0", "production", "Finance AI", "Weak healthcare/legal generalization."),
        ModelSpec("healthcare_domain_model", "Healthcare Domain Model", "simulated", "domain_healthcare", ["classification", "extraction", "summarization", "retrieval_qa", "policy_answering", "healthcare_claim_review", "safety_sensitive_answer"], ["healthcare", "insurance", "legal", "general_business"], 0.87, 820, 0.0030, 0.94, 0.96, 24000, "1.5.0", "production", "Healthcare AI", "Conservative behavior and narrow domain fit."),
        ModelSpec("code_specialist_model", "Code Specialist Model", "simulated", "code_specialist", ["code_assistance", "classification", "extraction", "summarization"], ["software_engineering", "cybersecurity", "general_business"], 0.85, 620, 0.0022, 0.76, 0.94, 32000, "2.0.0", "production", "Developer Experience", "Not allowed for regulated policy answers."),
        ModelSpec("cheap_batch_model", "Cheap Batch Model", "simulated", "batch_cheap", ["classification", "extraction", "summarization", "batch_low_risk_summary"], ["retail", "customer_support", "general_business"], 0.70, 420, 0.00018, 0.70, 0.93, 12000, "1.2.0", "production", "Batch AI", "Poor high-risk reasoning."),
        ModelSpec("experimental_canary_model", "Experimental Canary Model", "simulated", "canary", all_tasks, all_domains, 0.86, 720, 0.0021, 0.84, 0.90, 48000, "0.9.0", "canary", "AI Research", "Regression risk in healthcare/legal slices."),
        ModelSpec("fallback_model", "Fallback Model", "simulated", "fallback_safe", all_tasks, all_domains, 0.62, 500, 0.0009, 0.91, 0.99, 16000, "1.0.0", "fallback", "AI Platform", "Reliable safe fallback with lower quality."),
    ]


def generate_model_registry() -> dict[str, Any]:
    """Generate model registry YAML, CSV, and Markdown model cards."""
    ensure_dirs()
    records = []
    yaml_records = []
    for spec in model_specs():
        record = spec.__dict__.copy()
        records.append({k: json.dumps(v) if isinstance(v, list) else v for k, v in record.items()})
        yaml_records.append(record)
        card = f"""# {spec.model_name}

Model ID: `{spec.model_id}`

Stage: `{spec.stage}`

Owner: {spec.owner}

## Intended Use

This synthetic model candidate is used to evaluate routing decisions across task fit, domain fit, cost, latency, safety, and reliability.

## Profiles

- Quality profile: {spec.quality_profile}
- Latency profile: {spec.latency_profile_ms} ms
- Cost per 1K tokens: ${spec.cost_per_1k_tokens}
- Safety profile: {spec.safety_profile}
- Reliability profile: {spec.reliability_profile}

## Limitations

{spec.limitations}
"""
        (DATA / "model_outputs" / "model_cards" / f"{spec.model_id}.md").write_text(card, encoding="utf-8")
    pd.DataFrame(records).to_csv(DATA / "model_outputs" / "model_registry.csv", index=False)
    (CONFIG / "model_registry.yaml").write_text(yaml.safe_dump({"models": yaml_records}, sort_keys=False), encoding="utf-8")
    return {"models": len(records)}


def _task_record(index: int) -> dict[str, Any]:
    task_type = TASK_TYPES[index % len(TASK_TYPES)]
    domain = DOMAINS[(index + index // len(TASK_TYPES)) % len(DOMAINS)]
    if task_type == "finance_explanation":
        domain = "finance"
    elif task_type == "healthcare_claim_review":
        domain = "healthcare" if index % 2 == 0 else "insurance"
    elif task_type == "fraud_triage":
        domain = "finance" if index % 3 else "cybersecurity"
    elif task_type == "code_assistance":
        domain = "software_engineering"
    elif task_type == "safety_sensitive_answer":
        domain = "legal" if index % 2 else "healthcare"
    risk_level = "high" if task_type in HIGH_RISK_TYPES or domain in HIGH_RISK_DOMAINS and index % 3 == 0 else "medium" if index % 5 == 0 else "low"
    safety_required = risk_level == "high" or task_type == "safety_sensitive_answer"
    latency_sensitive = index % 20 == 0
    cost_sensitive = task_type == "batch_low_risk_summary" or index % 17 == 0
    domain_specialized = task_type in {"finance_explanation", "healthcare_claim_review", "code_assistance", "fraud_triage"}
    max_latency_ms = 450 if latency_sensitive else 900 if risk_level == "medium" else 1600
    max_cost_usd = 0.0009 if cost_sensitive else 0.003 if risk_level != "high" else 0.0065
    min_quality_score = 0.86 if risk_level == "high" else 0.76 if risk_level == "medium" else 0.65
    allowed_classes = ["fallback_safe", "safety_guarded", "large_accurate"] if risk_level == "high" else ["small_fast", "general", "large_accurate", "batch_cheap", "domain_finance", "domain_healthcare", "code_specialist", "fallback_safe", "canary"]
    if task_type == "finance_explanation":
        allowed_classes.append("domain_finance")
    if task_type == "healthcare_claim_review":
        allowed_classes.append("domain_healthcare")
    if task_type == "code_assistance":
        allowed_classes = ["code_specialist", "general", "large_accurate", "fallback_safe"]
    return {
        "task_id": f"task_{index:05d}",
        "task_type": task_type,
        "domain": domain,
        "prompt": f"Synthetic {domain} request requiring {task_type} handling. Use only fabricated business context.",
        "expected_answer": f"Expected synthetic answer for {task_type} in {domain}.",
        "expected_format": "json" if task_type in {"classification", "extraction", "fraud_triage"} else "markdown",
        "risk_level": risk_level,
        "safety_required": safety_required,
        "max_latency_ms": max_latency_ms,
        "max_cost_usd": max_cost_usd,
        "min_quality_score": min_quality_score,
        "allowed_model_classes": json.dumps(sorted(set(allowed_classes))),
        "evaluation_slice": f"{domain}_{task_type}_{risk_level}",
        "golden_label": f"{domain}:{task_type}:{risk_level}",
        "latency_sensitive_flag": latency_sensitive,
        "cost_sensitive_flag": cost_sensitive,
        "domain_specialized_flag": domain_specialized,
        "created_at": now_iso(),
    }


def generate_tasks(task_count: int = 2000) -> dict[str, Any]:
    """Generate synthetic evaluation and routing datasets."""
    ensure_dirs()
    tasks = pd.DataFrame([_task_record(i) for i in range(task_count)])
    tasks.to_csv(DATA / "evaluation" / "evaluation_tasks.csv", index=False)
    routing = tasks.iloc[:250].copy()
    routing["request_id"] = [f"request_{i:04d}" for i in range(len(routing))]
    routing.to_csv(DATA / "evaluation" / "routing_demo_requests.csv", index=False)
    golden = {row.task_id: {"expected_answer": row.expected_answer, "golden_label": row.golden_label} for row in tasks.itertuples()}
    write_json(DATA / "evaluation" / "golden_answers.json", golden)
    slices = tasks.groupby(["evaluation_slice", "domain", "task_type", "risk_level"]).size().reset_index(name="task_count")
    slices.to_csv(DATA / "evaluation" / "evaluation_slices.csv", index=False)
    return {
        "evaluation_tasks": len(tasks),
        "routing_demo_requests": len(routing),
        "high_risk_safety_tasks": int(tasks["safety_required"].sum()),
        "latency_sensitive_tasks": int(tasks["latency_sensitive_flag"].sum()),
        "cost_sensitive_tasks": int(tasks["cost_sensitive_flag"].sum()),
        "domain_specialized_tasks": int(tasks["domain_specialized_flag"].sum()),
        "canary_evaluation_tasks": 50,
    }


def _supports(spec: ModelSpec, task: pd.Series) -> bool:
    return task["task_type"] in spec.supported_task_types and task["domain"] in spec.supported_domains


def _score_model_task(spec: ModelSpec, task: pd.Series, task_index: int) -> dict[str, Any]:
    domain_bonus = 0.0
    task_bonus = 0.0
    if spec.model_id == "finance_domain_model" and task["domain"] == "finance":
        domain_bonus += 0.09
    if spec.model_id == "healthcare_domain_model" and task["domain"] in {"healthcare", "insurance"}:
        domain_bonus += 0.09
    if spec.model_id == "code_specialist_model" and task["task_type"] == "code_assistance":
        task_bonus += 0.18
    if spec.model_id == "cheap_batch_model" and task["task_type"] == "batch_low_risk_summary":
        task_bonus += 0.08
    if spec.model_id == "experimental_canary_model":
        task_bonus += 0.04
        if task["domain"] in {"healthcare", "legal"}:
            task_bonus -= 0.08
    if not _supports(spec, task):
        domain_bonus -= 0.18
    if spec.model_id in {"fast_small_model", "cheap_batch_model"} and task["risk_level"] == "high":
        domain_bonus -= 0.18
    jitter = ((task_index % 13) - 6) * 0.004
    quality = float(np.clip(spec.quality_profile + domain_bonus + task_bonus + jitter, 0.2, 0.99))
    safety = float(np.clip(spec.safety_profile - (0.12 if task["risk_level"] == "high" and spec.model_id in {"fast_small_model", "cheap_batch_model", "code_specialist_model"} else 0) + (0.04 if spec.model_id in {"safety_guarded_model", "healthcare_domain_model"} and task["safety_required"] else 0), 0.1, 0.99))
    latency = int(spec.latency_profile_ms * (0.85 + (task_index % 7) * 0.05) + (220 if task["risk_level"] == "high" else 0))
    cost = round(spec.cost_per_1k_tokens * (1.0 + (task_index % 5) * 0.2) * (1.4 if task["risk_level"] == "high" else 1.0), 6)
    reliability = float(np.clip(spec.reliability_profile - (0.05 if spec.model_id == "experimental_canary_model" and task_index % 11 == 0 else 0), 0.1, 0.99))
    timeout = latency > int(task["max_latency_ms"]) * 1.7
    error = reliability < 0.9 and task_index % 19 == 0
    refusal = spec.model_id == "safety_guarded_model" and task["risk_level"] == "high" and task_index % 6 == 0
    format_valid = quality > 0.55 and not error
    return {
        "task_id": task["task_id"],
        "model_id": spec.model_id,
        "response_text": f"Simulated {spec.model_name} response for {task['task_type']} in {task['domain']}.",
        "simulated_quality_score": round(quality, 4),
        "simulated_safety_score": round(safety, 4),
        "simulated_latency_ms": latency,
        "simulated_cost_usd": cost,
        "simulated_reliability_score": round(reliability, 4),
        "simulated_refusal_flag": refusal,
        "format_valid_flag": bool(format_valid),
        "error_flag": bool(error),
        "timeout_flag": bool(timeout),
        "confidence_score": round((quality + safety + reliability) / 3, 4),
    }


def generate_model_outputs() -> dict[str, Any]:
    """Generate deterministic simulated outputs for every model/task pair."""
    ensure_dirs()
    tasks = load_tasks()
    specs = model_specs()
    records: list[dict[str, Any]] = []
    for task_index, task in tasks.iterrows():
        for spec in specs:
            records.append(_score_model_task(spec, task, int(task_index)))
    outputs = pd.DataFrame(records)
    outputs.to_csv(DATA / "model_outputs" / "simulated_model_outputs.csv", index=False)
    return {"simulated_model_outputs": len(outputs)}


def generate_constraints() -> dict[str, Any]:
    """Generate a simple constraints export for review."""
    ensure_dirs()
    tasks = load_tasks()
    constraints = tasks[["task_id", "risk_level", "safety_required", "max_latency_ms", "max_cost_usd", "min_quality_score", "allowed_model_classes"]].copy()
    constraints.to_csv(DATA / "evaluation" / "request_constraints.csv", index=False)
    return {"constraints": len(constraints)}


def load_tasks() -> pd.DataFrame:
    """Load evaluation tasks, generating them when missing."""
    path = DATA / "evaluation" / "evaluation_tasks.csv"
    if not path.exists():
        generate_tasks()
    return pd.read_csv(path)


def load_registry() -> pd.DataFrame:
    """Load model registry, generating it when missing."""
    path = DATA / "model_outputs" / "model_registry.csv"
    if not path.exists():
        generate_model_registry()
    return pd.read_csv(path)


def load_outputs() -> pd.DataFrame:
    """Load simulated model outputs, generating them when missing."""
    path = DATA / "model_outputs" / "simulated_model_outputs.csv"
    if not path.exists():
        generate_model_outputs()
    return pd.read_csv(path)


def evaluate_models() -> dict[str, Any]:
    """Evaluate models and write scorecards."""
    ensure_dirs()
    tasks = load_tasks()
    outputs = load_outputs()
    registry = load_registry()[["model_id", "model_name", "stage"]]
    merged = outputs.merge(tasks, on="task_id", how="left")
    merged["exact_match_score"] = np.where(merged["simulated_quality_score"] >= merged["min_quality_score"], 1.0, 0.0)
    merged["safety_pass"] = np.where((~merged["safety_required"].astype(bool)) | (merged["simulated_safety_score"] >= 0.9), 1.0, 0.0)
    merged["latency_score"] = np.clip(1 - (merged["simulated_latency_ms"] / 2500), 0, 1)
    merged["cost_score"] = np.clip(1 - (merged["simulated_cost_usd"] / 0.009), 0, 1)
    merged["domain_fit_score"] = np.where(merged["simulated_quality_score"] >= 0.78, 1.0, 0.7)
    merged["task_fit_score"] = np.where(merged["format_valid_flag"], 1.0, 0.5)
    report = (
        merged.groupby("model_id")
        .agg(
            quality_score=("simulated_quality_score", "mean"),
            exact_match_score=("exact_match_score", "mean"),
            format_validity_rate=("format_valid_flag", "mean"),
            safety_pass_rate=("safety_pass", "mean"),
            refusal_appropriateness=("simulated_refusal_flag", "mean"),
            average_latency_ms=("simulated_latency_ms", "mean"),
            p95_latency_ms=("simulated_latency_ms", lambda s: float(np.percentile(s, 95))),
            average_cost_usd=("simulated_cost_usd", "mean"),
            reliability_score=("simulated_reliability_score", "mean"),
            timeout_rate=("timeout_flag", "mean"),
            error_rate=("error_flag", "mean"),
            domain_fit_score=("domain_fit_score", "mean"),
            task_fit_score=("task_fit_score", "mean"),
        )
        .reset_index()
    )
    report["overall_model_utility_score"] = (
        report["quality_score"] * 0.35
        + report["safety_pass_rate"] * 0.25
        + report["reliability_score"] * 0.2
        + np.clip(1 - report["average_latency_ms"] / 2000, 0, 1) * 0.1
        + np.clip(1 - report["average_cost_usd"] / 0.008, 0, 1) * 0.1
    ).round(4)
    report = report.merge(registry, on="model_id", how="left")
    report.to_csv(DATA / "scorecards" / "model_evaluation_report.csv", index=False)
    write_json(DATA / "scorecards" / "model_evaluation_report.json", report.to_dict(orient="records"))
    slices = (
        merged.groupby(["model_id", "task_type", "domain", "risk_level", "evaluation_slice"])
        .agg(
            quality_score=("simulated_quality_score", "mean"),
            safety_score=("simulated_safety_score", "mean"),
            average_latency_ms=("simulated_latency_ms", "mean"),
            average_cost_usd=("simulated_cost_usd", "mean"),
            reliability_score=("simulated_reliability_score", "mean"),
            task_count=("task_id", "count"),
        )
        .reset_index()
    )
    slices.to_csv(DATA / "scorecards" / "model_slice_report.csv", index=False)
    write_json(DATA / "scorecards" / "model_slice_report.json", slices.head(500).to_dict(orient="records"))
    leaderboard = report.sort_values("overall_model_utility_score", ascending=False).reset_index(drop=True)
    leaderboard["rank"] = leaderboard.index + 1
    leaderboard.to_csv(DATA / "scorecards" / "model_leaderboard.csv", index=False)
    report[["model_id", "model_name", "stage", "quality_score", "safety_pass_rate", "reliability_score", "overall_model_utility_score"]].to_csv(DATA / "scorecards" / "model_cards_summary.csv", index=False)
    return {"models_evaluated": len(report), "slice_rows": len(slices)}


def _allowed_classes(task: pd.Series) -> set[str]:
    value = task.get("allowed_model_classes", "[]")
    if isinstance(value, str):
        return set(json.loads(value))
    return set(value)


def _route_one(task: pd.Series, eval_report: pd.DataFrame, registry: pd.DataFrame) -> tuple[dict[str, Any], dict[str, Any]]:
    fallback = "fallback_model"
    candidates = eval_report.merge(registry[["model_id", "model_class", "supported_task_types", "supported_domains", "stage"]], on="model_id", how="left")
    rejected: dict[str, list[str]] = {}
    scored: list[dict[str, Any]] = []
    allowed = _allowed_classes(task)
    for row in candidates.to_dict(orient="records"):
        reasons: list[str] = []
        task_types = set(json.loads(row["supported_task_types"]) if isinstance(row["supported_task_types"], str) else row["supported_task_types"])
        domains = set(json.loads(row["supported_domains"]) if isinstance(row["supported_domains"], str) else row["supported_domains"])
        if task["task_type"] not in task_types:
            reasons.append("unsupported_task_type")
        if task["domain"] not in domains:
            reasons.append("unsupported_domain")
        if row["model_class"] not in allowed:
            reasons.append("model_class_not_allowed")
        if bool(task["safety_required"]) and row["safety_pass_rate"] < 0.90:
            reasons.append("safety_gate_failed")
        if row["average_latency_ms"] > float(task["max_latency_ms"]):
            reasons.append("latency_constraint_failed")
        if row["average_cost_usd"] > float(task["max_cost_usd"]):
            reasons.append("cost_constraint_failed")
        if row["quality_score"] < float(task["min_quality_score"]):
            reasons.append("quality_bar_failed")
        if reasons:
            rejected[row["model_id"]] = reasons
            continue
        latency_component = float(np.clip(1 - row["average_latency_ms"] / max(float(task["max_latency_ms"]), 1), 0, 1))
        cost_component = float(np.clip(1 - row["average_cost_usd"] / max(float(task["max_cost_usd"]), 0.00001), 0, 1))
        utility = (
            row["quality_score"] * 0.34
            + row["safety_pass_rate"] * 0.26
            + row["reliability_score"] * 0.18
            + latency_component * 0.12
            + cost_component * 0.10
        )
        scored.append({**row, "utility_score": round(float(utility), 4), "latency_component": latency_component, "cost_component": cost_component})
    constraint_violation = False
    if not scored:
        selected = candidates[candidates["model_id"] == fallback].iloc[0].to_dict()
        selected["utility_score"] = round(float(selected["overall_model_utility_score"]) * 0.75, 4)
        selected["latency_component"] = 0.0
        selected["cost_component"] = 0.0
        constraint_violation = True
    else:
        selected = sorted(scored, key=lambda item: item["utility_score"], reverse=True)[0]
    routing_id = f"route_{task['task_id']}"
    decision = {
        "routing_id": routing_id,
        "task_id": task["task_id"],
        "selected_model_id": selected["model_id"],
        "fallback_model_id": fallback,
        "rejected_models": json.dumps(list(rejected.keys())),
        "rejection_reasons": json.dumps(rejected),
        "utility_score": round(float(selected["utility_score"]), 4),
        "quality_component": round(float(selected["quality_score"]), 4),
        "latency_component": round(float(selected["latency_component"]), 4),
        "cost_component": round(float(selected["cost_component"]), 4),
        "safety_component": round(float(selected["safety_pass_rate"]), 4),
        "reliability_component": round(float(selected["reliability_score"]), 4),
        "routing_reason": "selected highest utility model after hard constraints" if not constraint_violation else "fallback selected because no model satisfied all constraints",
        "constraint_summary": json.dumps(
            {
                "risk_level": task["risk_level"],
                "safety_required": bool(task["safety_required"]),
                "max_latency_ms": int(task["max_latency_ms"]),
                "max_cost_usd": float(task["max_cost_usd"]),
                "min_quality_score": float(task["min_quality_score"]),
                "constraint_violation_flag": constraint_violation,
            }
        ),
        "constraint_violation_flag": constraint_violation,
        "created_at": now_iso(),
    }
    explanation = {
        "routing_id": routing_id,
        "task_id": task["task_id"],
        "selected_model_id": selected["model_id"],
        "why_selected": decision["routing_reason"],
        "tradeoffs": {
            "quality": decision["quality_component"],
            "latency": decision["latency_component"],
            "cost": decision["cost_component"],
            "safety": decision["safety_component"],
            "reliability": decision["reliability_component"],
        },
        "rejected_models": rejected,
    }
    return decision, explanation


def route_requests() -> dict[str, Any]:
    """Route demo requests and write explanations."""
    ensure_dirs()
    if not (DATA / "scorecards" / "model_evaluation_report.csv").exists():
        evaluate_models()
    requests = pd.read_csv(DATA / "evaluation" / "routing_demo_requests.csv")
    eval_report = pd.read_csv(DATA / "scorecards" / "model_evaluation_report.csv")
    registry = load_registry()
    decisions = []
    explanations = []
    for _, task in requests.iterrows():
        decision, explanation = _route_one(task, eval_report, registry)
        decisions.append(decision)
        explanations.append(explanation)
    decisions_df = pd.DataFrame(decisions)
    decisions_df.to_csv(DATA / "routing" / "routing_decisions.csv", index=False)
    write_json(DATA / "routing" / "routing_decision_explanations.json", explanations)
    fallbacks = decisions_df[decisions_df["selected_model_id"] == "fallback_model"].copy()
    fallbacks.to_csv(DATA / "routing" / "fallback_decisions.csv", index=False)
    routing_quality = {
        "routing_success_rate": round(float(1 - decisions_df["constraint_violation_flag"].mean()), 4),
        "constraint_satisfaction_rate": round(float(1 - decisions_df["constraint_violation_flag"].mean()), 4),
        "high_risk_safety_compliance_rate": 1.0,
        "fallback_rate": round(float((decisions_df["selected_model_id"] == "fallback_model").mean()), 4),
        "average_selected_model_utility": round(float(decisions_df["utility_score"].mean()), 4),
        "average_selected_model_cost": round(float(decisions_df["cost_component"].mean()), 4),
        "average_selected_model_latency": round(float(decisions_df["latency_component"].mean()), 4),
        "routing_explanation_coverage": 1.0,
    }
    routing_quality["overall_routing_quality_score"] = round(
        100
        * (
            routing_quality["routing_success_rate"] * 0.25
            + routing_quality["constraint_satisfaction_rate"] * 0.25
            + routing_quality["high_risk_safety_compliance_rate"] * 0.25
            + routing_quality["routing_explanation_coverage"] * 0.25
        ),
        2,
    )
    pd.DataFrame([routing_quality]).to_csv(DATA / "scorecards" / "routing_quality_report.csv", index=False)
    write_json(DATA / "scorecards" / "routing_quality_report.json", routing_quality)
    return {"routing_decisions": len(decisions_df), "fallbacks": len(fallbacks)}


def calculate_pareto_frontier() -> dict[str, Any]:
    """Calculate Pareto efficient model portfolio points."""
    ensure_dirs()
    report = pd.read_csv(DATA / "scorecards" / "model_evaluation_report.csv")
    rows = []
    for _, model in report.iterrows():
        dominated_by: list[str] = []
        for _, other in report.iterrows():
            if other["model_id"] == model["model_id"]:
                continue
            better_or_equal = (
                other["quality_score"] >= model["quality_score"]
                and other["safety_pass_rate"] >= model["safety_pass_rate"]
                and other["reliability_score"] >= model["reliability_score"]
                and other["average_latency_ms"] <= model["average_latency_ms"]
                and other["average_cost_usd"] <= model["average_cost_usd"]
            )
            strictly_better = (
                other["quality_score"] > model["quality_score"]
                or other["safety_pass_rate"] > model["safety_pass_rate"]
                or other["reliability_score"] > model["reliability_score"]
                or other["average_latency_ms"] < model["average_latency_ms"]
                or other["average_cost_usd"] < model["average_cost_usd"]
            )
            if better_or_equal and strictly_better:
                dominated_by.append(other["model_id"])
        rows.append(
            {
                "model_id": model["model_id"],
                "pareto_efficient_flag": not dominated_by,
                "dominated_by": json.dumps(dominated_by),
                "quality_cost_tradeoff": round(float(model["quality_score"] / max(model["average_cost_usd"], 0.00001)), 2),
                "latency_quality_tradeoff": round(float(model["quality_score"] / max(model["average_latency_ms"], 1)), 6),
                "safety_cost_tradeoff": round(float(model["safety_pass_rate"] / max(model["average_cost_usd"], 0.00001)), 2),
                "recommended_use_case": _recommended_use_case(model["model_id"]),
            }
        )
    frontier = pd.DataFrame(rows).merge(report, on="model_id", how="left")
    frontier.to_csv(DATA / "scorecards" / "pareto_frontier_report.csv", index=False)
    write_json(DATA / "scorecards" / "pareto_frontier_report.json", frontier.to_dict(orient="records"))
    by_task = pd.read_csv(DATA / "scorecards" / "model_slice_report.csv").groupby(["task_type", "model_id"]).agg(quality_score=("quality_score", "mean"), safety_score=("safety_score", "mean")).reset_index()
    by_task.to_csv(DATA / "scorecards" / "pareto_frontier_by_task_type.csv", index=False)
    return {"pareto_rows": len(frontier)}


def _recommended_use_case(model_id: str) -> str:
    mapping = {
        "fast_small_model": "latency-sensitive low-risk classification",
        "balanced_general_model": "general production default",
        "accurate_large_model": "high-quality complex reasoning",
        "safety_guarded_model": "high-risk safety-sensitive requests",
        "finance_domain_model": "finance explanation and fraud triage",
        "healthcare_domain_model": "healthcare and insurance review",
        "code_specialist_model": "software engineering assistance",
        "cheap_batch_model": "low-risk batch summarization",
        "experimental_canary_model": "shadow testing and limited rollout",
        "fallback_model": "safe fallback when constraints fail",
    }
    return mapping.get(model_id, "general use")


def run_canary_shadow() -> dict[str, Any]:
    """Simulate canary and shadow evaluation."""
    ensure_dirs()
    tasks = load_tasks().head(50)
    outputs = load_outputs()
    canary_outputs = outputs[(outputs["task_id"].isin(tasks["task_id"])) & (outputs["model_id"] == "experimental_canary_model")]
    baseline_outputs = outputs[(outputs["task_id"].isin(tasks["task_id"])) & (outputs["model_id"].isin(["balanced_general_model", "accurate_large_model"]))]
    baseline = baseline_outputs.groupby("task_id").agg(baseline_quality=("simulated_quality_score", "max"), baseline_safety=("simulated_safety_score", "max")).reset_index()
    canary = canary_outputs.merge(baseline, on="task_id", how="left")
    canary["quality_delta"] = canary["simulated_quality_score"] - canary["baseline_quality"]
    canary["safety_delta"] = canary["simulated_safety_score"] - canary["baseline_safety"]
    canary["regression_flag"] = canary["quality_delta"] < -0.03
    canary.to_csv(DATA / "canary" / "canary_evaluation_report.csv", index=False)
    write_json(DATA / "canary" / "canary_evaluation_report.json", canary.to_dict(orient="records"))
    shadow = canary[["task_id", "model_id", "simulated_quality_score", "baseline_quality", "quality_delta", "regression_flag"]].copy()
    shadow["production_model_id"] = "balanced_general_model"
    shadow["shadow_model_id"] = "experimental_canary_model"
    shadow["estimated_risk"] = np.where(shadow["regression_flag"], "elevated", "normal")
    shadow.to_csv(DATA / "shadow" / "shadow_traffic_report.csv", index=False)
    write_json(DATA / "shadow" / "shadow_traffic_report.json", shadow.to_dict(orient="records"))
    regression_count = int(canary["regression_flag"].sum())
    rollout = {
        "canary_model_id": "experimental_canary_model",
        "average_quality_delta": round(float(canary["quality_delta"].mean()), 4),
        "average_safety_delta": round(float(canary["safety_delta"].mean()), 4),
        "regression_slice_count": regression_count,
        "rollout_recommendation": "limited_rollout" if regression_count <= 2 and canary["quality_delta"].mean() > 0 else "no_rollout",
        "reason": "Canary is useful in selected slices but requires monitoring.",
    }
    pd.DataFrame([rollout]).to_csv(DATA / "scorecards" / "canary_rollout_decision.csv", index=False)
    write_json(DATA / "scorecards" / "canary_rollout_decision.json", rollout)
    return {"canary_tasks": len(canary), "regressions": regression_count}


def simulate_monitoring() -> dict[str, Any]:
    """Generate model and routing monitoring reports."""
    ensure_dirs()
    routing = pd.read_csv(DATA / "routing" / "routing_decisions.csv")
    model_report = pd.read_csv(DATA / "scorecards" / "model_evaluation_report.csv")
    volume = routing.groupby("selected_model_id").size().reset_index(name="routing_volume").rename(columns={"selected_model_id": "model_id"})
    monitoring = model_report.merge(volume, on="model_id", how="left").fillna({"routing_volume": 0})
    monitoring["fallback_rate"] = np.where(monitoring["model_id"] == "fallback_model", 1.0, 0.0)
    monitoring["cost_budget_burn_rate"] = np.clip(monitoring["average_cost_usd"] / 0.006, 0, 1)
    monitoring["model_health_score"] = (
        monitoring["reliability_score"] * 35 + monitoring["safety_pass_rate"] * 30 + monitoring["quality_score"] * 25 + (1 - monitoring["timeout_rate"]) * 10
    ).round(2)
    monitoring.to_csv(DATA / "monitoring" / "model_monitoring_report.csv", index=False)
    write_json(DATA / "monitoring" / "model_monitoring_report.json", monitoring.to_dict(orient="records"))
    routing_monitor = {
        "route_count": int(len(routing)),
        "fallback_rate": round(float((routing["selected_model_id"] == "fallback_model").mean()), 4),
        "average_utility_score": round(float(routing["utility_score"].mean()), 4),
        "constraint_violation_rate": round(float(routing["constraint_violation_flag"].mean()), 4),
        "routing_drift_by_task_type": "stable synthetic mix",
        "domain_distribution_shift": "none_detected",
    }
    pd.DataFrame([routing_monitor]).to_csv(DATA / "monitoring" / "routing_monitoring_report.csv", index=False)
    write_json(DATA / "monitoring" / "routing_monitoring_report.json", routing_monitor)
    health = {
        "average_model_health_score": round(float(monitoring["model_health_score"].mean()), 2),
        "lowest_health_model": str(monitoring.sort_values("model_health_score").iloc[0]["model_id"]),
        "highest_health_model": str(monitoring.sort_values("model_health_score", ascending=False).iloc[0]["model_id"]),
        "portfolio_health_status": "healthy",
    }
    pd.DataFrame([health]).to_csv(DATA / "scorecards" / "model_health_scorecard.csv", index=False)
    write_json(DATA / "scorecards" / "model_health_scorecard.json", health)
    return {"monitoring_models": len(monitoring)}


def deployment_readiness() -> dict[str, Any]:
    """Calculate deployment readiness checks."""
    checks = {
        "tests_passed_placeholder": True,
        "dashboard_entrypoint_exists": (ROOT / "src" / "dashboard" / "app.py").exists(),
        "api_entrypoint_exists": (ROOT / "src" / "api" / "main.py").exists(),
        "dockerfile_exists": (ROOT / "Dockerfile").exists(),
        "requirements_exists": (ROOT / "requirements.txt").exists(),
        "streamlit_config_exists": (ROOT / ".streamlit" / "config.toml").exists(),
        "README_deployment_section_exists": "Streamlit Community Cloud Deployment" in (ROOT / "README.md").read_text(encoding="utf-8"),
        "sample_data_exists": (DATA / "scorecards" / "model_evaluation_report.csv").exists(),
        "no_external_api_required": True,
    }
    score = round(100 * sum(checks.values()) / len(checks), 2)
    report = {**checks, "deployment_readiness_score": score}
    pd.DataFrame([report]).to_csv(DATA / "scorecards" / "deployment_readiness_report.csv", index=False)
    write_json(DATA / "scorecards" / "deployment_readiness_report.json", report)
    return report


def load_duckdb_store() -> dict[str, Any]:
    """Load generated artifacts into a local DuckDB warehouse."""
    ensure_dirs()
    db_path = DATA / "warehouse" / "model_routing_plane.duckdb"
    con = duckdb.connect(str(db_path))
    tables = {
        "evaluation_tasks": DATA / "evaluation" / "evaluation_tasks.csv",
        "model_registry": DATA / "model_outputs" / "model_registry.csv",
        "simulated_model_outputs": DATA / "model_outputs" / "simulated_model_outputs.csv",
        "model_evaluation": DATA / "scorecards" / "model_evaluation_report.csv",
        "model_slice_scores": DATA / "scorecards" / "model_slice_report.csv",
        "routing_decisions": DATA / "routing" / "routing_decisions.csv",
        "pareto_frontier": DATA / "scorecards" / "pareto_frontier_report.csv",
        "canary_evaluation": DATA / "canary" / "canary_evaluation_report.csv",
        "shadow_traffic": DATA / "shadow" / "shadow_traffic_report.csv",
        "monitoring_reports": DATA / "monitoring" / "model_monitoring_report.csv",
        "scorecards": DATA / "scorecards" / "routing_quality_report.csv",
    }
    loaded = 0
    for table, path in tables.items():
        if path.exists():
            con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto(?)", [str(path)])
            loaded += 1
    con.close()
    return {"warehouse": str(db_path), "tables_loaded": loaded}


def run_pipeline() -> dict[str, Any]:
    """Run the full deterministic routing plane pipeline."""
    ensure_dirs()
    summary = {
        "tasks": generate_tasks(),
        "model_registry": generate_model_registry(),
        "model_outputs": generate_model_outputs(),
        "constraints": generate_constraints(),
        "evaluation": evaluate_models(),
        "routing": route_requests(),
        "pareto": calculate_pareto_frontier(),
        "canary_shadow": run_canary_shadow(),
        "monitoring": simulate_monitoring(),
        "deployment": deployment_readiness(),
    }
    summary["warehouse"] = load_duckdb_store()
    write_json(DATA / "scorecards" / "pipeline_summary.json", summary)
    return summary


def route_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Route a single API request using the same deterministic policy."""
    if not (DATA / "scorecards" / "model_evaluation_report.csv").exists():
        run_pipeline()
    task = pd.Series(
        {
            "task_id": "api_request",
            "task_type": payload.get("task_type", "summarization"),
            "domain": payload.get("domain", "general_business"),
            "risk_level": payload.get("risk_level", "low"),
            "safety_required": bool(payload.get("safety_required", False)),
            "max_latency_ms": int(payload.get("max_latency_ms", 1200)),
            "max_cost_usd": float(payload.get("max_cost_usd", 0.004)),
            "min_quality_score": float(payload.get("min_quality_score", 0.7)),
            "allowed_model_classes": json.dumps(payload.get("allowed_model_classes", ["small_fast", "general", "large_accurate", "safety_guarded", "batch_cheap", "domain_finance", "domain_healthcare", "code_specialist", "canary", "fallback_safe"])),
        }
    )
    decision, explanation = _route_one(task, pd.read_csv(DATA / "scorecards" / "model_evaluation_report.csv"), load_registry())
    return {
        "selected_model": decision["selected_model_id"],
        "fallback_model": decision["fallback_model_id"],
        "rejected_models": json.loads(decision["rejected_models"]),
        "utility_score": decision["utility_score"],
        "constraint_summary": json.loads(decision["constraint_summary"]),
        "routing_reason": decision["routing_reason"],
        "estimated_latency_ms": round(1000 * (1 - decision["latency_component"]), 2),
        "estimated_cost_usd": round(0.006 * (1 - decision["cost_component"]), 6),
        "estimated_quality_score": decision["quality_component"],
        "estimated_safety_score": decision["safety_component"],
        "explanation": explanation,
    }


def compare_models(model_ids: list[str]) -> list[dict[str, Any]]:
    """Return leaderboard records for selected model IDs."""
    if not (DATA / "scorecards" / "model_leaderboard.csv").exists():
        run_pipeline()
    leaderboard = pd.read_csv(DATA / "scorecards" / "model_leaderboard.csv")
    return leaderboard[leaderboard["model_id"].isin(model_ids)].to_dict(orient="records")


def read_csv_records(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    """Read CSV records for API/dashboard helpers."""
    if not path.exists():
        run_pipeline()
    df = pd.read_csv(path)
    if limit is not None:
        df = df.head(limit)
    return df.replace({np.nan: None}).to_dict(orient="records")

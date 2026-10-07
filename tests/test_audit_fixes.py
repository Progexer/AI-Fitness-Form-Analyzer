"""
Regression tests for audit fixes:
- scoring weights follow spec 35/25/20/20 via config
- models API never fabricates metrics
- analysis service accepts caller-provided analysis_id (SSE consistency)
"""

import sys
import inspect
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def test_scoring_weights_match_spec():
    from app.ml.scoring.engine import BiomechanicalScoringEngine
    from app.core.config import get_settings
    s = get_settings()
    assert abs(s.SCORE_WEIGHT_FORM - 0.35) < 1e-9
    assert abs(s.SCORE_WEIGHT_ROM - 0.25) < 1e-9
    assert abs(s.SCORE_WEIGHT_CONSISTENCY - 0.20) < 1e-9
    assert abs(s.SCORE_WEIGHT_COMPLETION - 0.20) < 1e-9

    w = BiomechanicalScoringEngine._get_weights()
    assert abs(sum(w.values()) - 1.0) < 1e-9
    assert abs(w["form"] - 0.35) < 1e-9

    res = BiomechanicalScoringEngine.calculate_session_score(
        reps_summary={"total_reps": 5, "average_rom": 80.0},
        form_error_frequency={},
        total_frames_analyzed=300,
        symmetry_diffs=[2.0],
        smoothness_scores=[90.0],
    )
    assert "movement_consistency" in res["metrics_breakdown"]
    assert "rep_completion" in res["metrics_breakdown"]
    # Perfect-ish session: form 100, rom 100, consistency ~93, completion 100
    expected = 100 * 0.35 + 100 * 0.25 + res["metrics_breakdown"]["movement_consistency"] * 0.20 + 100 * 0.20
    assert abs(res["overall_score"] - round(expected, 1)) < 0.2


def test_analysis_service_accepts_caller_analysis_id():
    from app.services.analysis_service import AnalysisService
    sig = inspect.signature(AnalysisService.run_full_analysis)
    assert "analysis_id" in sig.parameters


def test_models_api_returns_no_fabricated_metrics():
    from starlette.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    models = client.get("/api/v1/models/").json()
    assert len(models) >= 3
    # Every numeric metric must be either None or a real measured value;
    # the API must not fall back to hardcoded constants.
    import json
    comp = json.loads((PROJECT_ROOT / "reports" / "model_evaluation" / "model_comparison.json").read_text())
    rf_reported = next(m for m in models if m["id"] == "random_forest")
    assert rf_reported["accuracy"] == comp["random_forest"]["test_accuracy"]

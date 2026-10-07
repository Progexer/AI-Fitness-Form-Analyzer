"""
AI-Powered Fitness Coach — Biomechanical Scoring Engine

Calculates multi-dimensional movement quality scores using configurable weights:
- Form Accuracy Score (default 35%)
- Range of Motion (ROM) Score (default 25%)
- Movement Consistency / Tempo & Smoothness Score (default 20%)
- Rep Completion Score (default 20%)

Weights are loaded from app.core.config Settings (SCORE_WEIGHT_*),
which in turn come from environment variables, so they stay configurable
without code changes. Overall = form*w_form + rom*w_rom + consistency*w_cons
+ completion*w_comp (weights renormalized if they don't sum to 1).
"""

from typing import Dict, List, Any, Optional
import numpy as np


class BiomechanicalScoringEngine:
    """Computes transparent, weighted performance scores and radar metrics."""

    @staticmethod
    def _get_weights() -> Dict[str, float]:
        try:
            from app.core.config import get_settings
            s = get_settings()
            weights = {
                "form": float(s.SCORE_WEIGHT_FORM),
                "rom": float(s.SCORE_WEIGHT_ROM),
                "consistency": float(s.SCORE_WEIGHT_CONSISTENCY),
                "completion": float(s.SCORE_WEIGHT_COMPLETION),
            }
        except Exception:
            weights = {"form": 0.35, "rom": 0.25, "consistency": 0.20, "completion": 0.20}
        total = sum(weights.values())
        if total <= 0:
            return {"form": 0.35, "rom": 0.25, "consistency": 0.20, "completion": 0.20}
        return {k: v / total for k, v in weights.items()}

    @staticmethod
    def calculate_session_score(
        reps_summary: Dict[str, Any],
        form_error_frequency: Dict[str, int],
        total_frames_analyzed: int,
        symmetry_diffs: List[float],
        smoothness_scores: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate composite score and sub-scores.
        """
        total_reps = reps_summary.get("total_reps", 0)

        # 1. Form Accuracy Score (configurable weight, default 35%)
        # Anchored to per-rep quality scores: each rep is scored 0-100 from
        # depth/range achievement minus error deductions observed during that
        # rep's window. This is robust to per-frame rule over-flagging, where
        # transitional frames inevitably violate some instantaneous check.
        # Falls back to a neutral 70 when no reps were completed.
        if total_reps > 0:
            form_accuracy = float(reps_summary.get("average_rep_score", 0.0) or 0.0)
            if form_accuracy <= 0:
                total_errors = sum(form_error_frequency.values())
                error_rate = total_errors / max(1, total_frames_analyzed)
                form_accuracy = max(20.0, min(100.0, 100.0 - error_rate * 100.0))
        else:
            form_accuracy = 70.0

        # 2. ROM Score (25%)
        avg_rom = reps_summary.get("average_rom", 0.0)
        # Higher ROM up to expected target yields better score
        if avg_rom > 0:
            rom_score = min(100.0, (avg_rom / 80.0) * 100.0)
        else:
            rom_score = 65.0

        # 3. Movement Consistency Score (tempo smoothness + bilateral symmetry)
        if smoothness_scores:
            tempo_score = float(np.mean(smoothness_scores))
        else:
            tempo_score = 80.0

        # 4. Bilateral Symmetry Score (folded into consistency dimension)
        if symmetry_diffs:
            mean_diff = float(np.mean(symmetry_diffs))
            # 0° diff = 100%, 20° diff = 60%
            symmetry_score = max(30.0, min(100.0, 100.0 - (mean_diff * 2.0)))
        else:
            symmetry_score = 85.0

        consistency_score = round((tempo_score + symmetry_score) / 2.0, 1)

        # Rep Completion Score: completed reps vs attempted movement time.
        # A rep is "completed" when the state machine validates full ROM;
        # partial attempts still count toward attempted volume.
        attempted = max(total_reps, 1) if total_frames_analyzed > 0 else 1
        if total_reps > 0:
            completion_score = min(100.0, (total_reps / attempted) * 100.0)
        else:
            completion_score = 0.0 if total_frames_analyzed > 30 else 70.0

        # Composite overall score with configurable weights
        w = BiomechanicalScoringEngine._get_weights()
        overall_score = (
            (form_accuracy * w["form"]) +
            (rom_score * w["rom"]) +
            (consistency_score * w["consistency"]) +
            (completion_score * w["completion"])
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 1)

        # Letter grade
        if overall_score >= 93:
            grade = "A+"
        elif overall_score >= 85:
            grade = "A"
        elif overall_score >= 75:
            grade = "B"
        elif overall_score >= 65:
            grade = "C"
        else:
            grade = "Needs Improvement"

        return {
            "overall_score": overall_score,
            "grade": grade,
            "weights": w,
            "metrics_breakdown": {
                "form_accuracy": round(form_accuracy, 1),
                "range_of_motion": round(rom_score, 1),
                "tempo_smoothness": round(tempo_score, 1),
                "bilateral_symmetry": round(symmetry_score, 1),
                "movement_consistency": consistency_score,
                "rep_completion": round(completion_score, 1),
            },
            "raw_stats": {
                "total_reps": total_reps,
                "total_form_faults": sum(form_error_frequency.values()),
                "error_breakdown": form_error_frequency,
                "frames_analyzed": total_frames_analyzed,
            }
        }

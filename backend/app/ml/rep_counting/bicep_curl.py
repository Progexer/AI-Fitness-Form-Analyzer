"""
AI-Powered Fitness Coach — Bicep Curl Repetition Counter

Tracks bilateral elbow flexion and extension angles.
Validates peak contraction (elbow <= 55°), full extension, and elbow stability.
"""

from typing import Dict, List, Any, Optional
from app.ml.rep_counting.base import BaseRepCounter, MovementPhase, RepData


class BicepCurlCounter(BaseRepCounter):
    # A rep is "almost done" while lowering back to extension.
    _final_phase = MovementPhase.ECCENTRIC

    def __init__(self):
        # In bicep curls:
        # Start/bottom: arm extended ~150°+
        # Inflection/top: peak contraction ~55° or lower
        super().__init__(
            exercise_name="bicep_curl",
            start_threshold=145.0,
            inflection_threshold=55.0,
            min_rep_duration=0.8
        )

    def _rep_base_score(self) -> float:
        if self.min_angle_in_rep > 65.0:
            return 80.0  # Incomplete curl squeeze
        return 100.0

    def update(
        self,
        angles: Dict[str, float],
        distances: Dict[str, float],
        timestamp: float,
        detected_errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        elbow_angle = angles.get("avg_elbow_angle", 160.0)
        rep_completed_this_frame = False

        if detected_errors:
            self.current_rep_errors.extend(detected_errors)

        if self.current_phase == MovementPhase.IDLE:
            # Concentric curling starts when angle drops below 130°
            if elbow_angle < 130.0:
                self.current_phase = MovementPhase.CONCENTRIC
                self.rep_start_time = timestamp
                self.rep_start_angle = elbow_angle
                self.min_angle_in_rep = elbow_angle
                self.max_angle_in_rep = elbow_angle
                self.current_rep_errors = list(detected_errors or [])

        elif self.current_phase == MovementPhase.CONCENTRIC:
            self.min_angle_in_rep = min(self.min_angle_in_rep, elbow_angle)
            self.max_angle_in_rep = max(self.max_angle_in_rep, elbow_angle)

            if elbow_angle <= self.inflection_threshold:
                self.current_phase = MovementPhase.INFLECTION
                self.peak_turnaround_time = timestamp
            elif elbow_angle > self.min_angle_in_rep + 12.0:
                # Started lowering prematurely
                self.current_phase = MovementPhase.ECCENTRIC
                self.peak_turnaround_time = timestamp

        elif self.current_phase == MovementPhase.INFLECTION:
            self.min_angle_in_rep = min(self.min_angle_in_rep, elbow_angle)
            if elbow_angle > self.min_angle_in_rep + 8.0:
                self.current_phase = MovementPhase.ECCENTRIC

        elif self.current_phase == MovementPhase.ECCENTRIC:
            self.max_angle_in_rep = max(self.max_angle_in_rep, elbow_angle)

            # Re-ascent (new curl began while lowering): back to CONCENTRIC,
            # re-anchor the extension reference to the lowest point seen.
            if elbow_angle < self.min_angle_in_rep - 10.0:
                self.current_phase = MovementPhase.CONCENTRIC
                self.min_angle_in_rep = min(self.min_angle_in_rep, elbow_angle)
                if self.max_angle_in_rep - self.min_angle_in_rep >= 15.0:
                    self.rep_start_angle = self.max_angle_in_rep
                return {
                    "rep_count": self.rep_count,
                    "phase": self.current_phase.value,
                    "current_angle": round(elbow_angle, 1),
                    "rep_completed": rep_completed_this_frame,
                    "latest_rep": self.reps_history[-1].to_dict() if self.reps_history else None,
                }

            self.min_angle_in_rep = min(self.min_angle_in_rep, elbow_angle)

            # Returned to extended position
            if elbow_angle >= self.start_threshold or self._returned_to_start(elbow_angle, tolerance=10.0):
                dur = timestamp - self.rep_start_time
                if dur >= self.min_rep_duration:
                    self.rep_count += 1
                    rom = self.max_angle_in_rep - self.min_angle_in_rep

                    # Rep score
                    base_score = self._rep_base_score()
                    error_deduction = len(set(self.current_rep_errors)) * 12.0
                    final_rep_score = max(20.0, min(100.0, base_score - error_deduction))

                    rep_record = RepData(
                        rep_number=self.rep_count,
                        start_time=self.rep_start_time,
                        peak_time=self.peak_turnaround_time,
                        end_time=timestamp,
                        min_angle=self.min_angle_in_rep,
                        max_angle=self.max_angle_in_rep,
                        rom=rom,
                        form_errors=self.current_rep_errors,
                        score=final_rep_score
                    )
                    self.reps_history.append(rep_record)
                    rep_completed_this_frame = True

                    self.current_phase = MovementPhase.IDLE
                    self.min_angle_in_rep = 999.0
                    self.max_angle_in_rep = -999.0
                elif elbow_angle < self.max_angle_in_rep - 25.0:
                    # Rep fizzled out before min duration: abandon without counting.
                    self.current_phase = MovementPhase.IDLE
                    self.min_angle_in_rep = 999.0
                    self.max_angle_in_rep = -999.0

        return {
            "rep_count": self.rep_count,
            "phase": self.current_phase.value,
            "current_angle": round(elbow_angle, 1),
            "rep_completed": rep_completed_this_frame,
            "latest_rep": self.reps_history[-1].to_dict() if self.reps_history else None,
        }

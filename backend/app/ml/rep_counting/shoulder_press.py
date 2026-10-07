"""
AI-Powered Fitness Coach — Overhead Shoulder Press Repetition Counter

Tracks vertical overhead arm extension, lockout angle, and neutral spine stability.
"""

from typing import Dict, List, Any, Optional
from app.ml.rep_counting.base import BaseRepCounter, MovementPhase, RepData


class ShoulderPressCounter(BaseRepCounter):
    # A rep is "almost done" while lowering back to rack.
    _final_phase = MovementPhase.ECCENTRIC

    def __init__(self):
        # Start/rack: elbows flexed ~85°
        # Top lockout: elbows extended ~165°+
        super().__init__(
            exercise_name="shoulder_press",
            start_threshold=95.0,
            inflection_threshold=160.0,
            min_rep_duration=0.8
        )

    def _rep_base_score(self) -> float:
        if self.max_angle_in_rep < 155.0:
            return 80.0  # Incomplete lockout
        return 100.0

    def update(
        self,
        angles: Dict[str, float],
        distances: Dict[str, float],
        timestamp: float,
        detected_errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        elbow_angle = angles.get("avg_elbow_angle", 90.0)
        rep_completed_this_frame = False

        if detected_errors:
            self.current_rep_errors.extend(detected_errors)

        if self.current_phase == MovementPhase.IDLE:
            # Pressing upwards begins when elbow angle exceeds 105°
            if elbow_angle > 105.0:
                self.current_phase = MovementPhase.CONCENTRIC
                self.rep_start_time = timestamp
                self.rep_start_angle = elbow_angle
                self.min_angle_in_rep = elbow_angle
                self.max_angle_in_rep = elbow_angle
                self.current_rep_errors = list(detected_errors or [])

        elif self.current_phase == MovementPhase.CONCENTRIC:
            self.min_angle_in_rep = min(self.min_angle_in_rep, elbow_angle)
            self.max_angle_in_rep = max(self.max_angle_in_rep, elbow_angle)

            # Reached top overhead lockout
            if elbow_angle >= self.inflection_threshold:
                self.current_phase = MovementPhase.INFLECTION
                self.peak_turnaround_time = timestamp
            elif elbow_angle < self.max_angle_in_rep - 15.0:
                # Started lowering before full lockout
                self.current_phase = MovementPhase.ECCENTRIC
                self.peak_turnaround_time = timestamp

        elif self.current_phase == MovementPhase.INFLECTION:
            self.max_angle_in_rep = max(self.max_angle_in_rep, elbow_angle)
            if elbow_angle < self.max_angle_in_rep - 10.0:
                self.current_phase = MovementPhase.ECCENTRIC

        elif self.current_phase == MovementPhase.ECCENTRIC:
            self.min_angle_in_rep = min(self.min_angle_in_rep, elbow_angle)

            # Re-ascent (new press began while lowering): back to CONCENTRIC,
            # re-anchor the rack reference to the lowest point seen.
            if elbow_angle > self.max_angle_in_rep + 10.0:
                self.current_phase = MovementPhase.CONCENTRIC
                self.max_angle_in_rep = max(self.max_angle_in_rep, elbow_angle)
                if self.max_angle_in_rep - self.min_angle_in_rep >= 15.0:
                    self.rep_start_angle = self.min_angle_in_rep
                return {
                    "rep_count": self.rep_count,
                    "phase": self.current_phase.value,
                    "current_angle": round(elbow_angle, 1),
                    "rep_completed": rep_completed_this_frame,
                    "latest_rep": self.reps_history[-1].to_dict() if self.reps_history else None,
                }

            self.max_angle_in_rep = max(self.max_angle_in_rep, elbow_angle)

            # Returned down to rack level
            if elbow_angle <= self.start_threshold or self._returned_to_start(elbow_angle, tolerance=10.0, min_rom=30.0):
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
                elif elbow_angle > self.min_angle_in_rep + 25.0:
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

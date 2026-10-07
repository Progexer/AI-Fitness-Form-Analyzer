"""
AI-Powered Fitness Coach — Squat Repetition Counter

Tracks knee flexion/extension angles and hip displacement.
Validates depth, ascent tempo, and form violations during repetitions.
"""

from typing import Dict, List, Any, Optional
from app.ml.rep_counting.base import BaseRepCounter, MovementPhase, RepData


class SquatCounter(BaseRepCounter):
    # A rep is "almost done" while ascending back to standing.
    _final_phase = MovementPhase.CONCENTRIC

    def __init__(self):
        # start_threshold: upright knee ~160°
        # inflection_threshold: parallel/deep knee ~95°
        super().__init__(
            exercise_name="squat",
            start_threshold=160.0,
            inflection_threshold=95.0,
            min_rep_duration=0.8
        )

    def _rep_base_score(self) -> float:
        # Full depth (knee <= 95°) gets 100 base score; shallow penalizes
        if self.min_angle_in_rep > 105.0:
            return 75.0
        elif self.min_angle_in_rep > 95.0:
            return 90.0
        return 100.0

    def update(
        self,
        angles: Dict[str, float],
        distances: Dict[str, float],
        timestamp: float,
        detected_errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        knee_angle = angles.get("avg_knee_angle", 180.0)
        rep_completed_this_frame = False

        if detected_errors:
            self.current_rep_errors.extend(detected_errors)

        if self.current_phase == MovementPhase.IDLE:
            if knee_angle < 145.0:
                self.current_phase = MovementPhase.ECCENTRIC
                self.rep_start_time = timestamp
                self.rep_start_angle = knee_angle
                self.min_angle_in_rep = knee_angle
                self.max_angle_in_rep = knee_angle
                self.current_rep_errors = list(detected_errors or [])

        elif self.current_phase == MovementPhase.ECCENTRIC:
            self.min_angle_in_rep = min(self.min_angle_in_rep, knee_angle)
            self.max_angle_in_rep = max(self.max_angle_in_rep, knee_angle)

            # Check if lowest inflection point reached
            if knee_angle <= self.inflection_threshold:
                self.current_phase = MovementPhase.INFLECTION
                self.peak_turnaround_time = timestamp
            elif knee_angle > self.min_angle_in_rep + 12.0:
                # Started ascending without hitting full depth
                self.current_phase = MovementPhase.CONCENTRIC
                self.peak_turnaround_time = timestamp

        elif self.current_phase == MovementPhase.INFLECTION:
            self.min_angle_in_rep = min(self.min_angle_in_rep, knee_angle)
            if knee_angle > self.min_angle_in_rep + 8.0:
                self.current_phase = MovementPhase.CONCENTRIC

        elif self.current_phase == MovementPhase.CONCENTRIC:
            self.max_angle_in_rep = max(self.max_angle_in_rep, knee_angle)

            # Re-descent (new descent began, e.g. video started mid-pose):
            # go back to ECCENTRIC and re-anchor the standing reference.
            if knee_angle < self.min_angle_in_rep - 10.0:
                self.current_phase = MovementPhase.ECCENTRIC
                self.min_angle_in_rep = min(self.min_angle_in_rep, knee_angle)
                if self.max_angle_in_rep - self.min_angle_in_rep >= 15.0:
                    self.rep_start_angle = self.max_angle_in_rep
                return {
                    "rep_count": self.rep_count,
                    "phase": self.current_phase.value,
                    "current_angle": round(knee_angle, 1),
                    "rep_completed": rep_completed_this_frame,
                    "latest_rep": self.reps_history[-1].to_dict() if self.reps_history else None,
                }

            self.min_angle_in_rep = min(self.min_angle_in_rep, knee_angle)

            if knee_angle >= self.start_threshold or self._returned_to_start(knee_angle):
                dur = timestamp - self.rep_start_time
                if dur >= self.min_rep_duration:
                    self.rep_count += 1
                    rom = self.max_angle_in_rep - self.min_angle_in_rep

                    # Rep score computation [0-100]
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
                elif knee_angle < self.max_angle_in_rep - 25.0:
                    # Rep fizzled out (too fast / reversed before min duration):
                    # abandon without counting so a fresh rep can start.
                    self.current_phase = MovementPhase.IDLE
                    self.min_angle_in_rep = 999.0
                    self.max_angle_in_rep = -999.0

        return {
            "rep_count": self.rep_count,
            "phase": self.current_phase.value,
            "current_angle": round(knee_angle, 1),
            "rep_completed": rep_completed_this_frame,
            "latest_rep": self.reps_history[-1].to_dict() if self.reps_history else None,
        }

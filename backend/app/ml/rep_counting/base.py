"""
AI-Powered Fitness Coach — Base Exercise Repetition Counter

State machine with hysteresis, phase tracking (eccentric/concentric),
ROM tracking, tempo monitoring, and per-rep biomechanical telemetry.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum
import time


class MovementPhase(str, Enum):
    IDLE = "IDLE"
    ECCENTRIC = "ECCENTRIC"        # Lowering / loading phase
    INFLECTION = "INFLECTION"      # Bottom / peak turnaround
    CONCENTRIC = "CONCENTRIC"      # Lifting / pressing phase
    COMPLETED = "COMPLETED"


class RepData:
    """Telemetry data captured for a single completed repetition."""
    def __init__(
        self,
        rep_number: int,
        start_time: float,
        peak_time: float,
        end_time: float,
        min_angle: float,
        max_angle: float,
        rom: float,
        form_errors: List[str],
        score: float
    ):
        self.rep_number = rep_number
        self.start_time = start_time
        self.peak_time = peak_time
        self.end_time = end_time
        self.duration = round(end_time - start_time, 2)
        self.eccentric_duration = round(peak_time - start_time, 2)
        self.concentric_duration = round(end_time - peak_time, 2)
        self.min_angle = round(min_angle, 1)
        self.max_angle = round(max_angle, 1)
        self.rom = round(rom, 1)
        self.form_errors = list(set(form_errors))
        self.score = round(score, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rep_number": self.rep_number,
            "start_time": self.start_time,
            "peak_time": self.peak_time,
            "end_time": self.end_time,
            "duration_sec": self.duration,
            "eccentric_duration_sec": self.eccentric_duration,
            "concentric_duration_sec": self.concentric_duration,
            "min_angle": self.min_angle,
            "max_angle": self.max_angle,
            "rom": self.rom,
            "form_errors": self.form_errors,
            "score": self.score,
        }


class BaseRepCounter(ABC):
    """Abstract base class for exercise rep counters."""

    def __init__(
        self,
        exercise_name: str,
        start_threshold: float,
        inflection_threshold: float,
        min_rep_duration: float = 0.8,
    ):
        self.exercise_name = exercise_name
        self.start_threshold = start_threshold
        self.inflection_threshold = inflection_threshold
        self.min_rep_duration = min_rep_duration

        self.rep_count = 0
        self.current_phase = MovementPhase.IDLE
        self.reps_history: List[RepData] = []

        # Current rep tracking variables
        self.rep_start_time = 0.0
        self.peak_turnaround_time = 0.0
        self.current_rep_errors: List[str] = []
        self.min_angle_in_rep = 999.0
        self.max_angle_in_rep = -999.0
        # Joint angle at the moment the rep started (upright/rack reference).
        # Used for person-adaptive completion: MediaPipe absolute angles vary
        # with body proportions and camera angle, so a fixed 160° lockout
        # threshold is unreachable for some subjects.
        self.rep_start_angle = 180.0

    def reset(self):
        self.rep_count = 0
        self.current_phase = MovementPhase.IDLE
        self.reps_history = []
        self.rep_start_time = 0.0
        self.peak_turnaround_time = 0.0
        self.current_rep_errors = []
        self.min_angle_in_rep = 999.0
        self.max_angle_in_rep = -999.0
        self.rep_start_angle = 180.0

    def _returned_to_start(self, current_angle: float, tolerance: float = 12.0, min_rom: float = 25.0) -> bool:
        """
        Person-adaptive rep completion: the joint has returned to within
        `tolerance` degrees of the angle at rep start, after travelling a
        range of motion of at least `min_rom` degrees. Works for both
        high-start (squat/push-up/curl) and low-start (shoulder press)
        movements since it uses absolute distance to the start reference.
        """
        rom = self.max_angle_in_rep - self.min_angle_in_rep
        return rom >= min_rom and abs(current_angle - self.rep_start_angle) <= tolerance

    # ── End-of-stream flush ──────────────────────────────────────────
    # Set by subclasses to the phase in which a rep is "almost done"
    # (CONCENTRIC for squat/push-up, ECCENTRIC for curl/shoulder-press).
    _final_phase = None

    def _rep_base_score(self) -> float:
        """Exercise-specific quality score before error deductions."""
        return 100.0

    def finalize(self, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Flush an in-progress rep when the video ends. Without this, the last
        rep of a clip is systematically lost (its completion peak is never
        followed by another frame). Only counts if ROM and duration are valid.
        Returns the recorded rep dict, or None.
        """
        if self._final_phase is None or self.current_phase != self._final_phase:
            return None
        rom = self.max_angle_in_rep - self.min_angle_in_rep
        dur = timestamp - self.rep_start_time
        if rom < 25.0 or dur < self.min_rep_duration:
            return None
        self.rep_count += 1
        base_score = self._rep_base_score()
        error_deduction = len(set(self.current_rep_errors)) * 12.0
        final_rep_score = max(20.0, min(100.0, base_score - error_deduction))
        rep_record = RepData(
            rep_number=self.rep_count,
            start_time=self.rep_start_time,
            peak_time=self.peak_turnaround_time or self.rep_start_time,
            end_time=timestamp,
            min_angle=self.min_angle_in_rep,
            max_angle=self.max_angle_in_rep,
            rom=rom,
            form_errors=self.current_rep_errors,
            score=final_rep_score,
        )
        self.reps_history.append(rep_record)
        self.current_phase = MovementPhase.IDLE
        self.min_angle_in_rep = 999.0
        self.max_angle_in_rep = -999.0
        return rep_record.to_dict()

    @abstractmethod
    def update(
        self,
        angles: Dict[str, float],
        distances: Dict[str, float],
        timestamp: float,
        detected_errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update counter state on each frame. Returns live feedback & rep state."""
        pass

    def get_summary(self) -> Dict[str, Any]:
        """Summary statistics across the entire session."""
        total_reps = len(self.reps_history)
        avg_score = float(sum(r.score for r in self.reps_history) / total_reps) if total_reps > 0 else 0.0
        avg_dur = float(sum(r.duration for r in self.reps_history) / total_reps) if total_reps > 0 else 0.0
        avg_rom = float(sum(r.rom for r in self.reps_history) / total_reps) if total_reps > 0 else 0.0

        all_errors = []
        for r in self.reps_history:
            all_errors.extend(r.form_errors)

        return {
            "exercise": self.exercise_name,
            "total_reps": total_reps,
            "average_rep_score": round(avg_score, 1),
            "average_duration_sec": round(avg_dur, 2),
            "average_rom": round(avg_rom, 1),
            "total_errors_detected": len(all_errors),
            "reps": [r.to_dict() for r in self.reps_history]
        }

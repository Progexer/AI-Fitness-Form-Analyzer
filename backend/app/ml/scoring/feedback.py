"""
AI-Powered Fitness Coach — Biomechanical Coaching Feedback Engine

Generates immediate real-time cues and detailed post-workout analysis reports
with actionable corrective exercise drills.
"""

from typing import Dict, List, Any, Optional


# Instant cues mapped to detected biomechanical faults
INSTANT_CUES = {
    "knee_valgus": "Push your knees outward over your pinky toes!",
    "shallow_squat": "Sink deeper — bring your hips parallel to knee height!",
    "excessive_forward_lean": "Keep your chest tall and eyes forward!",
    "asymmetric_weight_shift": "Distribute your weight evenly through both feet!",
    "elbow_flare": "Tuck your elbows to a 45-degree angle with your torso!",
    "sagging_hips": "Engage your core and glutes to keep your body in a straight plank!",
    "raised_hips": "Lower your hips inline with your shoulders and heels!",
    "shallow_depth": "Lower until your chest nearly grazes the floor!",
    "elbow_drift": "Pin your elbows to your sides — isolate the biceps!",
    "incomplete_rom": "Achieve full contraction at the top and full stretch at the bottom!",
    "trunk_sway": "Stand firm — avoid rocking back and forth to lift the weight!",
    "asymmetric_curl": "Lift both arms at an identical, synchronized tempo!",
    "excessive_arch": "Do not hyperextend your lower back — brace your core!",
    "incomplete_lockout": "Extend your arms fully overhead until elbows are straight!",
    "uneven_press": "Press both sides evenly and lock out together!",
    "good_form": "Great form! Maintain this steady tempo and control.",
}

# Corrective drills and cues for comprehensive reports
CORRECTIVE_DRILLS = {
    "knee_valgus": {
        "drill": "Banded Squats / Monster Walks",
        "description": "Place a mini-loop resistance band just above your knees during squats to activate the gluteus medius and prevent internal knee collapse."
    },
    "shallow_squat": {
        "drill": "Box Squats & Hip Mobility Openers",
        "description": "Perform squats to a 90-degree box or bench to build kinesthetic awareness of full parallel depth, paired with 90/90 hip stretches."
    },
    "excessive_forward_lean": {
        "drill": "Goblet Squats & Thoracic Extensions",
        "description": "Holding a kettlebell or dumbbell close to your sternum provides a natural counterbalance to maintain an upright torso angle."
    },
    "elbow_flare": {
        "drill": "Incline Arrow Push-ups",
        "description": "Focus on driving your elbows back like an arrow rather than out like a 'T', maintaining roughly a 45-degree angle to protect your rotator cuffs."
    },
    "sagging_hips": {
        "drill": "RKC Plank Hold & Hollow Body Rocks",
        "description": "Strengthen anterior core endurance to eliminate lumbar hyperextension during horizontal pressing movements."
    },
    "elbow_drift": {
        "drill": "Incline Dumbbell Curls & Wall Curls",
        "description": "Stand against a wall or sit on a 60-degree incline bench to physically constrain the upper arm from swinging forward."
    },
    "excessive_arch": {
        "drill": "Half-Kneeling Overhead Press",
        "description": "Pressing from a half-kneeling position locks your pelvis and prevents lumbar hyperextension, forcing strict shoulder drive."
    },
}


class FeedbackGenerator:
    """Generates real-time cues and structured coaching reports."""

    @staticmethod
    def get_instant_cue(error_type: str) -> str:
        return INSTANT_CUES.get(error_type, "Maintain smooth, controlled motion.")

    @staticmethod
    def generate_coaching_report(
        exercise: str,
        scoring_results: Dict[str, Any],
        reps_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Produce a comprehensive coaching evaluation.
        """
        overall_score = scoring_results.get("overall_score", 0.0)
        grade = scoring_results.get("grade", "N/A")
        error_counts = scoring_results.get("raw_stats", {}).get("error_breakdown", {})
        total_reps = reps_summary.get("total_reps", 0)

        strengths = []
        improvements = []
        drills = []

        # Analyze strengths
        breakdown = scoring_results.get("metrics_breakdown", {})
        if breakdown.get("form_accuracy", 0) >= 85:
            strengths.append("Exceptional movement discipline and minimal biomechanical breakdown.")
        if breakdown.get("range_of_motion", 0) >= 80:
            strengths.append("Consistent full range of motion throughout all completed reps.")
        if breakdown.get("bilateral_symmetry", 0) >= 85:
            strengths.append("High left-to-right bilateral symmetry with balanced limb mechanics.")
        if breakdown.get("tempo_smoothness", 0) >= 85:
            strengths.append("Controlled cadence with steady eccentric and concentric pacing.")

        if not strengths:
            strengths.append("Solid effort with clear fundamentals to build on.")

        # Top error analysis
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        for err, count in sorted_errors[:3]:
            if err != "good_form" and count > 0:
                cue = INSTANT_CUES.get(err, "")
                improvements.append({
                    "fault": err.replace("_", " ").title(),
                    "frequency": count,
                    "coaching_cue": cue
                })
                if err in CORRECTIVE_DRILLS:
                    drills.append(CORRECTIVE_DRILLS[err])

        # Summary text
        if overall_score >= 85:
            summary = f"Outstanding performance! You completed {total_reps} reps with high mechanical efficiency ({grade})."
        elif overall_score >= 70:
            summary = f"Good session with {total_reps} reps completed. Minor form corrections will significantly improve your efficiency."
        else:
            summary = f"Completed {total_reps} reps. Focus on the recommended corrective drills before increasing load or volume."

        return {
            "exercise": exercise,
            "overall_score": overall_score,
            "grade": grade,
            "summary": summary,
            "strengths": strengths,
            "improvements": improvements,
            "recommended_drills": drills,
        }

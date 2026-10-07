"""
AI-Powered Fitness Coach — Reports & PDF Export API Router
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.analysis_service import AnalysisService
from app.services.pdf_report_service import generate_workout_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{analysis_id}/pdf")
def download_pdf_report(analysis_id: str):
    res = AnalysisService.get_analysis_by_id(analysis_id)
    if not res:
        raise HTTPException(status_code=404, detail="Analysis record not found")

    pdf_stream = generate_workout_pdf(res)
    exercise_clean = res.get("exercise", "workout")
    filename = f"AI_Fitness_Report_{exercise_clean}_{analysis_id[:8]}.pdf"

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

"""
AI-Powered Fitness Coach — Publication-Quality PDF Workout Report Generator

Uses ReportLab to build structured biomechanical performance reports.
"""

import io
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def generate_workout_pdf(analysis_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a PDF document in-memory as a BytesIO stream.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15,
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    bold_body = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    elements = []

    # Title Banner
    exercise_name = analysis_data.get("exercise", "Workout").replace("_", " ").title()
    elements.append(Paragraph(f"AI Fitness Coach — {exercise_name} Evaluation", title_style))
    created_at = analysis_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))[:16]
    elements.append(Paragraph(f"Analysis ID: {analysis_data.get('id', 'N/A')}  |  Date: {created_at}  |  Model: {analysis_data.get('model_used', 'Random Forest')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=15))

    # KPI Summary Cards
    overall_score = analysis_data.get("overall_score", 0.0)
    grade = analysis_data.get("grade", "N/A")
    total_reps = analysis_data.get("total_reps", 0)
    proc_time = analysis_data.get("processing_time_sec", 0.0)

    score_color = "#10B981" if overall_score >= 80 else ("#F59E0B" if overall_score >= 65 else "#EF4444")

    kpi_data = [
        [
            Paragraph(f"<font size=8 color='#64748B'>OVERALL SCORE</font><br/><font size=20 color='{score_color}'><b>{overall_score}</b></font><font size=10 color='#64748B'>/100</font>", body_style),
            Paragraph(f"<font size=8 color='#64748B'>FORM GRADE</font><br/><font size=20 color='#0F172A'><b>{grade}</b></font>", body_style),
            Paragraph(f"<font size=8 color='#64748B'>COMPLETED REPS</font><br/><font size=20 color='#0F172A'><b>{total_reps}</b></font>", body_style),
            Paragraph(f"<font size=8 color='#64748B'>ANALYSIS DURATION</font><br/><font size=20 color='#0F172A'><b>{proc_time}s</b></font>", body_style),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 142])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 15))

    # Metrics Breakdown Section
    elements.append(Paragraph("Biomechanical Domain Metrics", section_title_style))
    breakdown = analysis_data.get("metrics_breakdown", {})
    sub_metrics = [
        ["Domain", "Score", "Target Benchmark", "Status"],
        ["Form Accuracy (45%)", f"{breakdown.get('form_accuracy', 0)} / 100", ">= 85.0", "Optimal" if breakdown.get('form_accuracy', 0) >= 80 else "Attention"],
        ["Range of Motion (25%)", f"{breakdown.get('range_of_motion', 0)} / 100", ">= 80.0", "Optimal" if breakdown.get('range_of_motion', 0) >= 80 else "Attention"],
        ["Tempo & Smoothness (15%)", f"{breakdown.get('tempo_smoothness', 0)} / 100", ">= 85.0", "Optimal" if breakdown.get('tempo_smoothness', 0) >= 80 else "Attention"],
        ["Bilateral Symmetry (15%)", f"{breakdown.get('bilateral_symmetry', 0)} / 100", ">= 85.0", "Optimal" if breakdown.get('bilateral_symmetry', 0) >= 80 else "Attention"],
    ]
    sub_table = Table(sub_metrics, colWidths=[170, 110, 130, 122])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 15))

    # Repetition Table Section
    elements.append(Paragraph("Repetition Telemetry Breakdown", section_title_style))
    reps = analysis_data.get("reps", [])
    rep_rows = [["Rep #", "Duration", "Ecc / Con", "Min Angle", "ROM", "Form Faults", "Score"]]
    for r in reps[:12]:  # Display up to 12 reps on single page
        errs = ", ".join(r.get("form_errors", [])) if r.get("form_errors") else "None (Clean)"
        rep_rows.append([
            f"Rep {r.get('rep_number', 1)}",
            f"{r.get('duration_sec', 0.0)}s",
            f"{r.get('eccentric_duration_sec', 0.0)}s / {r.get('concentric_duration_sec', 0.0)}s",
            f"{r.get('min_angle', 0.0)}°",
            f"{r.get('rom', 0.0)}°",
            Paragraph(errs, ParagraphStyle("TblErr", parent=body_style, fontSize=7, leading=9)),
            f"{r.get('score', 0.0)}"
        ])

    if len(rep_rows) == 1:
        rep_rows.append(["-", "-", "-", "-", "-", "No completed reps recorded", "-"])

    reps_table = Table(rep_rows, colWidths=[45, 55, 95, 65, 55, 160, 57])
    reps_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (4, -1), "CENTER"),
        ("ALIGN", (6, 0), (6, -1), "CENTER"),
    ]))
    elements.append(reps_table)
    elements.append(Spacer(1, 15))

    # Coaching Feedback & Corrective Drills
    feedback = analysis_data.get("coaching_feedback") or {}
    elements.append(Paragraph("AI Coaching Insights & Corrective Strategy", section_title_style))
    summary_text = feedback.get("summary", "Overall solid execution.")
    elements.append(Paragraph(f"<b>Summary:</b> {summary_text}", body_style))
    elements.append(Spacer(1, 6))

    drills = feedback.get("recommended_drills", [])
    if drills:
        elements.append(Paragraph("<b>Targeted Corrective Drills:</b>", bold_body))
        for d in drills:
            drill_name = d.get("drill", "")
            drill_desc = d.get("description", "")
            elements.append(Paragraph(f"• <b>{drill_name}:</b> {drill_desc}", body_style))
            elements.append(Spacer(1, 3))

    doc.build(elements)
    buffer.seek(0)
    return buffer

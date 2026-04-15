"""PDF report generation for startup feedback exports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _as_text(value: Any, fallback: str = "N/A") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        text = value.strip()
        return text if text else fallback
    if isinstance(value, (list, tuple, set)):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(parts) if parts else fallback
    return str(value)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        lines = [line.strip(" -•\t") for line in value.splitlines() if line.strip()]
        return lines if lines else [value.strip()]
    if isinstance(value, tuple | set):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


def _score_text(value: Any) -> str:
    if value is None:
        return "N/A"
    try:
        score = int(round(float(str(value))))
        return f"{score}/10"
    except (TypeError, ValueError):
        return _as_text(value)


def _paragraph_text(value: Any) -> str:
    if isinstance(value, (list, tuple, set)):
        items = [str(item).strip() for item in value if str(item).strip()]
        if not items:
            return "N/A"
        return "<br/>".join(f"• {escape(item)}" for item in items)
    if isinstance(value, dict):
        return escape(json.dumps(value, ensure_ascii=False))
    return escape(_as_text(value))


def _styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=sample["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0c1829"),
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#374f6a"),
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#7188a4"),
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "section",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1b48c4"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#0c1829"),
        ),
        "small": ParagraphStyle(
            "small",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#374f6a"),
        ),
        "card_label": ParagraphStyle(
            "card_label",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
        ),
        "card_value": ParagraphStyle(
            "card_value",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            textColor=colors.white,
        ),
    }


def _kv_section(story: list, title: str, rows: list[tuple[str, Any]], styles: dict[str, ParagraphStyle]) -> None:
    story.append(Paragraph(escape(title), styles["section"]))
    table_rows = [
        [
            Paragraph(f"<b>{escape(label)}</b>", styles["small"]),
            Paragraph(_paragraph_text(value), styles["body"]),
        ]
        for label, value in rows
    ]
    table = Table(table_rows, colWidths=[44 * mm, 136 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fbff")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce3f0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 4))


def _swot_cell(title: str, items: Any, styles: dict[str, ParagraphStyle]) -> Paragraph:
    bullet_text = _paragraph_text(_as_list(items))
    content = f"<b>{escape(title)}</b><br/>{bullet_text}"
    return Paragraph(content, styles["small"])


def generate_startup_feedback_pdf(
    batch_id: str,
    startup_name: str,
    outputs: dict[int, dict[str, Any]],
) -> bytes:
    """Build a styled PDF report for one startup."""
    a1 = outputs.get(1, {}) or {}
    a2 = outputs.get(2, {}) or {}
    a3 = outputs.get(3, {}) or {}
    a4 = outputs.get(4, {}) or {}
    a5 = outputs.get(5, {}) or {}
    a6 = outputs.get(6, {}) or {}

    styles = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"{startup_name} - EvalBot Feedback",
    )
    story: list = []

    story.append(Paragraph("EvalBot Feedback Report", styles["title"]))
    story.append(Paragraph(escape(startup_name), styles["subtitle"]))
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Batch: {escape(batch_id)} &nbsp;&nbsp;|&nbsp;&nbsp; Generated: {generated_at}", styles["meta"]))
    story.append(Spacer(1, 2))

    if a1.get("one_line_description"):
        story.append(Paragraph(escape(_as_text(a1.get("one_line_description"))), styles["body"]))
        story.append(Spacer(1, 6))

    cards = Table(
        [
            [
                Paragraph("VERDICT<br/><font size='12'><b>%s</b></font>" % escape(_as_text(a2.get("verdict"))), styles["card_label"]),
                Paragraph("TOTAL SCORE<br/><font size='12'><b>%s</b></font>" % escape(_as_text(a2.get("total_score"))), styles["card_label"]),
                Paragraph("RECOMMENDATION<br/><font size='12'><b>%s</b></font>" % escape(_as_text(a6.get("recommendation"))), styles["card_label"]),
            ]
        ],
        colWidths=[60 * mm, 60 * mm, 60 * mm],
    )
    cards.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1b48c4")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0, colors.white),
                ("INNERGRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#93a8e6")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(cards)
    story.append(Spacer(1, 9))

    if a2.get("summary"):
        story.append(Paragraph(f"<b>Executive Summary:</b> {escape(_as_text(a2.get('summary')))}", styles["body"]))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Scorecard", styles["section"]))
    score_rows = [["Dimension", "Score"]]
    for field, label in [
        ("score_problem_severity", "Problem Severity"),
        ("score_market_size", "Market Size"),
        ("score_differentiation", "Differentiation"),
        ("score_customer_clarity", "Customer Clarity"),
        ("score_founder_insight", "Founder Insight"),
        ("score_business_model", "Business Model"),
        ("score_moat_potential", "Moat Potential"),
        ("score_venture_potential", "Venture Potential"),
        ("score_competition_difficulty", "Competition Difficulty"),
        ("score_execution_feasibility", "Execution Feasibility"),
    ]:
        score_rows.append([label, _score_text(a2.get(field))])
    score_rows.append(["Total", _as_text(a2.get("total_score"))])
    score_table = Table(score_rows, colWidths=[126 * mm, 54 * mm])
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1b48c4")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce3f0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(score_table)

    swot = a2.get("swot", {}) or {}
    story.append(Paragraph("SWOT Analysis", styles["section"]))
    swot_table = Table(
        [
            [_swot_cell("Strengths", swot.get("strengths"), styles), _swot_cell("Weaknesses", swot.get("weaknesses"), styles)],
            [_swot_cell("Opportunities", swot.get("opportunities"), styles), _swot_cell("Threats", swot.get("threats"), styles)],
        ],
        colWidths=[90 * mm, 90 * mm],
    )
    swot_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce3f0")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(swot_table)
    story.append(Spacer(1, 4))

    _kv_section(
        story,
        "Startup Brief",
        [
            ("Problem", a1.get("problem")),
            ("Solution", a1.get("solution")),
            ("Target Customer", a1.get("target_customer")),
            ("Market", a1.get("market")),
            ("Business Model", a1.get("business_model")),
            ("Team", a1.get("team")),
        ],
        styles,
    )

    _kv_section(
        story,
        "Market Analysis",
        [
            ("Market Category", a3.get("market_category")),
            ("Size Class", a3.get("size_class")),
            ("Trend", a3.get("trend")),
            ("Attractiveness", _score_text(a3.get("attractiveness_score"))),
            ("Competition Difficulty", _score_text(a3.get("competition_score"))),
            ("Conclusion", a3.get("conclusion")),
        ],
        styles,
    )

    _kv_section(
        story,
        "Product & Positioning",
        [
            ("Product Reality", a4.get("product_reality")),
            ("Killer Feature", a4.get("killer_feature")),
            ("AI Wrapper Risk", a4.get("wrapper_risk")),
            ("Moat Hypothesis", a4.get("moat")),
            ("6-Month Focus", a4.get("six_month_focus")),
        ],
        styles,
    )

    _kv_section(
        story,
        "Founder Fit",
        [
            ("Founder Fit Score", _score_text(a5.get("fit_score"))),
            ("Execution Score", _score_text(a5.get("execution_score"))),
            ("Missing Roles", a5.get("missing_roles")),
            ("Conclusion", a5.get("conclusion")),
        ],
        styles,
    )

    _kv_section(
        story,
        "Recommendations",
        [
            ("Recommendation", a6.get("recommendation")),
            ("30-Day Plan", a6.get("thirty_day_plan")),
            ("90-Day Plan", a6.get("ninety_day_plan")),
            ("Pivot Options", a6.get("pivots")),
        ],
        styles,
    )

    doc.build(story)
    return buffer.getvalue()

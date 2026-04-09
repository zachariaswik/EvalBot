"""Roadmap page — /roadmap route (static)."""

import reflex as rx

from frontend.components.badges import section_marker
from frontend.components.navbar import page_layout

BLUE = "#1b48c4"
BLUE_BG = "#eef2fd"
GOLD = "#a85800"
GOLD_BG = "#fef3dc"
GREEN = "#0a7c52"
GREEN_BG = "#d1fae5"
AMBER = "#92400e"
TEAL = "#0d9488"
PURPLE = "#7c3aed"
TEXT = "#0c1829"
TEXT_3 = "#7188a4"
SURFACE = "#ffffff"
BORDER = "#dce3f0"
SURFACE_2 = "#f0f4fb"


def roadmap_card(
    number: str,
    icon_html: str,
    icon_bg: str,
    icon_border: str,
    title: str,
    desc: str,
    tag: str,
    tag_bg: str,
    tag_color: str,
    tag_border: str,
    watermark_color: str,
    preview: rx.Component,
    delay: str = "0s",
) -> rx.Component:
    return rx.box(
        # Watermark number
        rx.text(
            number,
            style={
                "position": "absolute",
                "top": "-16px",
                "right": "8px",
                "fontFamily": "'Georgia', serif",
                "fontSize": "100px",
                "fontWeight": "900",
                "color": watermark_color,
                "lineHeight": "1",
                "userSelect": "none",
                "pointerEvents": "none",
                "letterSpacing": "-0.06em",
            },
        ),
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.html(icon_html),
                    style={
                        "width": "44px",
                        "height": "44px",
                        "background": icon_bg,
                        "border": f"1px solid {icon_border}",
                        "borderRadius": "10px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                    },
                ),
                rx.box(
                    rx.text(tag, style={"fontSize": "10px", "fontWeight": "700", "color": tag_color, "letterSpacing": "0.06em", "fontFamily": "'Plus Jakarta Sans', sans-serif"}),
                    style={"padding": "3px 9px", "background": tag_bg, "border": f"1px solid {tag_border}", "borderRadius": "4px"},
                ),
                justify="between",
                align="start",
                width="100%",
                style={"marginBottom": "18px"},
            ),
            rx.text(title, style={"fontSize": "17px", "fontWeight": "800", "color": TEXT, "marginBottom": "8px", "letterSpacing": "-0.01em"}),
            rx.text(desc, style={"fontSize": "13px", "color": TEXT_3, "lineHeight": "1.7", "marginBottom": "18px", "flex": "1"}),
            preview,
            spacing="0",
            align="start",
            style={"position": "relative"},
        ),
        style={
            "background": SURFACE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "padding": "28px",
            "display": "flex",
            "flexDirection": "column",
            "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
            "position": "relative",
            "overflow": "hidden",
            "transition": "box-shadow 0.2s, border-color 0.2s, transform 0.15s",
            "_hover": {
                "boxShadow": "0 8px 30px rgba(27,72,196,0.1)",
                "borderColor": "#c2cfe4",
                "transform": "translateY(-1px)",
            },
        },
    )


def roadmap_page() -> rx.Component:
    return page_layout(
        # Header
        rx.vstack(
            section_marker("Product Vision"),
            rx.text(
                "Product Roadmap",
                style={"fontFamily": "'Georgia', serif", "fontSize": "40px", "fontWeight": "900", "color": TEXT, "letterSpacing": "-0.03em", "lineHeight": "1.05"},
            ),
            rx.text(
                "Where EvalBot is going. Each feature below is designed, not just dreamed.",
                style={"fontSize": "15px", "color": TEXT_3, "marginTop": "8px", "maxWidth": "500px"},
            ),
            spacing="1",
            align="start",
            style={"marginBottom": "44px"},
        ),

        # Feature grid
        rx.box(
            # 01 — Analyst Profiles
            roadmap_card(
                "01",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="#1b48c4" stroke-width="1.5"/><path d="M3 18c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="#1b48c4" stroke-width="1.5" stroke-linecap="round"/></svg>',
                BLUE_BG, "rgba(27,72,196,0.15)",
                "Analyst Profiles",
                "Give each team member their own account, history, and performance metrics. Track which analyst sourced the best deals.",
                "Coming Q3 2025", BLUE_BG, BLUE, "rgba(27,72,196,0.15)",
                BLUE_BG,
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.text("E", style={"fontFamily": "'Georgia', serif", "fontSize": "11px", "fontWeight": "900", "color": "white"}),
                            style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": BLUE, "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                        ),
                        rx.text("Erik W.", style={"fontSize": "12px", "fontWeight": "700", "color": TEXT}),
                        rx.text("·", style={"color": "#aebdd0"}),
                        rx.text("47 evals", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3}),
                        spacing="2",
                        align="center",
                        style={"marginBottom": "10px"},
                    ),
                    rx.vstack(
                        rx.hstack(rx.text("Avg Score", style={"fontSize": "11px", "color": TEXT_3}), rx.text("68.4", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": TEXT, "fontWeight": "700"}), justify="between", width="100%"),
                        rx.hstack(rx.text("VC Candidates", style={"fontSize": "11px", "color": TEXT_3}), rx.text("8", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": GREEN, "fontWeight": "700"}), justify="between", width="100%"),
                        rx.hstack(rx.text("Invested", style={"fontSize": "11px", "color": TEXT_3}), rx.text("2", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": BLUE, "fontWeight": "700"}), justify="between", width="100%"),
                        spacing="2",
                    ),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.8"},
                ),
            ),

            # 02 — Deal Flow Pipeline
            roadmap_card(
                "02",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="4" width="4" height="12" rx="1" stroke="#a85800" stroke-width="1.5"/><rect x="8" y="6" width="4" height="10" rx="1" stroke="#a85800" stroke-width="1.5"/><rect x="14.5" y="2" width="4" height="14" rx="1" stroke="#a85800" stroke-width="1.5"/></svg>',
                GOLD_BG, "rgba(168,88,0,0.15)",
                "Deal Flow Pipeline",
                "Kanban board to move startups from Submitted → Shortlisted → Due Diligence → Invested.",
                "Coming Q4 2025", GOLD_BG, GOLD, "rgba(168,88,0,0.15)",
                GOLD_BG,
                rx.hstack(
                    *[
                        rx.vstack(
                            rx.text(col, style={"fontSize": "9px", "fontWeight": "700", "color": clr, "letterSpacing": "0.04em", "textTransform": "uppercase", "marginBottom": "5px"}),
                            rx.box(rx.text("Co. A", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}), style={"background": bg, "border": f"1px solid {clr}22", "borderRadius": "4px", "padding": "5px 7px", "marginBottom": "3px"}),
                            spacing="0",
                            flex="1",
                            style={"minWidth": "0"},
                        )
                        for col, clr, bg in [
                            ("Submitted", "#7a90a4", "#f4f6fb"),
                            ("Shortlisted", BLUE, BLUE_BG),
                            ("Due Dil.", GOLD, GOLD_BG),
                            ("Invested", GREEN, GREEN_BG),
                        ]
                    ],
                    spacing="2",
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.8"},
                ),
            ),

            # 03 — Portfolio Tracking
            roadmap_card(
                "03",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><polyline points="2,16 6.5,9.5 10.5,12.5 18,5" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="13,5 18,5 18,10" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
                GREEN_BG, "rgba(10,124,82,0.15)",
                "Portfolio Tracking",
                "Track invested startups post-close. Re-evaluate automatically every quarter with updated data.",
                "Coming Q1 2026", GREEN_BG, GREEN, "rgba(10,124,82,0.15)",
                GREEN_BG,
                rx.box(
                    rx.el.table(
                        rx.el.thead(rx.el.tr(
                            rx.el.th("Startup", style={"textAlign": "left", "fontSize": "9px", "color": TEXT_3, "paddingBottom": "7px", "fontWeight": "700", "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                            rx.el.th("Status", style={"textAlign": "left", "fontSize": "9px", "color": TEXT_3, "paddingBottom": "7px", "fontWeight": "700", "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                            rx.el.th("Eval", style={"textAlign": "left", "fontSize": "9px", "color": TEXT_3, "paddingBottom": "7px", "fontWeight": "700", "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                        )),
                        rx.el.tbody(
                            rx.el.tr(
                                rx.el.td("Alpha Inc", style={"fontSize": "12px", "color": TEXT, "padding": "3px 0", "fontWeight": "600"}),
                                rx.el.td("Growing", style={"fontSize": "12px", "color": GREEN, "padding": "3px 0", "fontWeight": "600"}),
                                rx.el.td("Jan 25", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3}),
                            ),
                            rx.el.tr(
                                rx.el.td("BetaCo", style={"fontSize": "12px", "color": TEXT, "padding": "3px 0", "fontWeight": "600"}),
                                rx.el.td("Pivoting", style={"fontSize": "12px", "color": AMBER, "padding": "3px 0", "fontWeight": "600"}),
                                rx.el.td("Feb 25", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3}),
                            ),
                        ),
                        style={"width": "100%", "borderCollapse": "collapse"},
                    ),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.8"},
                ),
            ),

            # 04 — Automated Reports
            roadmap_card(
                "04",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3.5" y="1.5" width="13" height="17" rx="2" stroke="#7c3aed" stroke-width="1.5"/><line x1="7" y1="7" x2="13" y2="7" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><line x1="7" y1="10" x2="13" y2="10" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><line x1="7" y1="13" x2="11" y2="13" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/></svg>',
                "rgba(147,51,234,0.08)", "rgba(147,51,234,0.15)",
                "Automated Reports",
                "One-click PDF/email export of a full batch. Schedule weekly delivery to LPs and partners.",
                "Coming Q1 2026", "rgba(147,51,234,0.08)", PURPLE, "rgba(147,51,234,0.15)",
                "rgba(147,51,234,0.06)",
                rx.box(
                    rx.hstack(
                        rx.html('<svg width="13" height="13" viewBox="0 0 13 13" fill="none"><rect x="1" y="0.5" width="11" height="12" rx="1.5" stroke="#7188a4" stroke-width="1.2"/><line x1="3.5" y1="4" x2="9.5" y2="4" stroke="#7188a4" stroke-width="1.2"/><line x1="3.5" y1="6.5" x2="9.5" y2="6.5" stroke="#7188a4" stroke-width="1.2"/><line x1="3.5" y1="9" x2="7.5" y2="9" stroke="#7188a4" stroke-width="1.2"/></svg>'),
                        rx.text("batch_12_report.pdf", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "fontWeight": "500"}),
                        spacing="2",
                        style={"marginBottom": "10px"},
                    ),
                    rx.hstack(
                        rx.box(rx.text("Download PDF", style={"fontSize": "10px", "fontWeight": "600", "color": TEXT_3}), style={"padding": "3px 9px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "4px"}),
                        rx.box(rx.text("Send to Partners", style={"fontSize": "10px", "fontWeight": "600", "color": BLUE}), style={"padding": "3px 9px", "background": BLUE_BG, "border": "1px solid rgba(27,72,196,0.15)", "borderRadius": "4px"}),
                        spacing="2",
                        style={"marginBottom": "8px"},
                    ),
                    rx.text("Scheduled: Mondays 9am", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "#aebdd0"}),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.8"},
                ),
            ),

            # 05 — Partner API
            roadmap_card(
                "05",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M8 6H4a2 2 0 00-2 2v6a2 2 0 002 2h8a2 2 0 002-2v-4" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/><rect x="9" y="3" width="9" height="9" rx="2" stroke="#0d9488" stroke-width="1.5"/><line x1="12" y1="6" x2="15" y2="6" stroke="#0d9488" stroke-width="1.2" stroke-linecap="round"/><line x1="12" y1="8.5" x2="15" y2="8.5" stroke="#0d9488" stroke-width="1.2" stroke-linecap="round"/></svg>',
                "rgba(20,184,166,0.08)", "rgba(20,184,166,0.15)",
                "Partner API",
                "Founders submit pitches directly via API. Scores and verdicts returned automatically within minutes.",
                "Coming Q2 2026", SURFACE_2, TEXT_3, BORDER,
                "rgba(20,184,166,0.07)",
                rx.box(
                    rx.vstack(
                        rx.text("POST /api/v1/evaluate", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#4a7fd4", "lineHeight": "1.9"}),
                        rx.text('{"startup": "Acme AI",', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#7a90aa", "lineHeight": "1.9"}),
                        rx.text(' "pitch_url": "..."}', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#7a90aa", "lineHeight": "1.9"}),
                        rx.text('→ 200 {"score": 74,', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#0ec97a", "lineHeight": "1.9"}),
                        rx.text('      "verdict": "Promising"}', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#0ec97a", "lineHeight": "1.9"}),
                        spacing="0",
                        align="start",
                    ),
                    style={"padding": "14px 16px", "background": "#0d1a2e", "border": "1px solid rgba(255,255,255,0.06)", "borderRadius": "8px", "opacity": "0.85"},
                ),
            ),

            # 06 — Cohort Analytics
            roadmap_card(
                "06",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="13" width="3.5" height="5.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/><rect x="8" y="9" width="3.5" height="9.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/><rect x="14.5" y="5" width="3.5" height="13.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/></svg>',
                GOLD_BG, "rgba(168,88,0,0.15)",
                "Cohort Analytics",
                "Cross-batch trend charts: average score over time, verdict distribution shifts, sector patterns across cohorts.",
                "Coming Q2 2026", SURFACE_2, TEXT_3, BORDER,
                GOLD_BG,
                rx.box(
                    rx.text("📈 Cohort trend chart", style={"fontSize": "12px", "color": TEXT_3, "textAlign": "center", "padding": "20px 0"}),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.8"},
                ),
            ),

            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "20px",
            },
        ),
    )

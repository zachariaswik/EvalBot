"""Batch detail page — /batch/[batch_id] route."""

from __future__ import annotations

import reflex as rx

from frontend.components.badges import section_marker, verdict_badge, status_pill, score_bar
from frontend.components.charts import bar_chart, pie_chart
from frontend.components.navbar import page_layout
from frontend.state.batch import BatchState

BLUE = "#1b48c4"
BLUE_2 = "#163a9e"
BLUE_BG = "#eef2fd"
GOLD = "#a85800"
GOLD_BG = "#fef3dc"
GREEN = "#0a7c52"
GREEN_BG = "#d1fae5"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_3 = "#7188a4"
TEXT_4 = "#aebdd0"
SURFACE = "#ffffff"
SURFACE_2 = "#f0f4fb"
SURFACE_3 = "#e5ecf7"
BORDER = "#dce3f0"
BORDER_2 = "#c2cfe4"


def rank_badge(idx: int) -> rx.Component:
    if idx == 0:
        return rx.box(
            rx.text("1", style={"fontFamily": "'Georgia', serif", "fontSize": "11px", "fontWeight": "900", "color": "white", "lineHeight": "1"}),
            style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": BLUE, "display": "flex", "alignItems": "center", "justifyContent": "center"},
        )
    elif idx == 1:
        return rx.box(
            rx.text("2", style={"fontFamily": "'Georgia', serif", "fontSize": "11px", "fontWeight": "900", "color": TEXT_2, "lineHeight": "1"}),
            style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": SURFACE_3, "border": f"1.5px solid {BORDER_2}", "display": "flex", "alignItems": "center", "justifyContent": "center"},
        )
    elif idx == 2:
        return rx.box(
            rx.text("3", style={"fontFamily": "'Georgia', serif", "fontSize": "11px", "fontWeight": "900", "color": GOLD, "lineHeight": "1"}),
            style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": GOLD_BG, "border": "1.5px solid rgba(168,88,0,0.2)", "display": "flex", "alignItems": "center", "justifyContent": "center"},
        )
    else:
        return rx.text(str(idx + 1), style={"fontFamily": "'Courier New', monospace", "fontSize": "12px", "color": TEXT_4, "fontWeight": "500"})


def startup_score_row(s: dict, idx: int) -> rx.Component:
    score = s["score"]
    bar_color = s["bar_color"]
    return rx.el.tr(
        rx.el.td(
            rank_badge(idx),
            style={"padding": "14px 24px", "width": "48px"},
        ),
        rx.el.td(
            rx.link(
                s["name"],
                href="/batch/" + BatchState.current_batch_id + "/" + s["name"],
                style={"fontSize": "14px", "fontWeight": "700", "color": TEXT, "textDecoration": "none", "_hover": {"color": BLUE}},
            ),
            style={"padding": "14px 24px"},
        ),
        rx.el.td(
            verdict_badge(s["verdict"], s["verdict_color"]),
            style={"padding": "14px 24px"},
        ),
        rx.el.td(
            rx.hstack(
                rx.box(
                    rx.box(
                        style={
                            "height": "100%",
                            "borderRadius": "2px",
                            "background": bar_color,
                            "width": score.to(str) + "%",
                            "transition": "width 1.2s cubic-bezier(0.16,1,0.3,1) 0.2s",
                        }
                    ),
                    style={"flex": "1", "maxWidth": "100px", "height": "4px", "background": SURFACE_3, "borderRadius": "2px", "overflow": "hidden"},
                ),
                rx.text(
                    score,
                    style={"fontFamily": "'Georgia', serif", "fontSize": "18px", "fontWeight": "900", "color": bar_color, "lineHeight": "1", "minWidth": "28px"},
                ),
                spacing="3",
                align="center",
            ),
            style={"padding": "14px 24px", "minWidth": "180px"},
        ),
        rx.el.td(
            status_pill(s["pipeline_status"]),
            style={"padding": "14px 24px"},
        ),
        style={
            "borderBottom": f"1px solid {SURFACE_2}",
            "cursor": "pointer",
            "transition": "background 0.12s",
            "_hover": {"background": SURFACE_2},
        },
        on_click=rx.redirect("/batch/" + BatchState.current_batch_id + "/" + s["name"]),
    )


def batch_page() -> rx.Component:
    return page_layout(
        # Breadcrumb
        rx.hstack(
            rx.link("Dashboard", href="/", style={"color": BLUE, "fontSize": "13px", "fontWeight": "500", "textDecoration": "none"}),
            rx.text("/", style={"color": TEXT_4}),
            rx.text(BatchState.current_batch_id, style={"color": TEXT_2, "fontSize": "13px", "fontWeight": "500"}),
            spacing="2",
            align="center",
            style={"marginBottom": "28px"},
        ),

        # Header
        rx.hstack(
            rx.vstack(
                section_marker("Batch Analysis"),
                rx.text(
                    BatchState.current_batch_id,
                    style={"fontFamily": "'Georgia', serif", "fontSize": "36px", "fontWeight": "900", "color": TEXT, "letterSpacing": "-0.03em", "lineHeight": "1.05"},
                ),
                rx.cond(
                    BatchState.created_at != "",
                    rx.text(
                        BatchState.created_at[:19],
                        style={"fontFamily": "'Courier New', monospace", "fontSize": "12px", "color": TEXT_3, "marginTop": "5px"},
                    ),
                    rx.box(),
                ),
                spacing="1",
                align="start",
            ),
            rx.vstack(
                rx.text(
                    BatchState.startup_count,
                    style={"fontFamily": "'Georgia', serif", "fontSize": "44px", "fontWeight": "900", "color": BLUE, "lineHeight": "1", "letterSpacing": "-0.04em"},
                ),
                rx.text("startups", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                spacing="0",
                align="end",
            ),
            justify="between",
            align="end",
            wrap="wrap",
            style={"marginBottom": "40px"},
        ),

        # Charts
        rx.hstack(
            rx.box(
                section_marker("Score comparison"),
                bar_chart(BatchState.bar_chart_data, height=155),
                style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "12px",
                    "padding": "28px",
                    "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
                    "flex": "5",
                },
            ),
            rx.box(
                section_marker("Verdict distribution"),
                pie_chart(BatchState.pie_chart_data, height=200),
                style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "12px",
                    "padding": "28px",
                    "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
                    "flex": "3",
                },
            ),
            spacing="4",
            style={"marginBottom": "24px"},
        ),

        # Shortlist
        rx.cond(
            BatchState.shortlist.length() > 0,
            rx.box(
                section_marker("Recommended shortlist"),
                rx.hstack(
                    rx.foreach(
                        BatchState.shortlist,
                        lambda name: rx.link(
                            rx.hstack(
                                rx.box(style={"width": "6px", "height": "6px", "borderRadius": "50%", "background": GREEN, "flexShrink": "0"}),
                                rx.text(name, style={"fontSize": "13px", "fontWeight": "600", "color": GREEN}),
                                spacing="2",
                                align="center",
                            ),
                            href="/batch/" + BatchState.current_batch_id + "/" + name,
                            style={
                                "display": "inline-flex",
                                "alignItems": "center",
                                "padding": "5px 13px",
                                "background": GREEN_BG,
                                "border": "1px solid rgba(10,124,82,0.2)",
                                "borderRadius": "6px",
                                "textDecoration": "none",
                                "transition": "background 0.15s",
                                "_hover": {"background": "rgba(10,124,82,0.15)"},
                            },
                        ),
                    ),
                    wrap="wrap",
                    spacing="2",
                    style={"marginTop": "12px"},
                ),
                style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderLeft": f"4px solid {GREEN}",
                    "borderRadius": "0 12px 12px 0",
                    "padding": "22px 28px",
                    "marginBottom": "24px",
                },
            ),
            rx.box(),
        ),

        # Leaderboard
        rx.vstack(
            section_marker("Leaderboard"),
            rx.box(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Rank", style={"padding": "12px 24px", "textAlign": "left", "width": "48px", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                            rx.el.th("Startup", style={"padding": "12px 24px", "textAlign": "left", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                            rx.el.th("Verdict", style={"padding": "12px 24px", "textAlign": "left", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                            rx.el.th("Score", style={"padding": "12px 24px", "textAlign": "left", "minWidth": "180px", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                            rx.el.th("Status", style={"padding": "12px 24px", "textAlign": "left", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                            style={"borderBottom": f"1px solid {BORDER}", "background": SURFACE_2},
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            BatchState.startup_scores,
                            lambda s, idx: startup_score_row(s, idx),
                        )
                    ),
                    style={"width": "100%", "borderCollapse": "collapse"},
                ),
                style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "12px",
                    "overflow": "hidden",
                    "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
                },
            ),
            spacing="5",
            align="start",
            width="100%",
        ),
    )

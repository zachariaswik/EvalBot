"""Dashboard page — / route."""

from __future__ import annotations

import reflex as rx

from frontend.components.badges import section_marker
from frontend.components.navbar import page_layout
from frontend.state.dashboard import DashboardState

# ── Style constants ─────────────────────────────────────────────────────────
BLUE = "#1b48c4"
BLUE_2 = "#163a9e"
BLUE_BG = "#eef2fd"
GOLD_2 = "#d98e1e"
GREEN = "#0a7c52"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_3 = "#7188a4"
SURFACE = "#ffffff"
SURFACE_2 = "#f0f4fb"
BORDER = "#dce3f0"


def stat_card(number: str, label: str, value: rx.Var | str, suffix: str = "", accent: str = TEXT) -> rx.Component:
    return rx.box(
        # watermark number
        rx.text(
            number,
            style={
                "position": "absolute",
                "top": "-20px",
                "right": "4px",
                "fontFamily": "'Georgia', serif",
                "fontSize": "120px",
                "fontWeight": "900",
                "color": BLUE_BG,
                "lineHeight": "1",
                "userSelect": "none",
                "pointerEvents": "none",
                "letterSpacing": "-0.06em",
            },
        ),
        section_marker(label),
        rx.text(
            rx.cond(suffix, value.to(str) + suffix, value.to(str)),
            style={
                "fontFamily": "'Georgia', serif",
                "fontSize": "60px",
                "fontWeight": "900",
                "color": accent,
                "lineHeight": "1",
                "letterSpacing": "-0.05em",
                "position": "relative",
                "marginTop": "16px",
            },
        ),
        style={
            "background": SURFACE,
            "padding": "32px 36px",
            "position": "relative",
            "overflow": "hidden",
        },
    )


def batch_row(b: dict) -> rx.Component:
    count = b["startup_count"]
    date_text = rx.cond(b["created_at"], b["created_at"], "—")
    return rx.el.tr(
        rx.el.td(
            rx.hstack(
                rx.box(style={"width": "10px", "height": "10px", "borderRadius": "50%", "background": BLUE, "flexShrink": "0"}),
                rx.text(b["batch_id"], style={"fontFamily": "'Courier New', monospace", "fontSize": "15px", "fontWeight": "600", "color": TEXT}),
                rx.cond(
                    b["description"],
                    rx.text(b["description"], style={"fontSize": "13px", "color": TEXT_3}),
                    rx.box(),
                ),
                spacing="3",
                align="center",
            ),
            style={"padding": "18px 24px"},
        ),
        rx.el.td(
            rx.text(date_text, style={"fontFamily": "'Courier New', monospace", "fontSize": "13px", "color": TEXT_3}),
            style={"padding": "18px 24px"},
        ),
        rx.el.td(
            rx.vstack(
                rx.hstack(
                    rx.text(count, style={"fontSize": "18px", "fontWeight": "800", "color": TEXT}),
                    rx.text(
                        rx.cond(count == 1, "startup", "startups"),
                        style={"fontSize": "13px", "color": TEXT_3, "marginLeft": "4px"},
                    ),
                    spacing="1",
                    justify="end",
                    align="center",
                ),
                spacing="2",
                align="end",
            ),
            style={"padding": "18px 24px", "textAlign": "right"},
        ),
        rx.el.td(
            rx.text("›", style={"color": BLUE, "fontSize": "18px"}),
            style={"padding": "18px 24px", "textAlign": "right"},
        ),
        style={
            "borderBottom": f"1px solid {SURFACE_2}",
            "cursor": "pointer",
            "transition": "background 0.12s",
            "_hover": {"background": SURFACE_2},
        },
        on_click=rx.redirect(f"/batch/{b['batch_id']}"),
    )


def dashboard_page() -> rx.Component:
    return page_layout(
        # ── Page title ──
        rx.hstack(
            rx.vstack(
                section_marker("Dashboard / Deal Flow"),
                rx.text(
                    "Venture Intelligence",
                    style={"fontFamily": "'Georgia', serif", "fontSize": "40px", "fontWeight": "900", "color": TEXT, "letterSpacing": "-0.03em", "lineHeight": "1.05"},
                ),
                rx.text(
                    "All evaluated startups, batches, and AI-generated signals in one place.",
                    style={"fontSize": "15px", "color": TEXT_3, "marginTop": "6px"},
                ),
                spacing="1",
                align="start",
            ),
            rx.el.button(
                rx.hstack(
                    rx.html('<svg width="9" height="11" viewBox="0 0 9 11" fill="currentColor"><polygon points="0,0 9,5.5 0,11"/></svg>'),
                    rx.text("Run New Batch", style={"fontSize": "14px", "fontWeight": "700", "color": "white"}),
                    spacing="2",
                    align="center",
                ),
                disabled=True,
                style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "padding": "11px 24px",
                    "background": BLUE,
                    "border": "none",
                    "borderRadius": "8px",
                    "opacity": "0.45",
                    "cursor": "not-allowed",
                },
            ),
            justify="between",
            align="end",
            wrap="wrap",
            style={"marginBottom": "44px"},
        ),

        # ── All batches ──
        rx.vstack(
            section_marker("All batches"),
            rx.box(
                rx.grid(
                    stat_card("01", "Total batches", DashboardState.total_batches, accent=BLUE),
                    stat_card("02", "Total startups", DashboardState.total_startups, accent=GREEN),
                    stat_card("03", "Avg startups / batch", DashboardState.avg_startups_per_batch, accent=GOLD_2),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                rx.cond(
                    DashboardState.largest_batch_id != "",
                    rx.hstack(
                        rx.text("Largest batch", style={"fontSize": "12px", "fontWeight": "700", "letterSpacing": "0.04em", "textTransform": "uppercase", "color": TEXT_3}),
                        rx.box(
                            rx.text(
                                DashboardState.largest_batch_id,
                                style={"fontFamily": "'Courier New', monospace", "fontSize": "12px", "fontWeight": "600", "color": BLUE},
                            ),
                            style={"background": BLUE_BG, "border": "1px solid rgba(27,72,196,0.15)", "padding": "3px 10px", "borderRadius": "6px"},
                        ),
                        rx.text(
                            DashboardState.largest_batch_size.to(str) + " startups",
                            style={"fontSize": "14px", "fontWeight": "700", "color": TEXT},
                        ),
                        spacing="3",
                        align="center",
                        style={"marginTop": "14px"},
                    ),
                    rx.box(),
                ),
                style={"width": "100%", "marginBottom": "8px"},
            ),
            rx.cond(
                DashboardState.batches.length() > 0,
                rx.box(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Batch ID", style={"padding": "13px 24px", "textAlign": "left", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                                rx.el.th("Date", style={"padding": "16px 24px", "textAlign": "left", "fontSize": "12px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                                rx.el.th("Startups", style={"padding": "16px 24px", "textAlign": "right", "fontSize": "12px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                                rx.el.th("", style={"padding": "13px 24px", "width": "40px"}),
                                style={"borderBottom": f"1px solid {BORDER}"},
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(DashboardState.batches, batch_row),
                        ),
                        style={"width": "100%", "borderCollapse": "collapse"},
                    ),
                    style={
                        "background": SURFACE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "14px",
                        "overflow": "hidden",
                        "boxShadow": "0 8px 28px rgba(12,24,41,0.06)",
                    },
                ),
                rx.box(
                    rx.vstack(
                        rx.box(
                            rx.html('<svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="2" width="8" height="8" rx="1.5" stroke="#aebdd0" stroke-width="1.5"/><rect x="12" y="2" width="8" height="8" rx="1.5" stroke="#aebdd0" stroke-width="1.5"/><rect x="2" y="12" width="8" height="8" rx="1.5" stroke="#aebdd0" stroke-width="1.5"/><rect x="12" y="12" width="8" height="8" rx="1.5" stroke="#aebdd0" stroke-width="1.5" stroke-dasharray="2 2"/></svg>'),
                            style={
                                "width": "52px",
                                "height": "52px",
                                "background": SURFACE_2,
                                "border": f"1px solid {BORDER}",
                                "borderRadius": "12px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                        ),
                        rx.text("No batches yet", style={"fontSize": "16px", "fontWeight": "700", "color": TEXT_2}),
                        rx.text(
                            "Run python main.py batch Startups/ to evaluate your first batch.",
                            style={"fontSize": "13px", "color": TEXT_3, "maxWidth": "320px", "textAlign": "center"},
                        ),
                        spacing="3",
                        align="center",
                    ),
                    style={
                        "background": SURFACE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "64px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                    },
                ),
            ),
            spacing="5",
            align="start",
        ),
    )

"""Dashboard page — / route."""

from __future__ import annotations

import reflex as rx

from frontend.components.badges import section_marker, verdict_badge
from frontend.components.navbar import page_layout
from frontend.state.dashboard import DashboardState

# ── Style constants ─────────────────────────────────────────────────────────
BLUE = "#1b48c4"
BLUE_2 = "#163a9e"
BLUE_BG = "#eef2fd"
BLUE_GLOW = "rgba(27,72,196,0.12)"
GOLD_2 = "#d98e1e"
GREEN = "#0a7c52"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_3 = "#7188a4"
TEXT_4 = "#aebdd0"
SURFACE = "#ffffff"
SURFACE_2 = "#f0f4fb"
SURFACE_3 = "#e5ecf7"
BORDER = "#dce3f0"
BORDER_2 = "#c2cfe4"


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


def top_startup_card(s: dict, idx: int) -> rx.Component:
    score = s["score"]
    bar_color = s["bar_color"]
    return rx.link(
        rx.box(
            # rank badge #1
            rx.cond(
                idx == 0,
                rx.box(
                    rx.text("1", style={"fontFamily": "'Georgia', serif", "fontSize": "12px", "fontWeight": "900", "color": "white", "lineHeight": "1"}),
                    style={
                        "position": "absolute",
                        "top": "16px",
                        "right": "16px",
                        "width": "28px",
                        "height": "28px",
                        "background": BLUE,
                        "borderRadius": "50%",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                    },
                ),
                rx.box(),
            ),
            rx.box(
                rx.text(
                    s["name"],
                    style={
                        "fontSize": "16px",
                        "fontWeight": "700",
                        "color": TEXT,
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "marginBottom": "6px",
                    },
                ),
                verdict_badge(s["verdict"], s["verdict_color"]),
                style={"marginBottom": "12px"},
            ),
            rx.hstack(
                rx.text(
                    score,
                    style={"fontFamily": "'Georgia', serif", "fontSize": "38px", "fontWeight": "900", "lineHeight": "1", "color": bar_color},
                ),
                rx.text("/100", style={"fontSize": "14px", "color": TEXT_4, "marginBottom": "2px"}),
                spacing="1",
                align="end",
                style={"marginBottom": "12px"},
            ),
            rx.box(
                rx.box(
                    style={
                        "height": "100%",
                        "borderRadius": "2px",
                        "background": bar_color,
                        "width": score.to(str) + "%",
                    }
                ),
                style={"height": "3px", "background": SURFACE_3, "borderRadius": "2px", "overflow": "hidden"},
            ),
            style={
                "background": SURFACE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "24px",
                "cursor": "pointer",
                "position": "relative",
                "overflow": "hidden",
                "transition": "box-shadow 0.2s, border-color 0.2s, transform 0.15s",
                "_hover": {
                    "boxShadow": f"0 8px 30px {BLUE_GLOW}",
                    "borderColor": BORDER_2,
                    "transform": "translateY(-1px)",
                },
            },
        ),
        href=f"/batch/{DashboardState.latest_batch_id}/{s['name']}",
        style={"textDecoration": "none"},
    )


def batch_row(b: dict) -> rx.Component:
    count = b["startup_count"]
    return rx.el.tr(
        rx.el.td(
            rx.hstack(
                rx.box(style={"width": "8px", "height": "8px", "borderRadius": "50%", "background": BLUE, "flexShrink": "0"}),
                rx.text(b["batch_id"], style={"fontFamily": "'Courier New', monospace", "fontSize": "13px", "fontWeight": "500", "color": TEXT}),
                rx.cond(
                    b["description"],
                    rx.text(b["description"], style={"fontSize": "12px", "color": TEXT_3}),
                    rx.box(),
                ),
                spacing="3",
                align="center",
            ),
            style={"padding": "15px 24px"},
        ),
        rx.el.td(
            rx.text("—", style={"fontFamily": "'Courier New', monospace", "fontSize": "12px", "color": TEXT_3}),
            style={"padding": "15px 24px"},
        ),
        rx.el.td(
            rx.hstack(
                rx.text(count, style={"fontSize": "14px", "fontWeight": "700", "color": TEXT}),
                rx.text(
                    rx.cond(count == 1, "startup", "startups"),
                    style={"fontSize": "12px", "color": TEXT_3, "marginLeft": "3px"},
                ),
                spacing="1",
            ),
            style={"padding": "15px 24px", "textAlign": "right"},
        ),
        rx.el.td(
            rx.text("›", style={"color": BLUE, "fontSize": "16px"}),
            style={"padding": "15px 24px", "textAlign": "right"},
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
            rx.link(
                rx.hstack(
                    rx.html('<svg width="9" height="11" viewBox="0 0 9 11" fill="currentColor"><polygon points="0,0 9,5.5 0,11"/></svg>'),
                    rx.text("Run New Batch", style={"fontSize": "14px", "fontWeight": "700", "color": "white"}),
                    spacing="2",
                    align="center",
                ),
                href="/run",
                style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "padding": "11px 24px",
                    "background": BLUE,
                    "borderRadius": "8px",
                    "textDecoration": "none",
                    "transition": "background 0.15s",
                    "_hover": {"background": BLUE_2},
                },
            ),
            justify="between",
            align="end",
            wrap="wrap",
            style={"marginBottom": "44px"},
        ),

        # ── Stats ──
        rx.box(
            rx.hstack(
                stat_card("01", "01 / Startups evaluated", DashboardState.total_startups),
                stat_card("02", "02 / Batches processed", DashboardState.total_batches),
                stat_card("03", "03 / VC candidates (latest)", DashboardState.vc_percent, suffix="%", accent=GOLD_2),
                spacing="0",
                style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)", "gap": "1px", "background": BORDER},
            ),
            style={
                "borderRadius": "14px",
                "overflow": "hidden",
                "marginBottom": "44px",
                "boxShadow": "0 2px 12px rgba(12,24,41,0.06)",
            },
        ),

        # ── Latest batch highlight ──
        rx.cond(
            DashboardState.latest_batch_id != "",
            rx.box(
                rx.hstack(
                    rx.hstack(
                        section_marker("04 / Latest batch"),
                        rx.box(
                            rx.text(
                                DashboardState.latest_batch_id,
                                style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "fontWeight": "500", "color": BLUE},
                            ),
                            style={
                                "background": BLUE_BG,
                                "border": "1px solid rgba(27,72,196,0.15)",
                                "padding": "2px 9px",
                                "borderRadius": "4px",
                            },
                        ),
                        rx.cond(
                            DashboardState.latest_batch_created != "",
                            rx.text(
                                DashboardState.latest_batch_created[:10],
                                style={"fontSize": "12px", "color": TEXT_4, "fontWeight": "500"},
                            ),
                            rx.box(),
                        ),
                        spacing="3",
                        align="center",
                    ),
                    rx.link(
                        "View full batch →",
                        href="/batch/" + DashboardState.latest_batch_id,
                        style={"fontSize": "13px", "fontWeight": "600", "color": BLUE, "textDecoration": "none"},
                    ),
                    justify="between",
                    align="center",
                    style={"marginBottom": "20px"},
                ),
                rx.cond(
                    DashboardState.top_startups.length() > 0,
                    rx.box(
                        rx.foreach(
                            DashboardState.top_startups,
                            lambda s, idx: top_startup_card(s, idx),
                        ),
                        style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)", "gap": "14px"},
                    ),
                    rx.box(
                        rx.text("No startups evaluated in this batch yet.", style={"color": TEXT_3, "fontSize": "14px"}),
                        style={
                            "background": SURFACE,
                            "border": f"1px solid {BORDER}",
                            "borderRadius": "12px",
                            "padding": "36px",
                            "textAlign": "center",
                        },
                    ),
                ),
                style={"marginBottom": "44px"},
            ),
            rx.box(),
        ),

        # ── All batches ──
        rx.vstack(
            section_marker("05 / All batches"),
            rx.cond(
                DashboardState.batches.length() > 0,
                rx.box(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Batch ID", style={"padding": "13px 24px", "textAlign": "left", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                                rx.el.th("Date", style={"padding": "13px 24px", "textAlign": "left", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                                rx.el.th("Startups", style={"padding": "13px 24px", "textAlign": "right", "fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
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
                        "borderRadius": "12px",
                        "overflow": "hidden",
                        "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
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

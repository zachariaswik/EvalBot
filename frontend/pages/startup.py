"""Startup detail page — /batch/[batch_id]/[startup_name] route."""

from __future__ import annotations

import reflex as rx

from frontend.components.badges import section_marker, verdict_badge
from frontend.components.charts import radar_chart
from frontend.components.navbar import page_layout
from frontend.state.startup import StartupState

BLUE = "#1b48c4"
BLUE_BG = "#eef2fd"
GOLD = "#a85800"
GOLD_BG = "#fef3dc"
GREEN = "#0a7c52"
GREEN_BG = "#d1fae5"
RED = "#b91c1c"
RED_BG = "#fee2e2"
AMBER = "#92400e"
AMBER_BG = "#fef3c7"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_3 = "#7188a4"
TEXT_4 = "#aebdd0"
SURFACE = "#ffffff"
SURFACE_2 = "#f0f4fb"
SURFACE_3 = "#e5ecf7"
BORDER = "#dce3f0"


# ── Tab bar ──────────────────────────────────────────────────────────────────

def tab_button(label: str, tab_id: str) -> rx.Component:
    is_active = StartupState.active_tab == tab_id
    return rx.el.button(
        label,
        on_click=StartupState.set_tab(tab_id),
        style={
            "padding": "14px 22px",
            "fontSize": "13px",
            "fontWeight": "700",
            "fontFamily": "'Plus Jakarta Sans', sans-serif",
            "border": "none",
            "borderBottom": rx.cond(is_active, "2.5px solid #1b48c4", "2.5px solid transparent"),
            "background": rx.cond(is_active, SURFACE, "transparent"),
            "color": rx.cond(is_active, BLUE, TEXT_3),
            "cursor": "pointer",
            "whiteSpace": "nowrap",
            "transition": "color 0.15s, background 0.15s",
        },
    )


# ── SWOT ─────────────────────────────────────────────────────────────────────

def swot_panel(items: list[str] | rx.Var, title: str, bg: str, color: str, symbol: str) -> rx.Component:
    return rx.box(
        rx.text(title, style={"fontSize": "10px", "fontWeight": "800", "letterSpacing": "0.1em", "color": color, "marginBottom": "8px", "textTransform": "uppercase"}),
        rx.vstack(
            rx.foreach(
                items,
                lambda item: rx.hstack(
                    rx.text(symbol, style={"flexShrink": "0", "fontWeight": "800", "marginTop": "1px", "fontSize": "12px", "color": color}),
                    rx.text(item, style={"fontSize": "12px", "color": color, "lineHeight": "1.4"}),
                    spacing="1",
                    align="start",
                ),
            ),
            spacing="2",
        ),
        style={
            "padding": "14px",
            "background": bg,
            "border": f"1px solid {color}33",
            "borderRadius": "8px",
        },
    )


# ── Market tab ───────────────────────────────────────────────────────────────

def market_tab() -> rx.Component:
    a3 = StartupState.a3
    return rx.cond(
        StartupState.a3.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text("Market Category", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3, "marginBottom": "5px"}),
                    rx.text(a3["market_category"], style={"fontSize": "15px", "fontWeight": "700", "color": TEXT, "marginTop": "4px"}),
                    style={"padding": "18px", "background": SURFACE_2, "borderRadius": "8px", "border": f"1px solid {BORDER}", "flex": "1"},
                ),
                rx.box(
                    rx.text("Size Class", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3, "marginBottom": "5px"}),
                    rx.text(a3["size_class"], style={"fontSize": "15px", "fontWeight": "700", "color": TEXT, "marginTop": "4px"}),
                    style={"padding": "18px", "background": SURFACE_2, "borderRadius": "8px", "border": f"1px solid {BORDER}", "flex": "1"},
                ),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                rx.box(
                    rx.text("Attractiveness", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": BLUE, "marginBottom": "5px"}),
                    rx.hstack(
                        rx.text(a3["attractiveness_score"], style={"fontFamily": "'Georgia', serif", "fontSize": "32px", "fontWeight": "900", "color": BLUE, "lineHeight": "1"}),
                        rx.text("/10", style={"fontSize": "14px", "color": TEXT_3}),
                        spacing="1",
                        align="end",
                        style={"marginTop": "4px"},
                    ),
                    style={"padding": "18px", "background": BLUE_BG, "borderRadius": "8px", "border": "1px solid rgba(27,72,196,0.15)", "flex": "1"},
                ),
                rx.box(
                    rx.text("Competition Difficulty", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": GOLD, "marginBottom": "5px"}),
                    rx.hstack(
                        rx.text(a3["competition_score"], style={"fontFamily": "'Georgia', serif", "fontSize": "32px", "fontWeight": "900", "color": GOLD, "lineHeight": "1"}),
                        rx.text("/10", style={"fontSize": "14px", "color": TEXT_3}),
                        spacing="1",
                        align="end",
                        style={"marginTop": "4px"},
                    ),
                    style={"padding": "18px", "background": GOLD_BG, "borderRadius": "8px", "border": "1px solid rgba(168,88,0,0.15)", "flex": "1"},
                ),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                a3["trend"],
                rx.vstack(
                    rx.text("Trend", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                    rx.text(a3["trend"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                    spacing="1",
                    align="start",
                ),
                rx.box(),
            ),
            rx.cond(
                a3["conclusion"],
                rx.vstack(
                    rx.text("Conclusion", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                    rx.text(a3["conclusion"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                    spacing="1",
                    align="start",
                ),
                rx.box(),
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        rx.text("Market analysis not yet available.", style={"color": TEXT_3, "fontSize": "14px"}),
    )


# ── Product tab ───────────────────────────────────────────────────────────────

def product_tab() -> rx.Component:
    a4 = StartupState.a4
    wrapper_bg = rx.match(
        a4["wrapper_risk"],
        ("low", GREEN_BG),
        ("medium", AMBER_BG),
        RED_BG,
    )
    wrapper_color = rx.match(
        a4["wrapper_risk"],
        ("low", GREEN),
        ("medium", AMBER),
        RED,
    )
    return rx.cond(
        StartupState.a4.length() > 0,
        rx.vstack(
            rx.vstack(
                rx.text("Product Reality", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.text(a4["product_reality"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                spacing="1",
                align="start",
            ),
            rx.vstack(
                rx.text("Killer Feature", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.text(a4["killer_feature"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                spacing="1",
                align="start",
            ),
            rx.hstack(
                rx.text("AI Wrapper Risk", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.box(
                    rx.text(a4["wrapper_risk"].upper(), style={"fontSize": "12px", "fontWeight": "700", "color": wrapper_color}),
                    style={"padding": "4px 10px", "borderRadius": "5px", "background": wrapper_bg},
                ),
                spacing="3",
                align="center",
            ),
            rx.vstack(
                rx.text("Moat Hypothesis", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.text(a4["moat"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                spacing="1",
                align="start",
            ),
            rx.vstack(
                rx.text("6-Month Focus", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.text(a4["six_month_focus"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                spacing="1",
                align="start",
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        rx.text("Product analysis not yet available.", style={"color": TEXT_3, "fontSize": "14px"}),
    )


# ── Founder tab ───────────────────────────────────────────────────────────────

def founder_tab() -> rx.Component:
    a5 = StartupState.a5
    return rx.cond(
        StartupState.a5.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text("Founder Fit", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": BLUE, "marginBottom": "8px"}),
                    rx.hstack(
                        rx.text(a5["fit_score"], style={"fontFamily": "'Georgia', serif", "fontSize": "48px", "fontWeight": "900", "color": BLUE, "lineHeight": "1"}),
                        rx.text("/10", style={"fontSize": "16px", "color": TEXT_3}),
                        spacing="1",
                        align="end",
                    ),
                    style={"padding": "22px", "background": BLUE_BG, "borderRadius": "10px", "border": "1px solid rgba(27,72,196,0.15)", "flex": "1"},
                ),
                rx.box(
                    rx.text("Execution Confidence", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": GOLD, "marginBottom": "8px"}),
                    rx.hstack(
                        rx.text(a5["execution_score"], style={"fontFamily": "'Georgia', serif", "fontSize": "48px", "fontWeight": "900", "color": GOLD, "lineHeight": "1"}),
                        rx.text("/10", style={"fontSize": "16px", "color": TEXT_3}),
                        spacing="1",
                        align="end",
                    ),
                    style={"padding": "22px", "background": GOLD_BG, "borderRadius": "10px", "border": "1px solid rgba(168,88,0,0.15)", "flex": "1"},
                ),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                StartupState.missing_roles.length() > 0,
                rx.vstack(
                    rx.text("Missing Roles", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                    rx.hstack(
                        rx.foreach(
                            StartupState.missing_roles,
                            lambda role: rx.box(
                                rx.text(role, style={"fontSize": "12px", "fontWeight": "600", "color": AMBER}),
                                style={"padding": "4px 11px", "background": AMBER_BG, "border": "1px solid rgba(146,64,14,0.2)", "borderRadius": "5px"},
                            ),
                        ),
                        wrap="wrap",
                        spacing="2",
                    ),
                    spacing="2",
                    align="start",
                ),
                rx.box(),
            ),
            rx.vstack(
                rx.text("Conclusion", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.text(a5["conclusion"], style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"}),
                spacing="1",
                align="start",
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        rx.text("Founder analysis not yet available.", style={"color": TEXT_3, "fontSize": "14px"}),
    )


# ── Recommendations tab ───────────────────────────────────────────────────────

def plan_item(item: str, accent: str) -> rx.Component:
    return rx.hstack(
        rx.text("›", style={"color": accent, "flexShrink": "0", "fontWeight": "800", "fontSize": "12px", "marginTop": "2px"}),
        rx.text(item, style={"fontSize": "13px", "color": TEXT_2, "lineHeight": "1.55"}),
        spacing="2",
        align="start",
        style={"padding": "9px 12px", "background": SURFACE_2, "borderRadius": "6px", "borderLeft": f"3px solid {accent}"},
    )


def recs_tab() -> rx.Component:
    a6 = StartupState.a6
    rec_bg = rx.match(
        a6["recommendation"],
        ("Continue", GREEN_BG),
        ("Refine", BLUE_BG),
        ("Pivot", AMBER_BG),
        RED_BG,
    )
    rec_color = rx.match(
        a6["recommendation"],
        ("Continue", GREEN),
        ("Refine", BLUE),
        ("Pivot", AMBER),
        RED,
    )
    return rx.cond(
        StartupState.a6.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.text("Recommendation", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                rx.box(
                    rx.text(a6["recommendation"], style={"fontSize": "13px", "fontWeight": "700", "color": rec_color}),
                    style={"padding": "5px 14px", "borderRadius": "6px", "background": rec_bg},
                ),
                spacing="3",
                align="center",
                style={"marginBottom": "24px"},
            ),
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.box(style={"width": "4px", "height": "18px", "background": BLUE, "borderRadius": "2px", "flexShrink": "0"}),
                        rx.text("30-Day Plan", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                        spacing="2",
                        align="center",
                        style={"marginBottom": "12px"},
                    ),
                    rx.vstack(
                        rx.foreach(StartupState.thirty_day_plan, lambda item: plan_item(item, BLUE)),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    spacing="0",
                    align="start",
                    flex="1",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.box(style={"width": "4px", "height": "18px", "background": GREEN, "borderRadius": "2px", "flexShrink": "0"}),
                        rx.text("90-Day Plan", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                        spacing="2",
                        align="center",
                        style={"marginBottom": "12px"},
                    ),
                    rx.vstack(
                        rx.foreach(StartupState.ninety_day_plan, lambda item: plan_item(item, GREEN)),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    spacing="0",
                    align="start",
                    flex="1",
                ),
                spacing="6",
                align="start",
                style={"marginBottom": "22px"},
            ),
            rx.cond(
                StartupState.pivots.length() > 0,
                rx.vstack(
                    rx.hstack(
                        rx.box(style={"width": "4px", "height": "18px", "background": AMBER, "borderRadius": "2px", "flexShrink": "0"}),
                        rx.text("Pivot Options", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_3}),
                        spacing="2",
                        align="center",
                        style={"marginBottom": "12px"},
                    ),
                    rx.vstack(
                        rx.foreach(
                            StartupState.pivots,
                            lambda pivot: rx.box(
                                rx.text(pivot, style={"fontSize": "13px", "color": AMBER, "lineHeight": "1.6", "fontWeight": "500"}),
                                style={
                                    "padding": "13px 18px",
                                    "background": AMBER_BG,
                                    "border": "1px solid rgba(146,64,14,0.15)",
                                    "borderLeft": f"4px solid {AMBER}",
                                    "borderRadius": "0 8px 8px 0",
                                },
                            ),
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    spacing="0",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            spacing="0",
            align="start",
            width="100%",
        ),
        rx.text("Recommendations not yet available.", style={"color": TEXT_3, "fontSize": "14px"}),
    )


# ── Full page ─────────────────────────────────────────────────────────────────

def startup_page() -> rx.Component:
    a2 = StartupState.a2
    total_score = a2.get("total_score", 0)

    return page_layout(
        # Breadcrumb
        rx.hstack(
            rx.link("Dashboard", href="/", style={"color": BLUE, "fontSize": "13px", "fontWeight": "500", "textDecoration": "none"}),
            rx.text("/", style={"color": TEXT_4}),
            rx.link(
                StartupState.current_batch_id,
                href="/batch/" + StartupState.current_batch_id,
                style={"color": BLUE, "fontSize": "13px", "fontWeight": "500", "textDecoration": "none"},
            ),
            rx.text("/", style={"color": TEXT_4}),
            rx.text(StartupState.current_startup_name, style={"color": TEXT_2, "fontSize": "13px", "fontWeight": "500"}),
            spacing="2",
            align="center",
            style={"marginBottom": "28px"},
        ),

        # Hero card
        rx.box(
            # Decorative dot grid
            rx.box(style={
                "position": "absolute",
                "inset": "0",
                "backgroundImage": "radial-gradient(circle,rgba(255,255,255,0.08) 1px,transparent 1px)",
                "backgroundSize": "24px 24px",
                "pointerEvents": "none",
            }),
            # Content
            rx.hstack(
                rx.vstack(
                    rx.cond(
                        StartupState.a2.length() > 0,
                        verdict_badge(a2.get("verdict", ""), StartupState.verdict_color),
                        rx.box(),
                    ),
                    rx.text(
                        StartupState.current_startup_name,
                        style={"fontFamily": "'Georgia', serif", "fontSize": "42px", "fontWeight": "900", "color": "white", "letterSpacing": "-0.03em", "lineHeight": "1.05"},
                    ),
                    rx.cond(
                        StartupState.a1.length() > 0,
                        rx.text(
                            StartupState.a1["one_line_description"],
                            style={"fontSize": "16px", "color": "rgba(255,255,255,0.75)", "lineHeight": "1.6", "maxWidth": "540px"},
                        ),
                        rx.box(),
                    ),
                    spacing="3",
                    align="start",
                    flex="1",
                    style={"minWidth": "0"},
                ),
                rx.cond(
                    StartupState.a2.length() > 0,
                    rx.vstack(
                        rx.text("Composite Score", style={"fontSize": "12px", "fontWeight": "700", "letterSpacing": "0.1em", "textTransform": "uppercase", "color": "rgba(255,255,255,0.5)"}),
                        rx.hstack(
                            rx.text(
                                a2.get("total_score", 0),
                                style={"fontFamily": "'Georgia', serif", "fontSize": "80px", "fontWeight": "900", "color": "white", "lineHeight": "1", "letterSpacing": "-0.05em"},
                            ),
                            rx.text("/100", style={"fontSize": "20px", "color": "rgba(255,255,255,0.4)", "marginBottom": "6px"}),
                            spacing="1",
                            align="end",
                        ),
                        rx.box(
                            rx.box(
                                style={
                                    "height": "100%",
                                    "background": "white",
                                    "width": a2.get("total_score", 0).to(str) + "%",
                                    "borderRadius": "2px",
                                }
                            ),
                            style={"height": "4px", "width": "130px", "marginLeft": "auto", "background": "rgba(255,255,255,0.2)", "borderRadius": "2px", "overflow": "hidden", "marginTop": "6px"},
                        ),
                        spacing="1",
                        align="end",
                        flex_shrink="0",
                    ),
                    rx.box(),
                ),
                spacing="6",
                align="start",
                wrap="wrap",
                style={"position": "relative", "zIndex": "1"},
            ),
            # Summary blurb
            rx.cond(
                StartupState.a2.length() > 0,
                rx.cond(
                    a2.get("summary", ""),
                    rx.box(
                        rx.text(
                            a2.get("summary", ""),
                            style={"fontSize": "14px", "color": "rgba(255,255,255,0.85)", "lineHeight": "1.7"},
                        ),
                        style={
                            "position": "relative",
                            "zIndex": "1",
                            "marginTop": "24px",
                            "padding": "18px 22px",
                            "background": "rgba(255,255,255,0.1)",
                            "backdropFilter": "blur(4px)",
                            "borderRadius": "10px",
                            "border": "1px solid rgba(255,255,255,0.15)",
                        },
                    ),
                    rx.box(),
                ),
                rx.box(),
            ),
            style={
                "background": "linear-gradient(135deg,#1b48c4 0%,#2a5ad4 60%,#3b6fd4 100%)",
                "borderRadius": "16px",
                "padding": "40px 44px",
                "marginBottom": "20px",
                "position": "relative",
                "overflow": "hidden",
                "boxShadow": "0 8px 40px rgba(27,72,196,0.25)",
            },
        ),

        # Dimensions + SWOT
        rx.hstack(
            # Radar chart
            rx.cond(
                StartupState.a2.length() > 0,
                rx.box(
                    section_marker("Dimension Scores"),
                    radar_chart(StartupState.radar_data, height=280),
                    style={
                        "background": SURFACE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "28px",
                        "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
                        "flex": "1",
                    },
                ),
                rx.box(),
            ),
            # SWOT
            rx.cond(
                StartupState.a2.length() > 0,
                rx.box(
                    section_marker("SWOT Analysis"),
                    rx.hstack(
                        rx.vstack(
                            swot_panel(StartupState.swot_strengths, "Strengths", GREEN_BG, GREEN, "+"),
                            swot_panel(StartupState.swot_weaknesses, "Weaknesses", RED_BG, RED, "−"),
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            swot_panel(StartupState.swot_opportunities, "Opportunities", BLUE_BG, BLUE, "›"),
                            swot_panel(StartupState.swot_threats, "Threats", AMBER_BG, AMBER, "!"),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="2",
                        style={"marginTop": "22px"},
                    ),
                    style={
                        "background": SURFACE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "28px",
                        "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
                        "flex": "1",
                    },
                ),
                rx.box(),
            ),
            spacing="4",
            style={"marginBottom": "20px"},
        ),

        # Analyst tabs
        rx.box(
            # Tab bar
            rx.hstack(
                tab_button("Market", "market"),
                tab_button("Product", "product"),
                tab_button("Founder", "founder"),
                tab_button("Recommendations", "recs"),
                spacing="0",
                style={
                    "borderBottom": f"1px solid {BORDER}",
                    "padding": "0 28px",
                    "background": SURFACE_2,
                    "borderRadius": "12px 12px 0 0",
                    "overflowX": "auto",
                },
            ),
            # Tab content
            rx.box(
                rx.cond(StartupState.active_tab == "market", market_tab(), rx.box()),
                rx.cond(StartupState.active_tab == "product", product_tab(), rx.box()),
                rx.cond(StartupState.active_tab == "founder", founder_tab(), rx.box()),
                rx.cond(StartupState.active_tab == "recs", recs_tab(), rx.box()),
                style={"padding": "28px"},
            ),
            style={
                "background": SURFACE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
            },
        ),
    )

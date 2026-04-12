"""Roadmap detail pages — one static page per feature card."""

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
TEAL_BG = "rgba(20,184,166,0.08)"
PURPLE = "#7c3aed"
PURPLE_BG = "rgba(147,51,234,0.08)"
ROSE = "#be185d"
ROSE_BG = "#fce7f3"
RED = "#b91c1c"
RED_BG = "#fee2e2"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_3 = "#7188a4"
SURFACE = "#ffffff"
BORDER = "#dce3f0"
SURFACE_2 = "#f0f4fb"


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _breadcrumb() -> rx.Component:
    return rx.link(
        "← Roadmap",
        href="/roadmap",
        style={
            "fontSize": "13px",
            "fontWeight": "600",
            "color": TEXT_3,
            "textDecoration": "none",
            "marginBottom": "32px",
            "display": "inline-block",
            "_hover": {"color": BLUE},
        },
    )


def _page_header(
    icon_html: str,
    icon_bg: str,
    icon_border: str,
    label: str,
    title: str,
) -> rx.Component:
    return rx.vstack(
        _breadcrumb(),
        section_marker(label),
        rx.hstack(
            rx.box(
                rx.html(icon_html),
                style={
                    "width": "52px",
                    "height": "52px",
                    "background": icon_bg,
                    "border": f"1px solid {icon_border}",
                    "borderRadius": "12px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "flexShrink": "0",
                },
            ),
            rx.text(
                title,
                style={
                    "fontFamily": "'Georgia', serif",
                    "fontSize": "34px",
                    "fontWeight": "900",
                    "color": TEXT,
                    "letterSpacing": "-0.03em",
                    "lineHeight": "1.05",
                },
            ),
            spacing="4",
            align="center",
        ),
        spacing="3",
        align="start",
        style={"marginBottom": "40px"},
    )


def _unlock_item(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            style={
                "width": "6px",
                "height": "6px",
                "background": BLUE,
                "borderRadius": "50%",
                "flexShrink": "0",
                "marginTop": "6px",
            }
        ),
        rx.text(text, style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.6"}),
        spacing="3",
        align="start",
    )


def _unlocks_section(items: list) -> rx.Component:
    return rx.box(
        rx.text(
            "What this unlocks",
            style={
                "fontSize": "13px",
                "fontWeight": "700",
                "color": TEXT_3,
                "letterSpacing": "0.06em",
                "textTransform": "uppercase",
                "marginBottom": "16px",
            },
        ),
        rx.vstack(
            *[_unlock_item(item) for item in items],
            spacing="2",
            align="start",
        ),
        style={
            "padding": "24px",
            "background": SURFACE_2,
            "border": f"1px solid {BORDER}",
            "borderRadius": "10px",
            "marginTop": "32px",
        },
    )


# ── Page 1: Analyst Profiles ───────────────────────────────────────────────────

def analyst_profiles_page() -> rx.Component:
    profile_mockup = rx.vstack(
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.text("J", style={"fontFamily": "'Georgia', serif", "fontSize": "16px", "fontWeight": "900", "color": "white"}),
                        style={"width": "40px", "height": "40px", "borderRadius": "50%", "background": BLUE, "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                    ),
                    rx.vstack(
                        rx.text("Jordan Mills", style={"fontSize": "14px", "fontWeight": "700", "color": TEXT}),
                        rx.text("Senior Analyst", style={"fontSize": "11px", "color": TEXT_3}),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.vstack(
                    rx.text("47", style={"fontFamily": "'Georgia', serif", "fontSize": "22px", "fontWeight": "900", "color": BLUE}),
                    rx.text("evals", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                    spacing="0",
                    align="end",
                ),
                justify="between",
                align="start",
                width="100%",
                style={"marginBottom": "18px"},
            ),
            rx.box(style={"height": "1px", "background": BORDER, "marginBottom": "18px"}),
            rx.hstack(
                *[rx.vstack(
                    rx.text(val, style={"fontFamily": "'Georgia', serif", "fontSize": "20px", "fontWeight": "900", "color": clr}),
                    rx.text(label, style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                    spacing="0",
                    align="center",
                ) for val, clr, label in [
                    ("68.4", TEXT, "Avg Score"),
                    ("8", GREEN, "VC Picks"),
                    ("2", PURPLE, "Invested"),
                    ("91%", AMBER, "Accuracy"),
                ]],
                justify="between",
                width="100%",
                style={"marginBottom": "18px"},
            ),
            rx.box(style={"height": "1px", "background": BORDER, "marginBottom": "14px"}),
            rx.text("Recent Deals", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "10px"}),
            rx.el.table(
                rx.el.thead(rx.el.tr(
                    *[rx.el.th(h, style={"textAlign": "left", "fontSize": "9px", "color": TEXT_3, "paddingBottom": "6px", "fontWeight": "700", "letterSpacing": "0.06em", "textTransform": "uppercase", "paddingRight": "16px"})
                      for h in ["Startup", "Batch", "Score", "Verdict"]],
                )),
                rx.el.tbody(
                    *[rx.el.tr(
                        rx.el.td(name, style={"fontSize": "12px", "color": TEXT, "padding": "4px 0", "fontWeight": "600", "paddingRight": "16px"}),
                        rx.el.td(batch, style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "paddingRight": "16px"}),
                        rx.el.td(score, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": sc, "fontWeight": "700", "paddingRight": "16px"}),
                        rx.el.td(verdict, style={"fontSize": "11px", "color": vc, "fontWeight": "600"}),
                    ) for name, batch, score, verdict, sc, vc in [
                        ("NeuralPath", "Batch 4", "84", "Top VC", GREEN, GREEN),
                        ("DataBridge", "Batch 4", "71", "Promising", BLUE, BLUE),
                        ("QueueFlow", "Batch 3", "58", "Promising", BLUE, BLUE),
                        ("CloudMesh", "Batch 3", "42", "Reject", RED, RED),
                        ("AquaLogic", "Batch 2", "77", "Top VC", GREEN, GREEN),
                    ]],
                ),
                style={"width": "100%", "borderCollapse": "collapse"},
            ),
            style={"padding": "22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.box(
            rx.text("Team Leaderboard", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "12px"}),
            rx.vstack(
                *[rx.hstack(
                    rx.text(f"#{rank}", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": TEXT_3, "width": "24px"}),
                    rx.box(
                        rx.text(initial, style={"fontFamily": "'Georgia', serif", "fontSize": "10px", "fontWeight": "900", "color": "white"}),
                        style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": bg, "display": "flex", "alignItems": "center", "justifyContent": "center"},
                    ),
                    rx.text(name, style={"fontSize": "13px", "fontWeight": "600", "color": TEXT, "flex": "1"}),
                    rx.text(evals, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": TEXT_3}),
                    rx.text(avg, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": BLUE, "fontWeight": "700"}),
                    spacing="3",
                    align="center",
                    width="100%",
                ) for rank, initial, name, evals, avg, bg in [
                    (1, "J", "Jordan M.", "47 evals", "68.4", BLUE),
                    (2, "S", "Sara L.", "31 evals", "64.1", PURPLE),
                    (3, "M", "Marc D.", "28 evals", "61.7", TEAL),
                ]],
                spacing="3",
                align="start",
            ),
            style={"padding": "18px 22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="#1b48c4" stroke-width="1.5"/><path d="M3 18c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="#1b48c4" stroke-width="1.5" stroke-linecap="round"/></svg>',
            BLUE_BG, "rgba(27,72,196,0.2)",
            "Coming Feature",
            "Analyst Profiles",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "Give every analyst their own account, dashboard, and performance history.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Today, all evaluations run under a single system identity. When a startup "
                    "gets flagged as a Top VC Candidate, you can't easily tell who sourced it, "
                    "who evaluated it, or whether their scoring has drifted over time.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Analyst Profiles adds individual logins, personal eval histories, "
                    "and a live leaderboard — so your best dealmakers get credit and your "
                    "team can calibrate together.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Each profile tracks score distributions, verdict accuracy over time, "
                    "and deal outcomes — giving your fund a data-backed view of sourcing "
                    "quality that compounds across every batch.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "Per-analyst attribution on every evaluation and verdict",
                    "Performance trending — see if scoring calibration improves over time",
                    "Sourcing transparency for LP reporting and internal accountability",
                    "Team leaderboard to gamify deal quality across your VC team",
                ]),
                spacing="0",
                align="start",
            ),
            profile_mockup,
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )


# ── Page 2: Deal Flow Pipeline ─────────────────────────────────────────────────

def deal_flow_page() -> rx.Component:
    kanban_mockup = rx.vstack(
        rx.box(
            rx.hstack(
                *[rx.hstack(
                    rx.text(col, style={"fontSize": "10px", "fontWeight": "700", "color": clr, "letterSpacing": "0.05em", "textTransform": "uppercase"}),
                    rx.box(
                        rx.text(str(cnt), style={"fontSize": "9px", "fontWeight": "700", "color": "white"}),
                        style={"width": "17px", "height": "17px", "borderRadius": "50%", "background": clr, "display": "flex", "alignItems": "center", "justifyContent": "center"},
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                ) for col, clr, cnt in [
                    ("Submitted", "#7a90a4", 8),
                    ("Shortlisted", BLUE, 5),
                    ("Due Dil.", GOLD, 3),
                    ("Invested", GREEN, 2),
                ]],
                style={"marginBottom": "12px"},
            ),
            rx.hstack(
                *[rx.vstack(
                    *[rx.box(
                        rx.text(name, style={"fontSize": "11px", "fontWeight": "700", "color": TEXT, "marginBottom": "4px"}),
                        rx.hstack(
                            rx.text(sector, style={"fontSize": "9px", "color": clr, "fontWeight": "600"}),
                            rx.text(score, style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": TEXT_3}),
                            spacing="2",
                        ),
                        style={
                            "padding": "10px 12px",
                            "background": card_bg,
                            "border": f"1px solid {clr}33",
                            "borderRadius": "6px",
                            "width": "100%",
                        },
                    ) for name, sector, score in cards],
                    spacing="2",
                    align="start",
                    flex="1",
                    style={"minWidth": "0"},
                ) for _col, clr, card_bg, cards in [
                    ("col1", "#7a90a4", "#f4f6fb", [
                        ("NeuralPath AI", "Deep Tech", "score: —"),
                        ("DataBridge", "B2B SaaS", "score: —"),
                        ("CloudMesh", "Infra", "score: —"),
                    ]),
                    ("col2", BLUE, BLUE_BG, [
                        ("AquaLogic", "Climate", "74 pts"),
                        ("QueueFlow", "Ops", "68 pts"),
                    ]),
                    ("col3", GOLD, GOLD_BG, [
                        ("ByteShift", "AI/ML", "81 pts"),
                        ("Synapse", "Health", "77 pts"),
                    ]),
                    ("col4", GREEN, GREEN_BG, [
                        ("NeuralPath", "Deep Tech", "84 pts"),
                    ]),
                ]],
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "20px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.hstack(
            *[rx.hstack(
                rx.box(style={"width": "8px", "height": "8px", "borderRadius": "2px", "background": clr}),
                rx.text(label, style={"fontSize": "11px", "color": TEXT_3, "fontWeight": "500"}),
                spacing="2",
                align="center",
            ) for clr, label in [
                ("#7a90a4", "8 submitted"),
                (BLUE, "5 shortlisted"),
                (GOLD, "3 in due dil."),
                (GREEN, "2 invested"),
            ]],
            spacing="5",
            style={"padding": "12px 20px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="4" width="4" height="12" rx="1" stroke="#a85800" stroke-width="1.5"/><rect x="8" y="6" width="4" height="10" rx="1" stroke="#a85800" stroke-width="1.5"/><rect x="14.5" y="2" width="4" height="14" rx="1" stroke="#a85800" stroke-width="1.5"/></svg>',
            GOLD_BG, "rgba(168,88,0,0.2)",
            "Coming Feature",
            "Deal Flow Pipeline",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "A visual Kanban board that moves every startup from Submitted to Invested.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Right now, deals live in spreadsheets and scattered email threads. When a "
                    "batch finishes, you know who scored well — but tracking what happens next "
                    "is entirely manual.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Deal Flow Pipeline gives your team a shared board where every startup "
                    "moves through stage gates: Submitted → Shortlisted → Due Diligence → Invested. "
                    "EvalBot scores auto-populate; analysts drag cards forward.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Nothing falls through the cracks. Every promising company is visible, "
                    "every decision is timestamped, and your fund's decision velocity becomes "
                    "a measurable metric.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "Visual pipeline so every team member sees deal status at a glance",
                    "Stage-gate workflow with timestamps and assigned reviewer",
                    "Nothing slips — shortlisted companies never go cold unnoticed",
                    "Pipeline velocity metrics: avg days from submission to decision",
                ]),
                spacing="0",
                align="start",
            ),
            kanban_mockup,
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1.2fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )


# ── Page 3: Portfolio Tracking ─────────────────────────────────────────────────

def portfolio_tracking_page() -> rx.Component:
    portfolio_mockup = rx.vstack(
        rx.box(
            rx.text("Portfolio Companies", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "14px"}),
            rx.el.table(
                rx.el.thead(rx.el.tr(
                    *[rx.el.th(h, style={"textAlign": "left", "fontSize": "9px", "color": TEXT_3, "paddingBottom": "8px", "fontWeight": "700", "letterSpacing": "0.06em", "textTransform": "uppercase", "paddingRight": "12px"})
                      for h in ["Company", "Sector", "Invested", "Status", "Last Eval", "Score"]],
                )),
                rx.el.tbody(
                    *[rx.el.tr(
                        rx.el.td(name, style={"fontSize": "12px", "color": TEXT, "padding": "5px 0", "fontWeight": "700", "paddingRight": "12px"}),
                        rx.el.td(sector, style={"fontSize": "11px", "color": TEXT_3, "paddingRight": "12px"}),
                        rx.el.td(date, style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "paddingRight": "12px"}),
                        rx.el.td(
                            rx.box(
                                rx.text(status, style={"fontSize": "9px", "fontWeight": "700", "color": sclr}),
                                style={"padding": "2px 7px", "background": sbg, "borderRadius": "3px", "display": "inline-flex"},
                            ),
                            style={"paddingRight": "12px"},
                        ),
                        rx.el.td(last_eval, style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "paddingRight": "12px"}),
                        rx.el.td(
                            rx.hstack(
                                rx.text(score, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": score_clr, "fontWeight": "700"}),
                                rx.box(
                                    rx.box(style={"height": "100%", "borderRadius": "1px", "background": score_clr, "width": bar_w}),
                                    style={"width": "40px", "height": "3px", "background": "#e5ecf7", "borderRadius": "1px", "overflow": "hidden"},
                                ),
                                spacing="2",
                                align="center",
                            ),
                        ),
                    ) for name, sector, date, status, sbg, sclr, last_eval, score, score_clr, bar_w in [
                        ("NeuralPath", "Deep Tech", "Jan '24", "Growing", GREEN_BG, GREEN, "Q1 '25", "84", GREEN, "84%"),
                        ("AquaLogic", "Climate", "Mar '24", "Growing", GREEN_BG, GREEN, "Q1 '25", "74", BLUE, "74%"),
                        ("ByteShift", "AI/ML", "Jun '24", "On Track", BLUE_BG, BLUE, "Q4 '24", "71", BLUE, "71%"),
                        ("Synapse", "Health", "Aug '24", "Pivoting", GOLD_BG, GOLD, "Q4 '24", "67", GOLD, "67%"),
                        ("CloudMesh", "Infra", "Oct '24", "At Risk", RED_BG, RED, "Q1 '25", "48", RED, "48%"),
                        ("QueueFlow", "Ops", "Jan '25", "On Track", BLUE_BG, BLUE, "Q1 '25", "61", BLUE, "61%"),
                    ]],
                ),
                style={"width": "100%", "borderCollapse": "collapse"},
            ),
            style={"padding": "22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.hstack(
            *[rx.vstack(
                rx.text(val, style={"fontFamily": "'Georgia', serif", "fontSize": "22px", "fontWeight": "900", "color": clr}),
                rx.text(label, style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="0",
                align="center",
            ) for val, clr, label in [
                ("6", BLUE, "Portfolio co."),
                ("3", GREEN, "Growing"),
                ("1", GOLD, "Pivoting"),
                ("1", RED, "At risk"),
                ("68.4", BLUE, "Avg score"),
            ]],
            justify="between",
            width="100%",
            style={"padding": "16px 22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><polyline points="2,16 6.5,9.5 10.5,12.5 18,5" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="13,5 18,5 18,10" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            GREEN_BG, "rgba(10,124,82,0.2)",
            "Coming Feature",
            "Portfolio Tracking",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "Track every invested company post-close with quarterly re-evaluation triggers.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Closing a deal is the beginning, not the end. Today, once a startup "
                    "leaves the evaluation pipeline, it disappears from EvalBot's view "
                    "entirely. Portfolio monitoring is manual, ad-hoc, and inconsistent.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Portfolio Tracking brings every invested company into a structured "
                    "post-close view. Updated pitch materials trigger automatic re-evaluation "
                    "each quarter — so score drift, pivot signals, and red flags surface "
                    "before they become problems.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Status badges (Growing, On Track, Pivoting, At Risk) are assigned by "
                    "the analyst and updated each review cycle, giving your fund a live "
                    "health dashboard across the entire portfolio.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "Post-close tracking alongside pre-investment evaluation in one system",
                    "Quarterly re-evaluation triggers with automatic score updates",
                    "Early warning system — At Risk status visible across the team",
                    "Portfolio health summary for LP updates and board reporting",
                ]),
                spacing="0",
                align="start",
            ),
            portfolio_mockup,
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1.3fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )


# ── Page 4: Automated Reports ──────────────────────────────────────────────────

def automated_reports_page() -> rx.Component:
    report_mockup = rx.vstack(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.box(style={"width": "28px", "height": "28px", "background": PURPLE, "borderRadius": "6px"}),
                    rx.text("EvalBot Report", style={"fontFamily": "'Georgia', serif", "fontSize": "15px", "fontWeight": "900", "color": TEXT, "letterSpacing": "-0.02em"}),
                    rx.text("Batch 12 · April 2025", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                    spacing="2",
                    align="start",
                ),
                rx.box(
                    rx.text("Q2 2025", style={"fontSize": "9px", "fontWeight": "700", "color": PURPLE}),
                    style={"padding": "3px 8px", "background": PURPLE_BG, "border": "1px solid rgba(147,51,234,0.15)", "borderRadius": "4px"},
                ),
                justify="between",
                align="start",
                width="100%",
                style={"marginBottom": "18px"},
            ),
            rx.hstack(
                *[rx.vstack(
                    rx.text(val, style={"fontFamily": "'Georgia', serif", "fontSize": "20px", "fontWeight": "900", "color": clr}),
                    rx.text(label, style={"fontSize": "9px", "color": TEXT_3, "fontWeight": "600", "textAlign": "center"}),
                    spacing="0",
                    align="center",
                ) for val, clr, label in [
                    ("18", BLUE, "Startups"),
                    ("64.2", BLUE, "Avg Score"),
                    ("5", GREEN, "VC Picks"),
                    ("2", PURPLE, "Invested"),
                ]],
                justify="between",
                width="100%",
                style={"padding": "14px 0", "borderTop": f"1px solid {BORDER}", "borderBottom": f"1px solid {BORDER}", "marginBottom": "16px"},
            ),
            rx.text("Top Performers", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "10px"}),
            rx.vstack(
                *[rx.hstack(
                    rx.text(f"#{i + 1}", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "width": "20px"}),
                    rx.text(name, style={"fontSize": "12px", "fontWeight": "700", "color": TEXT, "flex": "1"}),
                    rx.text(score, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": GREEN, "fontWeight": "700"}),
                    spacing="3",
                    align="center",
                    width="100%",
                ) for i, (name, score) in enumerate([
                    ("NeuralPath AI", "84"),
                    ("ByteShift", "81"),
                    ("AquaLogic", "74"),
                ])],
                spacing="2",
                align="start",
            ),
            style={"padding": "22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.box(
            rx.text("Scheduled Delivery", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "14px"}),
            rx.vstack(
                rx.hstack(
                    rx.text("Frequency", style={"fontSize": "12px", "color": TEXT_2, "width": "90px"}),
                    rx.hstack(
                        *[rx.box(
                            rx.text(day, style={"fontSize": "10px", "fontWeight": "600", "color": clr}),
                            style={"padding": "4px 10px", "background": bg, "border": f"1px solid {bdr}", "borderRadius": "4px"},
                        ) for day, clr, bg, bdr in [
                            ("Mon", "white", BLUE, BLUE),
                            ("Fri", TEXT_3, SURFACE_2, BORDER),
                        ]],
                        spacing="2",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.hstack(
                    rx.text("Recipients", style={"fontSize": "12px", "color": TEXT_2, "width": "90px"}),
                    rx.hstack(
                        *[rx.box(
                            rx.text(r, style={"fontSize": "10px", "color": TEXT_3}),
                            style={"padding": "3px 8px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "3px"},
                        ) for r in ["lp@fund.com", "+3 more"]],
                        spacing="2",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.hstack(
                    rx.text("Format", style={"fontSize": "12px", "color": TEXT_2, "width": "90px"}),
                    rx.hstack(
                        *[rx.box(
                            rx.text(fmt, style={"fontSize": "10px", "fontWeight": "600", "color": clr}),
                            style={"padding": "4px 10px", "background": bg, "border": f"1px solid {bdr}", "borderRadius": "4px"},
                        ) for fmt, clr, bg, bdr in [
                            ("PDF", "white", PURPLE, PURPLE),
                            ("Email", TEXT_3, SURFACE_2, BORDER),
                        ]],
                        spacing="2",
                    ),
                    spacing="3",
                    align="center",
                ),
                spacing="4",
                align="start",
            ),
            style={"padding": "18px 22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><rect x="3.5" y="1.5" width="13" height="17" rx="2" stroke="#7c3aed" stroke-width="1.5"/><line x1="7" y1="7" x2="13" y2="7" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><line x1="7" y1="10" x2="13" y2="10" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><line x1="7" y1="13" x2="11" y2="13" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/></svg>',
            PURPLE_BG, "rgba(147,51,234,0.2)",
            "Coming Feature",
            "Automated Reports",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "One-click PDF export and scheduled email delivery to LPs and partners.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Every batch currently produces a batch_summary.md in the output folder. "
                    "Turning that into an LP-ready document means manual copy-paste, formatting "
                    "in Notion or Google Docs, and then a separate email send.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Automated Reports generates a polished, branded PDF — cover page, "
                    "key stats, top performers, full batch verdicts — with a single click. "
                    "Schedule delivery to any email list on any cadence.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "The report format is designed for LPs: clean, scannable, "
                    "no raw AI output visible. Partners see curated insights. "
                    "Your team keeps the detailed breakdown in EvalBot.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "LP-ready PDF export with branded cover page and key metrics",
                    "Scheduled delivery — set it once, goes out every Monday at 9am",
                    "Recipient lists with CC/BCC for partners, LPs, and board members",
                    "No manual formatting — zero time between batch finish and report out",
                ]),
                spacing="0",
                align="start",
            ),
            report_mockup,
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )


# ── Page 5: Partner API ────────────────────────────────────────────────────────

def partner_api_page() -> rx.Component:
    api_mockup = rx.vstack(
        rx.box(
            rx.hstack(
                rx.hstack(
                    *[rx.box(style={"width": "10px", "height": "10px", "borderRadius": "50%", "background": clr})
                      for clr in ["#ff5f56", "#ffbd2e", "#27c93f"]],
                    spacing="2",
                ),
                rx.text("evalbot-api / v1", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.4)"}),
                justify="between",
                align="center",
                width="100%",
                style={"marginBottom": "16px"},
            ),
            rx.text("# 1. Submit a pitch for evaluation", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.3)", "marginBottom": "4px"}),
            rx.text("POST /api/v1/evaluate", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": "#4a9eff", "marginBottom": "2px"}),
            rx.text("Authorization: Bearer sk-evalbot-...", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.5)", "marginBottom": "2px"}),
            rx.text('{ "startup": "Acme AI", "pitch_url": "https://..." }', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#c8d8f0", "marginBottom": "10px"}),
            rx.text('→ 202 Accepted  { "job_id": "eval_9f3a2c" }', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#0ec97a", "marginBottom": "16px"}),
            rx.text("# 2. Poll job status", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.3)", "marginBottom": "4px"}),
            rx.text("GET /api/v1/jobs/eval_9f3a2c", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": "#4a9eff", "marginBottom": "2px"}),
            rx.text('→ 200 OK  { "status": "running", "progress": "4/7" }', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#0ec97a", "marginBottom": "16px"}),
            rx.text("# 3. Fetch results when complete", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.3)", "marginBottom": "4px"}),
            rx.text("GET /api/v1/jobs/eval_9f3a2c/result", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": "#4a9eff", "marginBottom": "2px"}),
            rx.text("→ 200 OK", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#0ec97a", "marginBottom": "2px"}),
            rx.text('{ "score": 74, "verdict": "Promising",', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#c8d8f0", "marginBottom": "2px"}),
            rx.text('  "swot": {...}, "recommendations": [...] }', style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "#c8d8f0"}),
            style={"padding": "20px", "background": "#0d1a2e", "border": "1px solid rgba(255,255,255,0.06)", "borderRadius": "10px"},
        ),
        rx.box(
            rx.text("How it works", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "14px"}),
            rx.hstack(
                *[rx.hstack(
                    rx.vstack(
                        rx.box(
                            rx.text(num, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "fontWeight": "700", "color": "white"}),
                            style={"width": "28px", "height": "28px", "borderRadius": "50%", "background": TEAL, "display": "flex", "alignItems": "center", "justifyContent": "center"},
                        ),
                        rx.text(label, style={"fontSize": "11px", "fontWeight": "600", "color": TEXT, "textAlign": "center"}),
                        rx.text(sub, style={"fontSize": "9px", "color": TEXT_3, "textAlign": "center"}),
                        spacing="2",
                        align="center",
                    ),
                    *([] if i == 2 else [rx.text("→", style={"color": TEXT_3, "fontSize": "14px", "marginTop": "2px"})]),
                    spacing="3",
                    align="start",
                ) for i, (num, label, sub) in enumerate([
                    ("1", "Submit Pitch", "POST /evaluate"),
                    ("2", "EvalBot Runs", "7 agents ~2 min"),
                    ("3", "Get Results", "Score + SWOT + Recs"),
                ])],
                spacing="0",
                justify="between",
                width="100%",
            ),
            style={"padding": "18px 22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><path d="M8 6H4a2 2 0 00-2 2v6a2 2 0 002 2h8a2 2 0 002-2v-4" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/><rect x="9" y="3" width="9" height="9" rx="2" stroke="#0d9488" stroke-width="1.5"/></svg>',
            TEAL_BG, "rgba(20,184,166,0.2)",
            "Coming Feature",
            "Partner API",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "Founders submit pitches directly via REST API. Scores and verdicts return automatically.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Today, every pitch goes through manual file upload or a batch directory scan. "
                    "For high-volume deal flow or accelerator programs, this bottleneck limits "
                    "how fast your fund can process submissions.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "The Partner API lets founders (or application platforms) submit pitches "
                    "directly. A webhook fires when evaluation completes. Your portal receives "
                    "structured JSON with score, verdict, SWOT, and recommendations — "
                    "no human in the loop.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Authentication uses per-partner API keys with rate limiting. "
                    "Every API call is logged against the key owner, so you can track "
                    "submission volume by source.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "Self-serve founder submission — no manual intake required",
                    "Webhook callbacks so your platform gets notified when results are ready",
                    "Per-partner API keys with usage quotas and audit logs",
                    "Structured JSON output compatible with your existing deal tools",
                ]),
                spacing="0",
                align="start",
            ),
            api_mockup,
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )


# ── Page 6: Cohort Analytics ───────────────────────────────────────────────────

def cohort_analytics_page() -> rx.Component:
    bar_data = [
        ("B1", 59, "#7a90a4"),
        ("B2", 63, BLUE),
        ("B3", 61, "#7a90a4"),
        ("B4", 66, BLUE),
        ("B5", 64, BLUE),
        ("B6", 68, GREEN),
    ]
    chart_h = 80
    bar_w = 28
    gap = 14
    x_start = 24
    bars_svg = ""
    for i, (label, score, color) in enumerate(bar_data):
        x = x_start + i * (bar_w + gap)
        bar_height = int(score * chart_h / 100)
        y = chart_h - bar_height
        bars_svg += f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_height}" rx="3" fill="{color}"/>'
        bars_svg += f'<text x="{x + bar_w // 2}" y="{y - 4}" text-anchor="middle" font-family="Courier New" font-size="9" fill="#374f6a" font-weight="700">{score}</text>'
        bars_svg += f'<text x="{x + bar_w // 2}" y="{chart_h + 14}" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="9" fill="#7188a4">{label}</text>'
    total_w = x_start + len(bar_data) * (bar_w + gap) + 10
    svg_html = f'<svg width="100%" viewBox="0 0 {total_w} {chart_h + 22}" fill="none" xmlns="http://www.w3.org/2000/svg"><line x1="0" y1="{chart_h}" x2="{total_w}" y2="{chart_h}" stroke="#dce3f0" stroke-width="1"/>{bars_svg}</svg>'

    verdict_dist = [
        ("Top VC Candidate", GREEN, "18%"),
        ("Promising", BLUE, "31%"),
        ("Needs Work", GOLD, "29%"),
        ("Reject", RED, "22%"),
    ]

    analytics_mockup = rx.vstack(
        rx.box(
            rx.text("Avg Score Trend by Batch", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "14px"}),
            rx.html(svg_html),
            style={"padding": "20px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.box(
            rx.text("Verdict Distribution (All Batches)", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "14px"}),
            rx.box(
                *[rx.box(style={"flex": pct, "background": clr, "height": "100%"}) for _, clr, pct in verdict_dist],
                style={"display": "flex", "height": "10px", "borderRadius": "5px", "overflow": "hidden", "marginBottom": "12px"},
            ),
            rx.hstack(
                *[rx.hstack(
                    rx.box(style={"width": "8px", "height": "8px", "borderRadius": "2px", "background": clr, "flexShrink": "0"}),
                    rx.text(f"{lbl} {pct}", style={"fontSize": "10px", "color": TEXT_2, "fontWeight": "500"}),
                    spacing="2",
                    align="center",
                ) for lbl, clr, pct in verdict_dist],
                wrap="wrap",
                spacing="4",
            ),
            style={"padding": "18px 20px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.box(
            rx.text("Sector Breakdown (All Batches)", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "14px"}),
            rx.el.table(
                rx.el.thead(rx.el.tr(
                    *[rx.el.th(h, style={"textAlign": "left", "fontSize": "9px", "color": TEXT_3, "paddingBottom": "7px", "fontWeight": "700", "letterSpacing": "0.06em", "textTransform": "uppercase", "paddingRight": "16px"})
                      for h in ["Sector", "Submissions", "Avg Score", "VC Rate"]],
                )),
                rx.el.tbody(
                    *[rx.el.tr(
                        rx.el.td(sector, style={"fontSize": "12px", "color": TEXT, "padding": "4px 0", "fontWeight": "600", "paddingRight": "16px"}),
                        rx.el.td(count, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": TEXT_3, "paddingRight": "16px"}),
                        rx.el.td(avg, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": sc, "fontWeight": "700", "paddingRight": "16px"}),
                        rx.el.td(vc_rate, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": BLUE, "fontWeight": "600"}),
                    ) for sector, count, avg, vc_rate, sc in [
                        ("AI / ML", "24", "67.4", "29%", BLUE),
                        ("B2B SaaS", "19", "63.1", "21%", BLUE),
                        ("Deep Tech", "11", "71.2", "36%", GREEN),
                        ("Climate", "8", "69.8", "25%", GREEN),
                        ("Health", "7", "58.4", "14%", GOLD),
                        ("Other", "15", "55.9", "7%", GOLD),
                    ]],
                ),
                style={"width": "100%", "borderCollapse": "collapse"},
            ),
            style={"padding": "18px 20px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="13" width="3.5" height="5.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/><rect x="8" y="9" width="3.5" height="9.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/><rect x="14.5" y="5" width="3.5" height="13.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/></svg>',
            GOLD_BG, "rgba(168,88,0,0.2)",
            "Coming Feature",
            "Cohort Analytics",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "Cross-batch trend charts: scoring patterns, verdict shifts, and sector concentration across every cohort.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Each batch produces a snapshot of startups evaluated at one point in time. "
                    "But the real signal emerges across batches: is your average score drifting up "
                    "or down? Are you seeing more AI wrappers? Is one sector consistently "
                    "outperforming?",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "Cohort Analytics aggregates all historical batches into a unified view. "
                    "Score trend lines reveal calibration drift in your AI agents. Verdict "
                    "distribution shifts show whether your deal flow quality is improving. "
                    "Sector tables surface where you're over- or under-indexed.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "This is the layer that turns EvalBot from a batch tool into a "
                    "fund-level intelligence system — one that compounds knowledge "
                    "with every evaluation cycle.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "Score trend analysis — detect AI calibration drift before it impacts decisions",
                    "Verdict distribution shifts — see if deal quality is improving across batches",
                    "Sector concentration table — know where your fund is over-indexed",
                    "Batch-vs-batch comparison to benchmark each cohort against historical averages",
                ]),
                spacing="0",
                align="start",
            ),
            analytics_mockup,
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1.1fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )


# ── Page 7: Founder Portal ─────────────────────────────────────────────────────

def founder_portal_page() -> rx.Component:
    # Left panel: founder's own view (full access to their results)
    founder_view = rx.vstack(
        # Header: who is logged in
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.text("A", style={"fontFamily": "'Georgia', serif", "fontSize": "14px", "fontWeight": "900", "color": "white"}),
                    style={"width": "36px", "height": "36px", "borderRadius": "8px", "background": ROSE, "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                ),
                rx.vstack(
                    rx.text("Acme AI", style={"fontSize": "14px", "fontWeight": "700", "color": TEXT}),
                    rx.text("Founder · acme@acme.io", style={"fontSize": "11px", "color": TEXT_3}),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            rx.box(
                rx.text("Logged in", style={"fontSize": "10px", "fontWeight": "700", "color": GREEN}),
                style={"padding": "3px 9px", "background": GREEN_BG, "border": "1px solid rgba(10,124,82,0.2)", "borderRadius": "4px"},
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        rx.box(style={"height": "1px", "background": BORDER, "margin": "16px 0"}),
        # Score + verdict row
        rx.hstack(
            rx.vstack(
                rx.text("74", style={"fontFamily": "'Georgia', serif", "fontSize": "36px", "fontWeight": "900", "color": BLUE, "lineHeight": "1"}),
                rx.text("Your Score", style={"fontSize": "11px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="1",
                align="center",
            ),
            rx.box(style={"width": "1px", "background": BORDER, "height": "50px"}),
            rx.vstack(
                rx.box(
                    rx.text("Promising", style={"fontSize": "12px", "fontWeight": "700", "color": "white"}),
                    style={"padding": "4px 12px", "background": BLUE, "borderRadius": "5px"},
                ),
                rx.text("Verdict", style={"fontSize": "11px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="1",
                align="center",
            ),
            rx.box(style={"width": "1px", "background": BORDER, "height": "50px"}),
            rx.vstack(
                rx.text("Jan 2025", style={"fontFamily": "'Courier New', monospace", "fontSize": "13px", "fontWeight": "700", "color": TEXT}),
                rx.text("Last Eval", style={"fontSize": "11px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="1",
                align="center",
            ),
            justify="between",
            width="100%",
            style={"marginBottom": "18px"},
        ),
        # Key strengths (SWOT excerpt)
        rx.text("Key Strengths", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "10px"}),
        rx.vstack(
            *[rx.hstack(
                rx.box(style={"width": "5px", "height": "5px", "background": GREEN, "borderRadius": "50%", "flexShrink": "0", "marginTop": "5px"}),
                rx.text(item, style={"fontSize": "12px", "color": TEXT_2, "lineHeight": "1.5"}),
                spacing="2",
                align="start",
            ) for item in [
                "Strong founding team with deep domain expertise",
                "Clear product differentiation in an underserved market",
                "Early revenue traction with 3 paying enterprise customers",
            ]],
            spacing="2",
            align="start",
            style={"marginBottom": "18px"},
        ),
        # Top recommendation
        rx.text("Top Recommendation", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "10px"}),
        rx.box(
            rx.text(
                "Focus the next 90 days on signing a second enterprise reference customer "
                "before raising a seed round. Investors will want to see repeatable sales motion.",
                style={"fontSize": "12px", "color": TEXT_2, "lineHeight": "1.6"},
            ),
            style={"padding": "12px 14px", "background": BLUE_BG, "border": f"1px solid rgba(27,72,196,0.15)", "borderRadius": "7px"},
        ),
        spacing="0",
        align="start",
        style={"padding": "22px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
    )

    # Right panel: locked admin-only section
    admin_view = rx.vstack(
        # Comparative ranking — locked
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Batch Ranking", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                    rx.hstack(
                        rx.html('<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="2.5" y="5.5" width="7" height="5.5" rx="1.2" stroke="#7188a4" stroke-width="1.1"/><path d="M4 5.5V4a2 2 0 014 0v1.5" stroke="#7188a4" stroke-width="1.1"/></svg>'),
                        rx.text("Admin only", style={"fontSize": "10px", "fontWeight": "600", "color": TEXT_3}),
                        spacing="1",
                        align="center",
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                    style={"marginBottom": "14px"},
                ),
                # Blurred ranking rows
                rx.vstack(
                    *[rx.hstack(
                        rx.text(f"#{rank}", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": TEXT_3, "width": "24px"}),
                        rx.box(style={"flex": "1", "height": "10px", "background": clr, "borderRadius": "3px", "opacity": "0.25"}),
                        rx.text(score, style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": TEXT_3, "width": "36px", "textAlign": "right"}),
                        spacing="3",
                        align="center",
                        width="100%",
                    ) for rank, score, clr in [
                        (1, "84", GREEN),
                        (2, "81", GREEN),
                        (3, "77", BLUE),
                        (4, "74 ←", ROSE),   # founder's position highlighted
                        (5, "68", BLUE),
                        (6, "61", BLUE),
                    ]],
                    spacing="2",
                    align="start",
                    style={"filter": "blur(2.5px)", "userSelect": "none", "pointerEvents": "none"},
                ),
                spacing="0",
            ),
            style={"padding": "20px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px", "position": "relative", "overflow": "hidden"},
        ),
        # All-startups table — locked
        rx.box(
            rx.hstack(
                rx.text("All Startups (Batch 4)", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                rx.hstack(
                    rx.html('<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="2.5" y="5.5" width="7" height="5.5" rx="1.2" stroke="#7188a4" stroke-width="1.1"/><path d="M4 5.5V4a2 2 0 014 0v1.5" stroke="#7188a4" stroke-width="1.1"/></svg>'),
                    rx.text("Admin only", style={"fontSize": "10px", "fontWeight": "600", "color": TEXT_3}),
                    spacing="1",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
                style={"marginBottom": "14px"},
            ),
            rx.vstack(
                *[rx.hstack(
                    rx.box(style={"flex": "2", "height": "9px", "background": "#dce3f0", "borderRadius": "2px"}),
                    rx.box(style={"flex": "1", "height": "9px", "background": "#dce3f0", "borderRadius": "2px"}),
                    rx.box(style={"width": "28px", "height": "9px", "background": clr, "borderRadius": "2px", "opacity": "0.4"}),
                    spacing="3",
                    width="100%",
                ) for clr in [GREEN, GREEN, BLUE, ROSE, BLUE, BLUE]],
                spacing="2",
                align="start",
                style={"filter": "blur(2px)", "userSelect": "none", "pointerEvents": "none"},
            ),
            style={"padding": "20px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "10px"},
        ),
        rx.box(
            rx.text(
                "Comparative ranking and the full startup list are visible only to admins. "
                "Founders see their own score, verdict, and recommendations.",
                style={"fontSize": "12px", "color": TEXT_3, "lineHeight": "1.6", "textAlign": "center"},
            ),
            style={"padding": "14px 16px", "background": ROSE_BG, "border": "1px solid rgba(190,24,93,0.12)", "borderRadius": "8px"},
        ),
        spacing="4",
        align="start",
        width="100%",
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none"><circle cx="9" cy="7.5" r="3" stroke="#be185d" stroke-width="1.5"/><path d="M3 17c0-2.8 2.7-5 6-5" stroke="#be185d" stroke-width="1.5" stroke-linecap="round"/><circle cx="15" cy="14" r="2.5" stroke="#be185d" stroke-width="1.5"/><path d="M17.5 14h1.2" stroke="#be185d" stroke-width="1.5" stroke-linecap="round"/></svg>',
            ROSE_BG, "rgba(190,24,93,0.2)",
            "Coming Feature",
            "Founder Portal",
        ),
        rx.box(
            rx.vstack(
                rx.text(
                    "Let founders log in, submit their own pitch, and run the evaluation — then show them only their own results.",
                    style={"fontSize": "17px", "fontWeight": "700", "color": TEXT, "lineHeight": "1.5", "marginBottom": "16px"},
                ),
                rx.text(
                    "Today, every evaluation is initiated internally. Founders never interact "
                    "with EvalBot directly — they submit a pitch and wait. There's no "
                    "self-serve option, no transparency into what the agents actually assess, "
                    "and no ongoing relationship with the founders you evaluate.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "The Founder Portal gives each startup their own login. They upload their "
                    "pitch, run the 7-agent pipeline, and receive a full report: score, verdict, "
                    "SWOT, and recommendations. Their view is deliberately scoped — they see "
                    "their own results only, never other startups' data or batch rankings.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7", "marginBottom": "14px"},
                ),
                rx.text(
                    "You, as admin, retain the full view: all submitted startups side-by-side, "
                    "comparative rankings, cross-batch history, and the ability to filter and "
                    "configure what the evaluation covers for founder submissions vs. internal runs.",
                    style={"fontSize": "14px", "color": TEXT_2, "lineHeight": "1.7"},
                ),
                _unlocks_section([
                    "Self-serve founder login — each startup has its own isolated account",
                    "Founders run the eval pipeline on their own pitch, see score + recommendations",
                    "Strict data isolation — no founder can see another startup's results",
                    "Admin retains full comparative view: rankings, batch analysis, all startups",
                    "Configurable agent scope — filter which agents run for founder submissions",
                ]),
                spacing="0",
                align="start",
            ),
            rx.vstack(
                rx.text(
                    "Founder view",
                    style={"fontSize": "11px", "fontWeight": "700", "color": ROSE, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "8px"},
                ),
                founder_view,
                rx.text(
                    "Admin-only sections",
                    style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginTop": "16px", "marginBottom": "8px"},
                ),
                admin_view,
                spacing="0",
                align="start",
                width="100%",
            ),
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "48px",
                "alignItems": "start",
            },
        ),
    )

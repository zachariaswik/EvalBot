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


# ── Page 7: Founder Portal (phased roadmap) ───────────────────────────────────

def founder_portal_page() -> rx.Component:  # noqa: C901
    # ── shared icon SVGs ──────────────────────────────────────────────────────
    _CHECK = (
        '<svg width="13" height="13" viewBox="0 0 12 12" fill="none">'
        '<circle cx="6" cy="6" r="5.5" fill="#d1fae5"/>'
        '<path d="M3.5 6l1.8 1.8L8.5 4.5" stroke="#0a7c52" stroke-width="1.3"'
        ' stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    _CROSS = (
        '<svg width="13" height="13" viewBox="0 0 12 12" fill="none">'
        '<circle cx="6" cy="6" r="5.5" fill="#fee2e2"/>'
        '<path d="M4 4l4 4M8 4l-4 4" stroke="#b91c1c" stroke-width="1.3"'
        ' stroke-linecap="round"/></svg>'
    )
    _LOCK = (
        '<svg width="13" height="13" viewBox="0 0 12 12" fill="none">'
        '<rect x="2.5" y="5.5" width="7" height="5.5" rx="1.2" stroke="#aebdd0" stroke-width="1.1"/>'
        '<path d="M4 5.5V4a2 2 0 014 0v1.5" stroke="#aebdd0" stroke-width="1.1"/></svg>'
    )
    _PDF_SVG = (
        '<svg width="12" height="12" viewBox="0 0 14 14" fill="none">'
        '<rect x="1" y="0.5" width="12" height="13" rx="1.5" stroke="#7188a4" stroke-width="1.1"/>'
        '<line x1="3.5" y1="4.5" x2="10.5" y2="4.5" stroke="#7188a4" stroke-width="1"/>'
        '<line x1="3.5" y1="6.5" x2="10.5" y2="6.5" stroke="#7188a4" stroke-width="1"/>'
        '<line x1="3.5" y1="8.5" x2="8" y2="8.5" stroke="#7188a4" stroke-width="1"/></svg>'
    )

    # ── helper: capability row ────────────────────────────────────────────────
    def _cap(text, icon_svg):
        return rx.hstack(
            rx.html(icon_svg),
            rx.text(text, style={"fontSize": "12px", "color": TEXT_2, "lineHeight": "1.4"}),
            spacing="2",
            align="start",
        )

    # ── helper: phase badge ───────────────────────────────────────────────────
    def _phase_badge(num, label, color, bg):
        return rx.hstack(
            rx.box(
                rx.text(f"Phase {num}", style={"fontSize": "9px", "fontWeight": "800", "color": "white", "letterSpacing": "0.05em"}),
                style={"padding": "2px 8px", "background": color, "borderRadius": "3px"},
            ),
            rx.text(label, style={"fontSize": "11px", "fontWeight": "700", "color": color}),
            spacing="2",
            align="center",
        )

    # ── helper: small file row for phase 3 mockup ────────────────────────────
    def _file_row_sm(name, status, s_clr, s_bg):
        return rx.hstack(
            rx.html(_PDF_SVG),
            rx.text(name, style={"fontSize": "11px", "fontWeight": "600", "color": TEXT, "flex": "1"}),
            rx.box(
                rx.text(status, style={"fontSize": "9px", "fontWeight": "700", "color": s_clr}),
                style={"padding": "1px 6px", "background": s_bg, "borderRadius": "3px"},
            ),
            spacing="2",
            align="center",
            width="100%",
        )

    # ── Phase progression strip ───────────────────────────────────────────────
    def _phase_dot(num, label, color):
        return rx.vstack(
            rx.box(
                rx.text(str(num), style={"fontSize": "11px", "fontWeight": "800", "color": "white"}),
                style={
                    "width": "30px", "height": "30px", "borderRadius": "50%",
                    "background": color,
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                },
            ),
            rx.text(label, style={
                "fontSize": "10px", "fontWeight": "600", "color": color,
                "textAlign": "center", "maxWidth": "82px",
            }),
            spacing="2",
            align="center",
        )

    phase_strip = rx.box(
        rx.hstack(
            _phase_dot(1, "Accounts & Scores", BLUE),
            rx.box(style={"flex": "1", "height": "2px", "background": f"linear-gradient(90deg, {BLUE}, {GREEN})", "marginBottom": "20px", "marginLeft": "4px", "marginRight": "4px"}),
            _phase_dot(2, "Team Access", GREEN),
            rx.box(style={"flex": "1", "height": "2px", "background": f"linear-gradient(90deg, {GREEN}, {GOLD})", "marginBottom": "20px", "marginLeft": "4px", "marginRight": "4px"}),
            _phase_dot(3, "Document Submission", GOLD),
            rx.box(style={"flex": "1", "height": "2px", "background": f"linear-gradient(90deg, {GOLD}, {PURPLE})", "marginBottom": "20px", "marginLeft": "4px", "marginRight": "4px"}),
            _phase_dot(4, "Self-Service Runs", PURPLE),
            align="center",
            width="100%",
        ),
        style={
            "padding": "24px 32px",
            "background": SURFACE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "10px",
            "marginBottom": "32px",
        },
    )

    # ── Phase 1 mockup: founder login + score card ────────────────────────────
    phase1_mockup = rx.box(
        rx.hstack(
            rx.box(
                rx.text("A", style={"fontSize": "11px", "fontWeight": "900", "color": "white", "fontFamily": "'Georgia', serif"}),
                style={"width": "26px", "height": "26px", "borderRadius": "6px", "background": ROSE, "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
            ),
            rx.vstack(
                rx.text("Acme AI", style={"fontSize": "12px", "fontWeight": "700", "color": TEXT}),
                rx.text("founder@acme.io", style={"fontSize": "10px", "color": TEXT_3}),
                spacing="0",
                align="start",
            ),
            rx.box(
                rx.text("Logged in", style={"fontSize": "9px", "fontWeight": "700", "color": GREEN}),
                style={"padding": "2px 7px", "background": GREEN_BG, "borderRadius": "3px"},
            ),
            justify="between",
            align="center",
            width="100%",
            style={"marginBottom": "14px"},
        ),
        rx.hstack(
            rx.vstack(
                rx.text("74", style={"fontFamily": "'Georgia', serif", "fontSize": "26px", "fontWeight": "900", "color": BLUE, "lineHeight": "1"}),
                rx.text("Score", style={"fontSize": "10px", "color": TEXT_3}),
                spacing="1",
                align="center",
            ),
            rx.box(style={"width": "1px", "background": BORDER, "height": "36px"}),
            rx.vstack(
                rx.box(
                    rx.text("Promising", style={"fontSize": "11px", "fontWeight": "700", "color": "white"}),
                    style={"padding": "3px 9px", "background": BLUE, "borderRadius": "4px"},
                ),
                rx.text("Verdict", style={"fontSize": "10px", "color": TEXT_3}),
                spacing="1",
                align="center",
            ),
            rx.box(style={"width": "1px", "background": BORDER, "height": "36px"}),
            rx.vstack(
                rx.text("Jan '25", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "fontWeight": "700", "color": TEXT}),
                rx.text("Evaluated", style={"fontSize": "10px", "color": TEXT_3}),
                spacing="1",
                align="center",
            ),
            justify="between",
            width="100%",
            style={"marginBottom": "14px"},
        ),
        rx.vstack(
            *[rx.hstack(
                rx.html(_LOCK),
                rx.text(item, style={"fontSize": "11px", "color": TEXT_3}),
                spacing="2",
                align="center",
                style={"padding": "5px 10px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "5px"},
            ) for item in ["Rankings — admin only", "Other startups — hidden"]],
            spacing="2",
            align="start",
            width="100%",
        ),
        style={"padding": "16px 18px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "9px"},
    )

    phase1 = rx.box(
        _phase_badge(1, "Accounts & Score Visibility", BLUE, BLUE_BG),
        rx.text(
            "Founders receive a login. They can see their own startup's score, verdict, SWOT, and recommendations — nothing else.",
            style={"fontSize": "13px", "color": TEXT_2, "lineHeight": "1.6", "margin": "10px 0 14px"},
        ),
        rx.vstack(
            _cap("Create a founder account tied to their startup", _CHECK),
            _cap("View their score, verdict, and SWOT analysis", _CHECK),
            _cap("Read actionable recommendations from Agent 6", _CHECK),
            _cap("See only their own startup — no comparative data", _CHECK),
            rx.box(style={"height": "1px", "background": BORDER, "width": "100%"}),
            _cap("Team sharing (Phase 2)", _LOCK),
            _cap("Document submission (Phase 3)", _LOCK),
            _cap("Running evaluations (Phase 4)", _LOCK),
            spacing="2",
            align="start",
            width="100%",
            style={"marginBottom": "16px"},
        ),
        rx.text("Mockup", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "8px"}),
        phase1_mockup,
        style={
            "padding": "22px 24px",
            "background": SURFACE,
            "border": f"2px solid rgba(27,72,196,0.18)",
            "borderTop": f"4px solid {BLUE}",
            "borderRadius": "12px",
        },
    )

    # ── Phase 2 mockup: team member list ─────────────────────────────────────
    phase2_mockup = rx.box(
        rx.text("Team Members", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "10px"}),
        rx.vstack(
            *[rx.hstack(
                rx.box(
                    rx.text(init, style={"fontSize": "10px", "fontWeight": "900", "color": "white", "fontFamily": "'Georgia', serif"}),
                    style={"width": "24px", "height": "24px", "borderRadius": "5px", "background": clr, "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                ),
                rx.vstack(
                    rx.text(name, style={"fontSize": "12px", "fontWeight": "600", "color": TEXT}),
                    rx.text(email, style={"fontSize": "10px", "color": TEXT_3}),
                    spacing="0",
                    align="start",
                ),
                rx.box(
                    rx.text(role, style={"fontSize": "9px", "fontWeight": "700", "color": clr}),
                    style={"padding": "2px 7px", "background": bg, "borderRadius": "3px", "marginLeft": "auto"},
                ),
                spacing="2",
                align="center",
                width="100%",
                style={"padding": "7px 0"},
            ) for init, name, email, role, clr, bg in [
                ("A", "Alex Chen", "alex@acme.io", "Founder", ROSE, ROSE_BG),
                ("S", "Sara Patel", "sara@acme.io", "Co-Founder", BLUE, BLUE_BG),
                ("M", "Mike R.", "mike@acme.io", "Viewer", TEXT_3, SURFACE_2),
            ]],
            spacing="0",
            align="start",
            width="100%",
            style={"marginBottom": "12px"},
        ),
        rx.box(
            rx.text("All 3 members see the same evaluation results", style={"fontSize": "11px", "color": GREEN, "fontWeight": "600"}),
            style={"padding": "8px 12px", "background": GREEN_BG, "border": f"1px solid rgba(10,124,82,0.2)", "borderRadius": "6px"},
        ),
        style={"padding": "16px 18px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "9px"},
    )

    phase2 = rx.box(
        _phase_badge(2, "Team-Wide Access", GREEN, GREEN_BG),
        rx.text(
            "Multiple founders and employees from the same startup can all log in and see shared evaluation results.",
            style={"fontSize": "13px", "color": TEXT_2, "lineHeight": "1.6", "margin": "10px 0 14px"},
        ),
        rx.vstack(
            _cap("Invite co-founders and team members by email", _CHECK),
            _cap("Role management: Founder, Co-Founder, or Viewer", _CHECK),
            _cap("All team members see the same startup's results", _CHECK),
            _cap("Team activity log — who viewed what and when", _CHECK),
            rx.box(style={"height": "1px", "background": BORDER, "width": "100%"}),
            _cap("Document submission (Phase 3)", _LOCK),
            _cap("Running evaluations (Phase 4)", _LOCK),
            spacing="2",
            align="start",
            width="100%",
            style={"marginBottom": "16px"},
        ),
        rx.text("Mockup", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "8px"}),
        phase2_mockup,
        style={
            "padding": "22px 24px",
            "background": SURFACE,
            "border": f"2px solid rgba(10,124,82,0.18)",
            "borderTop": f"4px solid {GREEN}",
            "borderRadius": "12px",
        },
    )

    # ── Phase 3 mockup: submission hub ────────────────────────────────────────
    phase3_mockup = rx.box(
        rx.text("Submission Hub", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "10px"}),
        rx.vstack(
            _file_row_sm("pitch_deck_v3.pdf", "Ready", GREEN, GREEN_BG),
            _file_row_sm("exec_summary.pdf", "Ready", GREEN, GREEN_BG),
            _file_row_sm("projections_2025.xlsx", "Ready", GREEN, GREEN_BG),
            _file_row_sm("team_bios.pdf", "Pending", TEXT_3, SURFACE_2),
            _file_row_sm("market_research.pdf", "Pending", TEXT_3, SURFACE_2),
            spacing="2",
            align="start",
            width="100%",
            style={"marginBottom": "12px"},
        ),
        rx.hstack(
            rx.text("Completeness", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
            rx.text("60%", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": GOLD, "fontWeight": "700"}),
            justify="between",
            width="100%",
            style={"marginBottom": "5px"},
        ),
        rx.box(
            rx.box(style={"height": "100%", "background": GOLD, "width": "60%", "borderRadius": "3px"}),
            style={"width": "100%", "height": "6px", "background": "#fef3c7", "borderRadius": "3px", "overflow": "hidden", "marginBottom": "12px"},
        ),
        rx.box(
            rx.text("Admin reviews and runs EvalBot when ready", style={"fontSize": "11px", "color": TEXT_2, "fontWeight": "600"}),
            style={"padding": "7px 12px", "background": "#fffbeb", "border": "1px solid rgba(180,130,0,0.2)", "borderRadius": "6px"},
        ),
        style={"padding": "16px 18px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "9px"},
    )

    phase3 = rx.box(
        _phase_badge(3, "Document Submission", GOLD, GOLD_BG),
        rx.text(
            "Founders upload their pitch materials, financials, and team docs. Your team reviews everything and runs the evaluation when ready.",
            style={"fontSize": "13px", "color": TEXT_2, "lineHeight": "1.6", "margin": "10px 0 14px"},
        ),
        rx.vstack(
            _cap("Upload pitch decks, financial models, and team docs", _CHECK),
            _cap("Submission completeness tracker before trigger", _CHECK),
            _cap("Each document type routed to the correct agents", _CHECK),
            _cap("Admin reviews submissions and triggers EvalBot", _CHECK),
            rx.box(style={"height": "1px", "background": BORDER, "width": "100%"}),
            _cap("Founders triggering their own eval runs (Phase 4)", _LOCK),
            spacing="2",
            align="start",
            width="100%",
            style={"marginBottom": "16px"},
        ),
        rx.text("Mockup", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "8px"}),
        phase3_mockup,
        style={
            "padding": "22px 24px",
            "background": SURFACE,
            "border": f"2px solid rgba(168,88,0,0.18)",
            "borderTop": f"4px solid {GOLD}",
            "borderRadius": "12px",
        },
    )

    # ── Phase 4 mockup: self-service run panel ────────────────────────────────
    phase4_mockup = rx.box(
        rx.hstack(
            rx.vstack(
                rx.text("Run Evaluation", style={"fontSize": "12px", "fontWeight": "700", "color": TEXT}),
                rx.text("5 documents ready · 7 agents", style={"fontSize": "10px", "color": TEXT_3}),
                spacing="0",
                align="start",
            ),
            rx.box(
                rx.text("▶  Run Now", style={"fontSize": "11px", "fontWeight": "800", "color": "white"}),
                style={"padding": "7px 16px", "background": PURPLE, "borderRadius": "6px"},
            ),
            justify="between",
            align="center",
            width="100%",
            style={"marginBottom": "14px"},
        ),
        rx.text("Latest Run — in progress", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "8px"}),
        rx.vstack(
            *[rx.hstack(
                rx.text(agent, style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "width": "56px", "flexShrink": "0"}),
                rx.box(
                    rx.box(style={"height": "100%", "background": clr, "width": f"{pct}%", "borderRadius": "2px"}),
                    style={"flex": "1", "height": "5px", "background": SURFACE_2, "borderRadius": "2px", "overflow": "hidden"},
                ),
                rx.text(status, style={"fontSize": "10px", "fontWeight": "600", "color": clr, "width": "64px", "textAlign": "right", "flexShrink": "0"}),
                spacing="2",
                align="center",
                width="100%",
            ) for agent, pct, clr, status in [
                ("Agent 1", 100, GREEN, "✓ Done"),
                ("Agent 2", 100, GREEN, "✓ Done"),
                ("Agent 3", 100, GREEN, "✓ Done"),
                ("Agent 4", 60, BLUE, "Running…"),
                ("Agent 5", 0, TEXT_3, "Queued"),
                ("Agent 6", 0, TEXT_3, "Queued"),
            ]],
            spacing="2",
            align="start",
            width="100%",
        ),
        style={"padding": "16px 18px", "background": SURFACE, "border": f"1px solid {BORDER}", "borderRadius": "9px"},
    )

    phase4 = rx.box(
        _phase_badge(4, "Self-Service Evaluation Runs", PURPLE, PURPLE_BG),
        rx.text(
            "Founders can trigger their own EvalBot runs whenever they update their documents, watching all 7 agents progress in real time.",
            style={"fontSize": "13px", "color": TEXT_2, "lineHeight": "1.6", "margin": "10px 0 14px"},
        ),
        rx.vstack(
            _cap("Founders trigger evaluation runs themselves", _CHECK),
            _cap("Real-time run progress across all 7 agents", _CHECK),
            _cap("Re-run any time after updating documents", _CHECK),
            _cap("Updated score and recommendations delivered instantly", _CHECK),
            _cap("Run history — compare scores across submissions", _CHECK),
            spacing="2",
            align="start",
            width="100%",
            style={"marginBottom": "16px"},
        ),
        rx.text("Mockup", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "8px"}),
        phase4_mockup,
        style={
            "padding": "22px 24px",
            "background": SURFACE,
            "border": f"2px solid rgba(124,58,237,0.18)",
            "borderTop": f"4px solid {PURPLE}",
            "borderRadius": "12px",
        },
    )

    # ── Access levels comparison ───────────────────────────────────────────────
    access_strip = rx.box(
        rx.text("Access Levels", style={"fontSize": "15px", "fontWeight": "700", "color": TEXT, "marginBottom": "20px"}),
        rx.box(
            *[rx.box(
                rx.text(role, style={"fontSize": "11px", "fontWeight": "700", "color": clr, "letterSpacing": "0.05em", "textTransform": "uppercase", "marginBottom": "14px"}),
                rx.vstack(
                    *[rx.hstack(
                        rx.html(tick),
                        rx.text(item, style={"fontSize": "13px", "color": TEXT_2, "lineHeight": "1.4"}),
                        spacing="2",
                        align="start",
                    ) for item, tick in items],
                    spacing="3",
                    align="start",
                ),
                style={"padding": "20px", "background": bg, "border": f"1px solid {bdr}", "borderRadius": "10px"},
            ) for role, clr, bg, bdr, items in [
                ("Founder", ROSE, ROSE_BG, "rgba(190,24,93,0.12)", [
                    ("See their own score, verdict, SWOT & recommendations", _CHECK),
                    ("Invite team members to share access", _CHECK),
                    ("Upload pitch materials, financials, and team docs", _CHECK),
                    ("Trigger evaluation runs (Phase 4)", _CHECK),
                    ("See other startups or comparative rankings", _CROSS),
                    ("Access admin controls or batch analytics", _CROSS),
                ]),
                ("LP / Partner", BLUE, BLUE_BG, "rgba(27,72,196,0.12)", [
                    ("View curated batch-level reports", _CHECK),
                    ("See top-ranked startups in summary view", _CHECK),
                    ("Access verdict distribution across batches", _CHECK),
                    ("View individual startup details or documents", _CROSS),
                    ("Run or trigger evaluations", _CROSS),
                    ("Access founder submission materials", _CROSS),
                ]),
                ("Admin (VC)", GREEN, GREEN_BG, "rgba(10,124,82,0.12)", [
                    ("Full access to all startup submissions and results", _CHECK),
                    ("Comparative rankings and cross-batch analytics", _CHECK),
                    ("Configure evaluation scope and access roles", _CHECK),
                    ("View and download all submitted documents", _CHECK),
                    ("Manage founder accounts and team permissions", _CHECK),
                    ("Override or re-run evaluations for any startup", _CHECK),
                ]),
            ]],
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "16px"},
        ),
        style={
            "padding": "28px 32px",
            "background": SURFACE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "marginTop": "40px",
        },
    )

    return page_layout(
        _page_header(
            '<svg width="24" height="24" viewBox="0 0 20 20" fill="none">'
            '<circle cx="9" cy="7.5" r="3" stroke="#be185d" stroke-width="1.5"/>'
            '<path d="M3 17c0-2.8 2.7-5 6-5" stroke="#be185d" stroke-width="1.5" stroke-linecap="round"/>'
            '<circle cx="15" cy="14" r="2.5" stroke="#be185d" stroke-width="1.5"/>'
            '<path d="M17.5 14h1.2" stroke="#be185d" stroke-width="1.5" stroke-linecap="round"/></svg>',
            ROSE_BG, "rgba(190,24,93,0.2)",
            "Roadmap Feature",
            "Founder Portal",
        ),
        rx.text(
            "A four-phase plan giving founders their own window into EvalBot — "
            "starting with read-only score access and building toward fully self-service evaluation runs.",
            style={"fontSize": "15px", "color": TEXT_2, "lineHeight": "1.6", "maxWidth": "680px", "marginBottom": "32px"},
        ),
        phase_strip,
        rx.box(
            phase1,
            phase2,
            phase3,
            phase4,
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "24px"},
        ),
        access_strip,
    )


# ── Page 8: Course Integration ────────────────────────────────────────────────

def course_integration_page() -> rx.Component:
    """Course Integration — Evolve API bridge: sync content, run bot, unified overview."""

    _LINK_ICON = (
        '<svg width="22" height="22" viewBox="0 0 22 22" fill="none">'
        '<path d="M9 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" stroke="#0d9488" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M13 9a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" stroke="#0d9488" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    )
    _CHK = (
        '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
        '<circle cx="6" cy="6" r="5.5" fill="#d1fae5"/>'
        '<path d="M3.5 6l2 2 3-3.5" stroke="#0a7c52" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    )
    _SYNC = (
        '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
        '<circle cx="6" cy="6" r="5.5" fill="#ccfbf1"/>'
        '<path d="M4 3.5A3 3 0 019 6" stroke="#0d9488" stroke-width="1.1" stroke-linecap="round"/>'
        '<path d="M8 8.5A3 3 0 013 6" stroke="#0d9488" stroke-width="1.1" stroke-linecap="round"/>'
        '<polygon points="9,4.5 10.5,3 10.5,6" fill="#0d9488"/>'
        '</svg>'
    )
    _BOT = (
        '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
        '<circle cx="6" cy="6" r="5.5" fill="rgba(27,72,196,0.12)"/>'
        '<circle cx="4.5" cy="5.5" r="1" fill="#1b48c4"/>'
        '<circle cx="7.5" cy="5.5" r="1" fill="#1b48c4"/>'
        '<path d="M4 8s.8 1 2 1 2-1 2-1" stroke="#1b48c4" stroke-width="1" stroke-linecap="round"/>'
        '</svg>'
    )

    # ── Journey strip ──────────────────────────────────────────────────────────

    def _step(num: str, label: str, color: str, bg: str) -> rx.Component:
        return rx.vstack(
            rx.box(
                rx.text(num, style={"fontSize": "12px", "fontWeight": "800", "color": color}),
                style={
                    "width": "32px", "height": "32px", "borderRadius": "50%",
                    "background": bg, "border": f"1.5px solid {color}",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                },
            ),
            rx.text(label, style={"fontSize": "11px", "fontWeight": "600", "color": TEXT_2,
                                  "textAlign": "center", "maxWidth": "80px"}),
            spacing="2",
            align="center",
        )

    journey_strip = rx.box(
        rx.hstack(
            _step("1", "Founder on Evolve", TEAL, TEAL_BG),
            rx.box(style={"flex": "1", "height": "1.5px", "marginTop": "-18px",
                          "background": f"linear-gradient(90deg,{TEAL},{GOLD})"}),
            _step("2", "Completes Modules", GOLD, GOLD_BG),
            rx.box(style={"flex": "1", "height": "1.5px", "marginTop": "-18px",
                          "background": f"linear-gradient(90deg,{GOLD},{BLUE})"}),
            _step("3", "API Sync", BLUE, BLUE_BG),
            rx.box(style={"flex": "1", "height": "1.5px", "marginTop": "-18px",
                          "background": f"linear-gradient(90deg,{BLUE},{PURPLE})"}),
            _step("4", "EvalBot Runs", PURPLE, PURPLE_BG),
            rx.box(style={"flex": "1", "height": "1.5px", "marginTop": "-18px",
                          "background": f"linear-gradient(90deg,{PURPLE},{GREEN})"}),
            _step("5", "Overview in AltaLab", GREEN, GREEN_BG),
            align="center",
            spacing="0",
        ),
        style={
            "background": SURFACE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "padding": "28px 36px",
            "marginBottom": "28px",
            "boxShadow": "0 2px 8px rgba(12,24,41,0.04)",
        },
    )

    # ── Evolve Sync panel (left) ───────────────────────────────────────────────

    def _sync_row(icon_html: str, label: str, value: str, accent: str) -> rx.Component:
        return rx.hstack(
            rx.html(icon_html),
            rx.text(label, style={"fontSize": "12px", "color": TEXT_2, "flex": "1"}),
            rx.text(value, style={"fontSize": "12px", "fontWeight": "700", "color": accent,
                                  "fontFamily": "'Courier New', monospace"}),
            spacing="2",
            align="center",
            style={"padding": "7px 10px", "background": SURFACE_2,
                   "borderRadius": "6px", "marginBottom": "4px"},
        )

    def _mod_sync_row(label: str, pct: int, status: str, status_color: str) -> rx.Component:
        return rx.hstack(
            rx.html(_CHK if status == "Synced" else _SYNC),
            rx.vstack(
                rx.text(label, style={"fontSize": "11px", "fontWeight": "600", "color": TEXT,
                                      "lineHeight": "1.2"}),
                rx.hstack(
                    rx.box(style={"width": f"{pct}%", "height": "3px", "background": TEAL,
                                  "borderRadius": "2px"}),
                    rx.box(style={"flex": "1", "height": "3px", "background": "#e5ecf7",
                                  "borderRadius": "2px"}),
                    spacing="0",
                    style={"width": "100%"},
                ),
                spacing="1",
                align="start",
                style={"flex": "1"},
            ),
            rx.text(status, style={"fontSize": "10px", "color": status_color, "fontWeight": "600",
                                   "flexShrink": "0"}),
            spacing="2",
            align="center",
            style={"padding": "7px 10px", "background": SURFACE_2,
                   "borderRadius": "6px", "marginBottom": "3px"},
        )

    sync_panel = rx.box(
        rx.hstack(
            rx.box(
                style={"width": "8px", "height": "8px", "borderRadius": "50%",
                       "background": GREEN, "boxShadow": f"0 0 6px {GREEN}"},
            ),
            rx.text("Evolve API", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3,
                                         "letterSpacing": "0.08em", "textTransform": "uppercase"}),
            rx.box(style={"flex": "1"}),
            rx.text("Connected", style={"fontSize": "10px", "color": GREEN, "fontWeight": "700"}),
            spacing="2",
            align="center",
            style={"marginBottom": "14px"},
        ),
        _sync_row(
            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="1" y="2" width="10" height="8" rx="1.5" stroke="#0d9488" stroke-width="1"/><line x1="1" y1="5" x2="11" y2="5" stroke="#0d9488" stroke-width="0.8"/></svg>',
            "Modules imported", "8 / 8", TEAL,
        ),
        _sync_row(
            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="6" cy="4.5" r="2" stroke="#1b48c4" stroke-width="1"/><path d="M2 10.5c0-2.2 1.8-4 4-4s4 1.8 4 4" stroke="#1b48c4" stroke-width="1" stroke-linecap="round"/></svg>',
            "Founders enrolled", "24", BLUE,
        ),
        _sync_row(
            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 8l2.5-3 2 2 2-2.5 1.5 1.5" stroke="#0a7c52" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/><rect x="1" y="1" width="10" height="10" rx="1.5" stroke="#0a7c52" stroke-width="1"/></svg>',
            "Completions synced", "61", GREEN,
        ),
        _sync_row(
            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="6" cy="6" r="4.5" stroke="#7188a4" stroke-width="1"/><line x1="6" y1="4" x2="6" y2="6.5" stroke="#7188a4" stroke-width="1" stroke-linecap="round"/><circle cx="6" cy="8" r="0.5" fill="#7188a4"/></svg>',
            "Last sync", "2 min ago", TEXT_3,
        ),
        rx.text("Course Modules", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3,
                                          "letterSpacing": "0.07em", "textTransform": "uppercase",
                                          "margin": "14px 0 8px"}),
        _mod_sync_row("01 · Introduction",        100, "Synced",  GREEN),
        _mod_sync_row("02 · Market Sizing",        100, "Synced",  GREEN),
        _mod_sync_row("03 · Business Model",       100, "Synced",  GREEN),
        _mod_sync_row("04 · Financials",            80, "Syncing", TEAL),
        _mod_sync_row("05 · GTM Strategy",          80, "Syncing", TEAL),
        _mod_sync_row("06 · Team & Execution",      60, "Syncing", TEAL),
        _mod_sync_row("07 · Pitch & Storytelling",  40, "Syncing", TEAL),
        _mod_sync_row("08 · Demo Day Prep",         40, "Syncing", TEAL),
        style={
            "background": SURFACE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "padding": "20px",
            "flex": "1",
            "minWidth": "0",
            "boxShadow": "0 2px 8px rgba(12,24,41,0.04)",
        },
    )

    # ── EvalBot panel (right) ───────────────────────────────────────────────

    def _bot_log_row(ts: str, founder: str, event: str, color: str) -> rx.Component:
        return rx.hstack(
            rx.text(ts, style={"fontSize": "9px", "color": TEXT_3,
                               "fontFamily": "'Courier New', monospace", "flexShrink": "0",
                               "width": "36px"}),
            rx.text(founder, style={"fontSize": "10px", "fontWeight": "700", "color": TEXT,
                                    "flexShrink": "0", "width": "76px",
                                    "overflow": "hidden", "textOverflow": "ellipsis",
                                    "whiteSpace": "nowrap"}),
            rx.text(event, style={"fontSize": "10px", "color": color, "flex": "1",
                                  "overflow": "hidden", "textOverflow": "ellipsis",
                                  "whiteSpace": "nowrap"}),
            spacing="2",
            align="center",
            style={"padding": "5px 8px", "borderBottom": f"1px solid {BORDER}"},
        )

    bot_panel = rx.box(
        rx.hstack(
            rx.box(
                rx.html(
                    '<svg width="16" height="16" viewBox="0 0 20 20" fill="none">'
                    '<rect x="4" y="6" width="12" height="10" rx="2" stroke="#7c3aed" stroke-width="1.5"/>'
                    '<circle cx="7.5" cy="11" r="1" fill="#7c3aed"/>'
                    '<circle cx="12.5" cy="11" r="1" fill="#7c3aed"/>'
                    '<path d="M8 14.5s.8.8 2 .8 2-.8 2-.8" stroke="#7c3aed" stroke-width="1" stroke-linecap="round"/>'
                    '<path d="M10 6V3" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/>'
                    '<circle cx="10" cy="2.5" r="1" fill="#7c3aed"/>'
                    '</svg>'
                ),
                style={"width": "30px", "height": "30px", "background": PURPLE_BG,
                       "borderRadius": "8px", "border": "1px solid rgba(147,51,234,0.18)",
                       "display": "flex", "alignItems": "center", "justifyContent": "center",
                       "flexShrink": "0"},
            ),
            rx.vstack(
                rx.text("EvalBot", style={"fontSize": "13px", "fontWeight": "800",
                                             "color": TEXT, "lineHeight": "1.1"}),
                rx.text("Evaluation assistant for course completions",
                        style={"fontSize": "10px", "color": TEXT_3}),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            style={"marginBottom": "16px"},
        ),
        # Status strip
        rx.hstack(
            rx.hstack(
                rx.box(style={"width": "7px", "height": "7px", "borderRadius": "50%",
                               "background": GREEN, "boxShadow": f"0 0 5px {GREEN}"}),
                rx.text("Running", style={"fontSize": "11px", "color": GREEN, "fontWeight": "700"}),
                spacing="1", align="center",
            ),
            rx.box(style={"flex": "1"}),
            rx.text("Last run: 4 min ago", style={"fontSize": "10px", "color": TEXT_3}),
            align="center",
            style={"padding": "8px 12px", "background": "#f0fdf6",
                   "border": "1px solid rgba(10,124,82,0.18)", "borderRadius": "8px",
                   "marginBottom": "14px"},
        ),
        # Stats row
        rx.hstack(
            rx.vstack(
                rx.text("18", style={"fontSize": "20px", "fontWeight": "800", "color": PURPLE,
                                     "fontFamily": "'Courier New', monospace", "lineHeight": "1"}),
                rx.text("Evals run", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="1", align="center",
            ),
            rx.box(style={"width": "1px", "height": "36px", "background": BORDER}),
            rx.vstack(
                rx.text("6", style={"fontSize": "20px", "fontWeight": "800", "color": TEAL,
                                    "fontFamily": "'Courier New', monospace", "lineHeight": "1"}),
                rx.text("Pending", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="1", align="center",
            ),
            rx.box(style={"width": "1px", "height": "36px", "background": BORDER}),
            rx.vstack(
                rx.text("24", style={"fontSize": "20px", "fontWeight": "800", "color": BLUE,
                                     "fontFamily": "'Courier New', monospace", "lineHeight": "1"}),
                rx.text("Founders", style={"fontSize": "10px", "color": TEXT_3, "fontWeight": "600"}),
                spacing="1", align="center",
            ),
            justify="between",
            style={"padding": "12px 16px", "background": SURFACE_2,
                   "borderRadius": "8px", "marginBottom": "14px"},
        ),
        # Activity log
        rx.text("Recent Activity", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3,
                                           "letterSpacing": "0.07em", "textTransform": "uppercase",
                                           "marginBottom": "6px"}),
        rx.box(
            _bot_log_row("0m",  "Teemu V.",    "Bot evaluation completed — score 74",   GREEN),
            _bot_log_row("4m",  "Sara K.",     "Module 08 synced from Evolve",          TEAL),
            _bot_log_row("11m", "Marcus L.",   "Bot evaluation completed — score 61",   BLUE),
            _bot_log_row("18m", "Aisha N.",    "Module 07 synced from Evolve",          TEAL),
            _bot_log_row("23m", "Jonas B.",    "Bot evaluation completed — score 82",   GREEN),
            _bot_log_row("31m", "Priya M.",    "All 8 modules synced — bot queued",     PURPLE),
            style={"background": SURFACE_2, "borderRadius": "8px",
                   "border": f"1px solid {BORDER}", "overflow": "hidden",
                   "marginBottom": "14px"},
        ),
        # Trigger button mockup
        rx.box(
            rx.hstack(
                rx.html(
                    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
                    '<polygon points="3,2 3,10 10,6" fill="white"/>'
                    '</svg>'
                ),
                rx.text("Run EvalBot Now",
                        style={"fontSize": "12px", "color": "white", "fontWeight": "700"}),
                spacing="2",
                align="center",
            ),
            style={"padding": "9px 16px", "background": PURPLE,
                   "borderRadius": "7px", "display": "inline-flex",
                   "alignItems": "center", "cursor": "default",
                   "boxShadow": "0 2px 8px rgba(124,58,237,0.3)"},
        ),
        style={
            "background": SURFACE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "padding": "20px",
            "flex": "2",
            "minWidth": "0",
            "boxShadow": "0 2px 8px rgba(12,24,41,0.04)",
        },
    )

    # ── Feature breakdown cards ────────────────────────────────────────────────

    def _feat(icon_html: str, icon_bg: str, icon_border: str, accent: str,
              title: str, bullets: list[str]) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.box(
                    rx.html(icon_html),
                    style={
                        "width": "36px", "height": "36px",
                        "background": icon_bg, "border": f"1px solid {icon_border}",
                        "borderRadius": "8px",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "flexShrink": "0",
                    },
                ),
                rx.text(title, style={"fontSize": "14px", "fontWeight": "800", "color": TEXT,
                                      "letterSpacing": "-0.01em"}),
                spacing="3",
                align="center",
                style={"marginBottom": "14px"},
            ),
            rx.vstack(
                *[
                    rx.hstack(
                        rx.box(style={"width": "5px", "height": "5px", "borderRadius": "50%",
                                      "background": accent, "flexShrink": "0", "marginTop": "5px"}),
                        rx.text(b, style={"fontSize": "12px", "color": TEXT_2, "lineHeight": "1.55"}),
                        spacing="2",
                        align="start",
                    )
                    for b in bullets
                ],
                spacing="2",
            ),
            style={
                "background": SURFACE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "20px 22px",
                "boxShadow": "0 2px 8px rgba(12,24,41,0.04)",
            },
        )

    feat_sync = _feat(
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M4 10a6 6 0 0110.5-4" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/><path d="M16 10a6 6 0 01-10.5 4" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/><polyline points="14,4 16.5,6 14,8" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="6,12 3.5,14 6,16" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        TEAL_BG, "rgba(20,184,166,0.15)", TEAL,
        "Evolve API Sync",
        [
            "All course modules, video metadata, and student progress imported automatically",
            "Bi-directional: completion events on Evolve propagate to AltaLab in real time",
            "No manual data entry — Evolve remains the source of truth",
            "Re-syncs on a configurable schedule (e.g. every 5 minutes)",
        ],
    )
    feat_bot = _feat(
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><rect x="4" y="7" width="12" height="10" rx="2.5" stroke="#7c3aed" stroke-width="1.5"/><circle cx="8" cy="12" r="1.2" fill="#7c3aed"/><circle cx="12" cy="12" r="1.2" fill="#7c3aed"/><path d="M8.5 15.5s.8.8 1.5.8 1.5-.8 1.5-.8" stroke="#7c3aed" stroke-width="1" stroke-linecap="round"/><path d="M10 7V4" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><circle cx="10" cy="3" r="1.2" fill="#7c3aed"/></svg>',
        PURPLE_BG, "rgba(147,51,234,0.15)", PURPLE,
        "EvalBot Runner",
        [
            "Trigger the Evolve evaluation bot directly from AltaLab's interface",
            "Bot runs automatically when a founder completes all 8 modules on Evolve",
            "Results (score, feedback, flags) written back to AltaLab immediately",
            "Full bot activity log — who ran, when, and what outcome",
        ],
    )
    feat_material = _feat(
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><rect x="2" y="2" width="16" height="16" rx="2.5" stroke="#a85800" stroke-width="1.5"/><line x1="6" y1="7" x2="14" y2="7" stroke="#a85800" stroke-width="1.5" stroke-linecap="round"/><line x1="6" y1="10.5" x2="14" y2="10.5" stroke="#a85800" stroke-width="1.5" stroke-linecap="round"/><line x1="6" y1="14" x2="10" y2="14" stroke="#a85800" stroke-width="1.5" stroke-linecap="round"/></svg>',
        GOLD_BG, "rgba(168,88,0,0.15)", GOLD,
        "Full Material Mirror",
        [
            "All curriculum content from Evolve is browsable inside AltaLab",
            "Module descriptions, learning objectives, and assets accessible in one place",
            "Analysts can review what founders studied before evaluating their pitch",
            "Content updates on Evolve automatically reflect in AltaLab on next sync",
        ],
    )
    feat_overview = _feat(
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3" fill="#0a7c52" opacity="0.2"/><circle cx="10" cy="10" r="1.5" fill="#0a7c52"/><path d="M10 2v3M10 15v3M2 10h3M15 10h3" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round"/><path d="M4.9 4.9l2.2 2.2M12.9 12.9l2.2 2.2M4.9 15.1l2.2-2.2M12.9 7.1l2.2-2.2" stroke="#0a7c52" stroke-width="1" stroke-linecap="round" opacity="0.5"/></svg>',
        GREEN_BG, "rgba(10,124,82,0.15)", GREEN,
        "Unified Progress Overview",
        [
            "Single dashboard: every founder's module completions, bot score, and pipeline status",
            "Filter by cohort, module progress, or bot evaluation outcome",
            "Completed founders auto-feed the 7-agent AltaLab evaluation pipeline",
            "Admins see the full picture; founders see only their own results",
        ],
    )

    return page_layout(
        _page_header(
            _LINK_ICON,
            TEAL_BG, "rgba(20,184,166,0.2)",
            "Roadmap Feature",
            "Course Integration",
        ),
        rx.text(
            "Rather than hosting the curriculum directly, AltaLab connects to the Evolve platform via API. "
            "Everything completed on Evolve — modules, bot evaluations, student progress — is imported "
            "automatically, so you run the EvalBot and keep the full overview without leaving AltaLab.",
            style={"fontSize": "15px", "color": TEXT_2, "lineHeight": "1.6",
                   "maxWidth": "700px", "marginBottom": "32px"},
        ),
        journey_strip,
        rx.hstack(
            sync_panel,
            bot_panel,
            spacing="5",
            align="start",
            style={"marginBottom": "28px"},
        ),
        rx.box(
            feat_sync,
            feat_bot,
            feat_material,
            feat_overview,
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
        ),
    )


# ── Page 9: Potential Platform Upgrades (overview of 6 platform features) ──────

def platform_features_page() -> rx.Component:
    """Overview page listing all 6 platform-suite features."""

    _GRID_ICON = (
        '<svg width="22" height="22" viewBox="0 0 22 22" fill="none">'
        '<rect x="2" y="2" width="8" height="8" rx="2" stroke="#1b48c4" stroke-width="1.5"/>'
        '<rect x="12" y="2" width="8" height="8" rx="2" stroke="#1b48c4" stroke-width="1.5"/>'
        '<rect x="2" y="12" width="8" height="8" rx="2" stroke="#1b48c4" stroke-width="1.5"/>'
        '<rect x="12" y="12" width="8" height="8" rx="2" stroke="#1b48c4" stroke-width="1.5"/>'
        '</svg>'
    )

    _FEATURES = [
        (
            "01",
            '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="#1b48c4" stroke-width="1.5"/><path d="M3 18c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="#1b48c4" stroke-width="1.5" stroke-linecap="round"/></svg>',
            BLUE_BG, "rgba(27,72,196,0.15)", BLUE,
            "Analyst Profiles",
            "Per-analyst accounts with eval history, avg score, sourcing stats, and a team leaderboard.",
            "/roadmap/analyst-profiles",
        ),
        (
            "02",
            '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="4" width="4" height="12" rx="1" stroke="#a85800" stroke-width="1.5"/><rect x="8" y="6" width="4" height="10" rx="1" stroke="#a85800" stroke-width="1.5"/><rect x="14.5" y="2" width="4" height="14" rx="1" stroke="#a85800" stroke-width="1.5"/></svg>',
            GOLD_BG, "rgba(168,88,0,0.15)", GOLD,
            "Deal Flow Pipeline",
            "Kanban board moving startups from Submitted → Shortlisted → Due Diligence → Invested.",
            "/roadmap/deal-flow-pipeline",
        ),
        (
            "03",
            '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><polyline points="2,16 6.5,9.5 10.5,12.5 18,5" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="13,5 18,5 18,10" stroke="#0a7c52" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            GREEN_BG, "rgba(10,124,82,0.15)", GREEN,
            "Portfolio Tracking",
            "Track invested startups post-close. Trigger quarterly re-evaluations and surface early warning signals.",
            "/roadmap/portfolio-tracking",
        ),
        (
            "04",
            '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><rect x="3.5" y="1.5" width="13" height="17" rx="2" stroke="#7c3aed" stroke-width="1.5"/><line x1="7" y1="7" x2="13" y2="7" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><line x1="7" y1="10" x2="13" y2="10" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/><line x1="7" y1="13" x2="11" y2="13" stroke="#7c3aed" stroke-width="1.5" stroke-linecap="round"/></svg>',
            PURPLE_BG, "rgba(147,51,234,0.15)", PURPLE,
            "Automated Reports",
            "One-click PDF/email export of a full batch. Schedule weekly LP delivery — no manual formatting.",
            "/roadmap/automated-reports",
        ),
        (
            "05",
            '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M8 6H4a2 2 0 00-2 2v6a2 2 0 002 2h8a2 2 0 002-2v-4" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/><rect x="9" y="3" width="9" height="9" rx="2" stroke="#0d9488" stroke-width="1.5"/><line x1="12" y1="6" x2="15" y2="6" stroke="#0d9488" stroke-width="1.2" stroke-linecap="round"/><line x1="12" y1="8.5" x2="15" y2="8.5" stroke="#0d9488" stroke-width="1.2" stroke-linecap="round"/></svg>',
            TEAL_BG, "rgba(20,184,166,0.15)", TEAL,
            "Partner API",
            "Founders submit pitches via REST API. Scores and verdicts returned automatically — no manual intake.",
            "/roadmap/partner-api",
        ),
        (
            "06",
            '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="13" width="3.5" height="5.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/><rect x="8" y="9" width="3.5" height="9.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/><rect x="14.5" y="5" width="3.5" height="13.5" rx="0.5" stroke="#a85800" stroke-width="1.5"/></svg>',
            GOLD_BG, "rgba(168,88,0,0.15)", GOLD,
            "Cohort Analytics",
            "Cross-batch trend charts: avg score over time, verdict distribution shifts, sector concentration.",
            "/roadmap/cohort-analytics",
        ),
    ]

    def _feature_card(
        num: str,
        icon_html: str,
        icon_bg: str,
        icon_border: str,
        accent: str,
        title: str,
        desc: str,
        href: str,
    ) -> rx.Component:
        return rx.link(
            rx.box(
                rx.hstack(
                    rx.box(
                        rx.html(icon_html),
                        style={
                            "width": "42px",
                            "height": "42px",
                            "background": icon_bg,
                            "border": f"1px solid {icon_border}",
                            "borderRadius": "10px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "flexShrink": "0",
                        },
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                num,
                                style={"fontSize": "10px", "fontWeight": "700", "color": accent,
                                       "fontFamily": "'Courier New', monospace", "letterSpacing": "0.04em"},
                            ),
                            rx.text(
                                title,
                                style={"fontSize": "15px", "fontWeight": "800", "color": TEXT,
                                       "letterSpacing": "-0.01em"},
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            desc,
                            style={"fontSize": "13px", "color": TEXT_3, "lineHeight": "1.65"},
                        ),
                        spacing="1",
                        align="start",
                    ),
                    spacing="4",
                    align="start",
                    width="100%",
                ),
                rx.hstack(
                    rx.text(
                        "View details →",
                        style={"fontSize": "11px", "fontWeight": "600", "color": accent},
                    ),
                    justify="end",
                    style={"marginTop": "16px"},
                ),
                style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "12px",
                    "padding": "22px 24px",
                    "boxShadow": "0 2px 8px rgba(12,24,41,0.04)",
                    "transition": "box-shadow 0.2s, border-color 0.2s, transform 0.15s",
                    "_hover": {
                        "boxShadow": "0 6px 24px rgba(27,72,196,0.09)",
                        "borderColor": "#c2cfe4",
                        "transform": "translateY(-1px)",
                    },
                },
            ),
            href=href,
            style={"textDecoration": "none", "display": "block"},
        )

    return page_layout(
        _page_header(
            _GRID_ICON,
            BLUE_BG, "rgba(27,72,196,0.15)",
            "Roadmap Feature",
            "Potential Platform Upgrades",
        ),
        rx.text(
            "Six potential upgrades designed to take EvalBot from a single-user tool to a "
            "full-team investment platform — with workflow management, LP reporting, and open API access.",
            style={"fontSize": "15px", "color": TEXT_2, "lineHeight": "1.6",
                   "maxWidth": "680px", "marginBottom": "36px"},
        ),
        rx.box(
            *[
                _feature_card(num, icon, ibg, iborder, accent, title, desc, href)
                for num, icon, ibg, iborder, accent, title, desc, href in _FEATURES
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "16px",
            },
        ),
    )


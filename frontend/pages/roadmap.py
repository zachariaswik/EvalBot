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
TEAL_BG = "rgba(20,184,166,0.08)"
PURPLE = "#7c3aed"
ROSE = "#be185d"
ROSE_BG = "#fce7f3"
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
    href: str,
    watermark_color: str,
    preview: rx.Component,
    delay: str = "0s",
) -> rx.Component:
    return rx.link(
        rx.box(
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
                    rx.text(
                        "View details →",
                        style={
                            "fontSize": "11px",
                            "fontWeight": "600",
                            "color": TEXT_3,
                            "letterSpacing": "0.01em",
                        },
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
        ),
        href=href,
        style={"textDecoration": "none", "display": "block"},
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
            # 01 — Founder Portal
            roadmap_card(
                "01",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="9" cy="7.5" r="3" stroke="#be185d" stroke-width="1.5"/><path d="M3 17c0-2.8 2.7-5 6-5" stroke="#be185d" stroke-width="1.5" stroke-linecap="round"/><circle cx="15" cy="14" r="2.5" stroke="#be185d" stroke-width="1.5"/><path d="M17.5 14h1.2" stroke="#be185d" stroke-width="1.5" stroke-linecap="round"/></svg>',
                ROSE_BG, "rgba(190,24,93,0.15)",
                "Founder Portal",
                "Let founders log in, submit their own pitch, and see their evaluation. Each founder sees only their own results — admins see everything.",
                "/roadmap/founder-portal",
                ROSE_BG,
                rx.box(
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.text("A", style={"fontFamily": "'Georgia', serif", "fontSize": "10px", "fontWeight": "900", "color": "white"}),
                                style={"width": "24px", "height": "24px", "borderRadius": "6px", "background": ROSE, "display": "flex", "alignItems": "center", "justifyContent": "center"},
                            ),
                            rx.vstack(
                                rx.text("Acme AI", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT}),
                                rx.text("Founder view", style={"fontSize": "9px", "color": ROSE, "fontWeight": "600"}),
                                spacing="0",
                                align="start",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.box(
                            rx.text("Logged in", style={"fontSize": "9px", "fontWeight": "600", "color": GREEN}),
                            style={"padding": "2px 7px", "background": GREEN_BG, "borderRadius": "3px"},
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        style={"marginBottom": "10px"},
                    ),
                    rx.vstack(
                        rx.hstack(rx.text("Your Score", style={"fontSize": "11px", "color": TEXT_3}), rx.text("74", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": BLUE, "fontWeight": "700"}), justify="between", width="100%"),
                        rx.hstack(rx.text("Verdict", style={"fontSize": "11px", "color": TEXT_3}), rx.text("Promising", style={"fontSize": "11px", "color": BLUE, "fontWeight": "600"}), justify="between", width="100%"),
                        rx.hstack(
                            rx.text("Ranking", style={"fontSize": "11px", "color": TEXT_3}),
                            rx.hstack(
                                rx.html('<svg width="10" height="10" viewBox="0 0 10 10" fill="none"><rect x="2" y="4.5" width="6" height="4.5" rx="1" stroke="#aebdd0" stroke-width="1"/><path d="M3.5 4.5V3a1.5 1.5 0 013 0v1.5" stroke="#aebdd0" stroke-width="1"/></svg>'),
                                rx.text("Admin only", style={"fontSize": "10px", "color": "#aebdd0", "fontWeight": "600"}),
                                spacing="1",
                                align="center",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        spacing="2",
                    ),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.8"},
                ),
            ),

            # 02 — Course Integration
            roadmap_card(
                "02",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1" y="3" width="18" height="13" rx="2.5" stroke="#0d9488" stroke-width="1.5"/><polygon points="8.5,8 8.5,13.5 14.5,10.7" fill="#0d9488"/></svg>',
                TEAL_BG, "rgba(20,184,166,0.15)",
                "Course Integration",
                "Host the full accelerator curriculum on-platform. Self-paced video lectures, interactive worksheets, and document uploads — all feeding EvalBot.",
                "/roadmap/course-integration",
                TEAL_BG,
                rx.box(
                    rx.hstack(
                        rx.box(style={"width": "44px", "height": "4px", "borderRadius": "2px", "background": TEAL, "flexShrink": "0"}),
                        rx.box(style={"flex": "1", "height": "4px", "borderRadius": "2px", "background": "#e5ecf7"}),
                        spacing="0",
                        style={"marginBottom": "6px"},
                    ),
                    rx.text("Module 3 of 8 · 38%", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": TEXT_3, "marginBottom": "10px"}),
                    rx.vstack(
                        *[
                            rx.hstack(
                                rx.html(icon),
                                rx.text(label, style={"fontSize": "11px", "fontWeight": "600", "color": clr}),
                                spacing="2",
                                align="center",
                            )
                            for icon, label, clr in [
                                ('<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><circle cx="5.5" cy="5.5" r="5" fill="#d1fae5"/><path d="M3 5.5l1.8 1.8 3-3.3" stroke="#0a7c52" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>', "01 · Introduction", GREEN),
                                ('<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><circle cx="5.5" cy="5.5" r="5" fill="#d1fae5"/><path d="M3 5.5l1.8 1.8 3-3.3" stroke="#0a7c52" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>', "02 · Market Sizing", GREEN),
                                ('<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><circle cx="5.5" cy="5.5" r="5" fill="#ccfbf1"/><polygon points="4.5,3.5 4.5,7.5 8.5,5.5" fill="#0d9488"/></svg>', "03 · Business Model", TEAL),
                                ('<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><rect x="2.5" y="5" width="6" height="4.5" rx="1" stroke="#aebdd0" stroke-width="1"/><path d="M4 5V4a1.5 1.5 0 013 0v1" stroke="#aebdd0" stroke-width="1"/></svg>', "04 · Financials", TEXT_3),
                            ]
                        ],
                        spacing="2",
                    ),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.85"},
                ),
            ),

            # 03 — Potential Platform Upgrades
            roadmap_card(
                "03",
                '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="2" y="2" width="7" height="7" rx="1.5" stroke="#1b48c4" stroke-width="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5" stroke="#1b48c4" stroke-width="1.5"/><rect x="2" y="11" width="7" height="7" rx="1.5" stroke="#1b48c4" stroke-width="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5" stroke="#1b48c4" stroke-width="1.5"/></svg>',
                BLUE_BG, "rgba(27,72,196,0.15)",
                "Potential Platform Upgrades",
                "Six platform upgrades — team analytics, deal-flow Kanban, portfolio tracking, LP reports, Partner API, and cross-batch insights.",
                "/roadmap/platform",
                BLUE_BG,
                rx.box(
                    rx.vstack(
                        *[
                            rx.hstack(
                                rx.box(style={"width": "7px", "height": "7px", "borderRadius": "2px", "background": clr, "flexShrink": "0"}),
                                rx.text(label, style={"fontSize": "11px", "color": TEXT, "fontWeight": "600"}),
                                spacing="2",
                                align="center",
                            )
                            for label, clr in [
                                ("Analyst Profiles", BLUE),
                                ("Deal Flow Pipeline", GOLD),
                                ("Portfolio Tracking", GREEN),
                                ("Automated Reports", PURPLE),
                                ("Partner API", TEAL),
                                ("Cohort Analytics", AMBER),
                            ]
                        ],
                        spacing="2",
                    ),
                    style={"padding": "14px 16px", "background": SURFACE_2, "border": f"1px solid {BORDER}", "borderRadius": "8px", "opacity": "0.85"},
                ),
            ),

            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "20px",
            },
        ),
    )

"""Top navigation bar component."""

import reflex as rx

# Brand colors
BLUE = "#1b48c4"
BLUE_2 = "#163a9e"
BLUE_GLOW = "rgba(27,72,196,0.35)"
SURFACE = "#ffffff"
BORDER = "#dce3f0"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_4 = "#aebdd0"


def navbar() -> rx.Component:
    return rx.el.header(
        rx.box(
            # Brand
            rx.link(
                rx.hstack(
                    rx.box(
                        rx.html(
                            '<svg width="17" height="17" viewBox="0 0 17 17" fill="none">'
                            '<rect x="1.5" y="1.5" width="6" height="6" rx="1.5" fill="white"/>'
                            '<rect x="9.5" y="1.5" width="6" height="6" rx="1.5" fill="white" opacity="0.5"/>'
                            '<rect x="1.5" y="9.5" width="6" height="6" rx="1.5" fill="white" opacity="0.5"/>'
                            '<rect x="9.5" y="9.5" width="6" height="6" rx="1.5" fill="white" opacity="0.25"/>'
                            "</svg>"
                        ),
                        style={
                            "width": "34px",
                            "height": "34px",
                            "background": BLUE,
                            "borderRadius": "8px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "flexShrink": "0",
                            "boxShadow": "0 2px 8px rgba(27,72,196,0.25)",
                        },
                    ),
                    rx.vstack(
                        rx.text(
                            "EvalBot",
                            style={
                                "fontFamily": "'Georgia', serif",
                                "fontSize": "19px",
                                "fontWeight": "700",
                                "color": TEXT,
                                "lineHeight": "1.1",
                                "letterSpacing": "-0.025em",
                            },
                        ),
                        rx.text(
                            "AI Venture Analyst",
                            style={
                                "fontSize": "9px",
                                "fontWeight": "700",
                                "letterSpacing": "0.12em",
                                "textTransform": "uppercase",
                                "color": TEXT_4,
                                "lineHeight": "1",
                            },
                        ),
                        spacing="0",
                        gap="0",
                    ),
                    spacing="3",
                    align="center",
                ),
                href="/",
                style={"textDecoration": "none", "flexShrink": "0"},
            ),
            # Nav links
            rx.hstack(
                rx.link(
                    "Dashboard",
                    href="/",
                    style={
                        "color": TEXT_2,
                        "fontSize": "14px",
                        "fontWeight": "500",
                        "textDecoration": "none",
                        "transition": "color 0.15s",
                        "_hover": {"color": BLUE},
                    },
                ),
                rx.link(
                    "Roadmap",
                    href="/roadmap",
                    style={
                        "color": TEXT_2,
                        "fontSize": "14px",
                        "fontWeight": "500",
                        "textDecoration": "none",
                        "transition": "color 0.15s",
                        "_hover": {"color": BLUE},
                    },
                ),
                rx.link(
                    rx.hstack(
                        rx.html(
                            '<svg width="9" height="11" viewBox="0 0 9 11" fill="currentColor">'
                            '<polygon points="0,0 9,5.5 0,11"/>'
                            "</svg>"
                        ),
                        rx.text("Run Batch", style={"color": "white", "fontSize": "13px", "fontWeight": "700"}),
                        spacing="2",
                        align="center",
                    ),
                    href="/run",
                    style={
                        "display": "inline-flex",
                        "alignItems": "center",
                        "textDecoration": "none",
                        "background": BLUE,
                        "padding": "9px 20px",
                        "borderRadius": "8px",
                        "letterSpacing": "0.01em",
                        "transition": "background 0.15s, box-shadow 0.15s",
                        "_hover": {
                            "background": BLUE_2,
                            "boxShadow": f"0 4px 16px {BLUE_GLOW}",
                        },
                    },
                ),
                spacing="8",
                align="center",
            ),
            style={
                "maxWidth": "1280px",
                "margin": "0 auto",
                "padding": "0 32px",
                "height": "60px",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
            },
        ),
        style={
            "background": SURFACE,
            "borderBottom": f"1px solid {BORDER}",
            "position": "sticky",
            "top": "0",
            "zIndex": "100",
        },
    )


def footer() -> rx.Component:
    return rx.el.footer(
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.text(
                            "EB",
                            style={
                                "fontFamily": "'Georgia', serif",
                                "fontSize": "9px",
                                "fontWeight": "900",
                                "color": "white",
                                "lineHeight": "1",
                            },
                        ),
                        style={
                            "width": "22px",
                            "height": "22px",
                            "background": BLUE,
                            "borderRadius": "5px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                    ),
                    rx.text(
                        "EvalBot · Multi-Agent Venture Analysis",
                        style={"fontSize": "13px", "color": "#7188a4", "fontWeight": "500"},
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    "Internal Tool",
                    style={
                        "fontSize": "12px",
                        "color": TEXT_4,
                        "fontWeight": "500",
                        "letterSpacing": "0.06em",
                        "textTransform": "uppercase",
                    },
                ),
                justify="between",
                width="100%",
            ),
            style={
                "maxWidth": "1280px",
                "margin": "0 auto",
                "padding": "22px 32px",
            },
        ),
        style={
            "background": SURFACE,
            "borderTop": f"1px solid {BORDER}",
        },
    )


def page_layout(*children: rx.Component, **kwargs) -> rx.Component:
    """Wrap a page with navbar, main content area, and footer."""
    return rx.vstack(
        navbar(),
        rx.box(
            *children,
            style={
                "flex": "1",
                "maxWidth": "1280px",
                "margin": "0 auto",
                "width": "100%",
                "padding": "44px 32px",
                "position": "relative",
                "zIndex": "1",
            },
        ),
        footer(),
        spacing="0",
        min_height="100vh",
        style={
            "background": "#f4f6fb",
            "fontFamily": "'Plus Jakarta Sans', system-ui, sans-serif",
            "position": "relative",
        },
    )

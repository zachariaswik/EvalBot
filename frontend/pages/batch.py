"""Batch detail page — /batch/[batch_id] route."""

from __future__ import annotations

import reflex as rx

from frontend.components.badges import section_marker, verdict_badge, status_pill, score_bar
from frontend.components.navbar import page_layout
from frontend.state.batch import BatchState


def _score_histogram(data: rx.Var, zones: rx.Var) -> rx.Component:
    """Score distribution histogram trimmed to actual data range.
    Scales cleanly to any number of startups."""

    def _bar(item: dict) -> rx.Component:
        return rx.box(
            rx.cond(
                item["has_count"],
                rx.text(
                    item["count"].to(str),
                    style={
                        "fontSize": "9px",
                        "color": item["fill"],
                        "fontWeight": "700",
                        "fontFamily": "'Courier New', monospace",
                        "lineHeight": "1",
                        "marginBottom": "3px",
                    },
                ),
                rx.box(style={"height": "12px"}),
            ),
            rx.box(
                style={
                    "width": "68%",
                    "height": rx.cond(
                        item["has_count"],
                        item["height_px"].to(str) + "px",
                        "0px",
                    ),
                    "background": item["fill"],
                    "borderRadius": "3px 3px 0 0",
                    "opacity": "0.82",
                }
            ),
            style={
                "flex": "1",
                "height": "100%",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "flex-end",
            },
        )

    def _zone_label(zone: dict) -> rx.Component:
        return rx.box(
            rx.text(zone["label"], style={
                "fontSize": "9px", "color": zone["hex"], "fontWeight": "700",
                "letterSpacing": "0.05em", "textTransform": "uppercase", "opacity": "0.6",
            }),
            style={"flex": zone["flex"].to(str)},
        )

    def _zone_bg(zone: dict) -> rx.Component:
        return rx.box(style={"flex": zone["flex"].to(str), "height": "100%", "background": zone["bg"]})

    return rx.box(
        # Zone labels (dynamically sized to match trimmed range)
        rx.box(
            rx.foreach(zones, _zone_label),
            style={"display": "flex", "width": "100%", "marginBottom": "8px"},
        ),
        # Chart area
        rx.box(
            # Zone backgrounds
            rx.box(
                rx.foreach(zones, _zone_bg),
                style={
                    "display": "flex",
                    "position": "absolute",
                    "top": "0", "left": "0", "right": "0", "bottom": "0",
                    "zIndex": "0",
                    "borderRadius": "6px",
                    "overflow": "hidden",
                },
            ),
            # Bars
            rx.box(
                rx.foreach(data, _bar),
                style={
                    "display": "flex",
                    "position": "absolute",
                    "top": "0", "left": "0", "right": "0", "bottom": "0",
                    "zIndex": "1",
                    "alignItems": "flex-end",
                    "padding": "0 6px",
                    "gap": "3px",
                },
            ),
            style={
                "position": "relative",
                "height": "115px",
                "width": "100%",
                "borderRadius": "6px",
                "marginBottom": "4px",
            },
        ),
        # Score axis labels
        rx.box(
            rx.foreach(
                data,
                lambda item: rx.box(
                    rx.text(
                        item["label"],
                        style={
                            "fontSize": "8px",
                            "color": TEXT_4,
                            "fontFamily": "'Courier New', monospace",
                            "textAlign": "center",
                        },
                    ),
                    style={"flex": "1", "display": "flex", "justifyContent": "center"},
                ),
            ),
            style={"display": "flex", "width": "100%", "paddingTop": "4px"},
        ),
        style={"width": "100%"},
    )

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
    return rx.box(
        rx.text((idx + 1).to(str), style={"fontFamily": "'Courier New', monospace", "fontSize": "12px", "color": TEXT, "fontWeight": "500"}),
        style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": GOLD_BG, "border": "1.5px solid rgba(168,88,0,0.2)", "display": "flex", "alignItems": "center", "justifyContent": "center"}
    )


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
                href=f"/batch/{BatchState.current_batch_id}/{s['name']}",
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
        on_click=rx.redirect(f"/batch/{BatchState.current_batch_id}/{s['name']}"),
    )


def verdict_row(item: dict) -> rx.Component:
    """A single verdict breakdown row: colored accent | name + count | fill bar + pct."""
    return rx.box(
        rx.hstack(
            # Colored left accent
            rx.box(
                style={
                    "width": "3px",
                    "minHeight": "44px",
                    "borderRadius": "2px",
                    "background": item["hex"],
                    "flexShrink": "0",
                    "alignSelf": "stretch",
                }
            ),
            # Content: name + count on top, bar + pct below
            rx.vstack(
                rx.hstack(
                    rx.text(
                        item["name"],
                        style={
                            "fontSize": "12.5px",
                            "fontWeight": "600",
                            "color": TEXT,
                            "flex": "1",
                            "lineHeight": "1.35",
                        },
                    ),
                    rx.text(
                        item["count"],
                        style={
                            "fontFamily": "'Georgia', serif",
                            "fontSize": "20px",
                            "fontWeight": "900",
                            "color": item["hex"],
                            "lineHeight": "1",
                            "minWidth": "20px",
                            "textAlign": "right",
                        },
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.hstack(
                    rx.box(
                        rx.box(
                            style={
                                "height": "100%",
                                "width": item["fill_width"],
                                "background": item["hex"],
                                "borderRadius": "2px",
                                "opacity": "0.75",
                                "transition": "width 0.9s cubic-bezier(0.16,1,0.3,1) 0.2s",
                            }
                        ),
                        style={
                            "flex": "1",
                            "height": "4px",
                            "background": SURFACE_3,
                            "borderRadius": "2px",
                            "overflow": "hidden",
                        },
                    ),
                    rx.text(
                        item["pct_str"],
                        style={
                            "fontSize": "11px",
                            "color": TEXT_3,
                            "minWidth": "32px",
                            "textAlign": "right",
                            "fontFamily": "'Courier New', monospace",
                        },
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                spacing="1",
                align="start",
                flex="1",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={
            "padding": "10px 0",
            "borderBottom": f"1px solid {SURFACE_2}",
        },
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
                section_marker("Score distribution"),
                _score_histogram(BatchState.score_histogram, BatchState.score_zones),
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
                # Header: label + sentiment badge
                rx.hstack(
                    section_marker("Verdict breakdown"),
                    rx.box(
                        rx.text(
                            BatchState.batch_sentiment,
                            style={
                                "fontSize": "10px",
                                "fontWeight": "700",
                                "color": BatchState.batch_sentiment_hex,
                                "letterSpacing": "0.04em",
                                "textTransform": "uppercase",
                            },
                        ),
                        style={
                            "padding": "3px 9px",
                            "borderRadius": "20px",
                            "background": SURFACE_2,
                            "border": f"1px solid {BORDER}",
                        },
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                    style={"marginBottom": "16px"},
                ),
                # Verdict rows
                rx.foreach(
                    BatchState.verdict_distribution,
                    verdict_row,
                ),
                # Footer: unique verdict count
                rx.text(
                    BatchState.verdict_distribution.length().to(str) + " verdict types across "
                    + BatchState.startup_count.to(str) + " startups",
                    style={
                        "fontSize": "11px",
                        "color": TEXT_4,
                        "marginTop": "12px",
                        "fontFamily": "'Courier New', monospace",
                    },
                ),
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

"""Verdict badge, score bar, and status pill components."""

from __future__ import annotations

import reflex as rx

# Verdict color → CSS color
VERDICT_BADGE_STYLES: dict[str, dict] = {
    "emerald": {"background": "#0a7c52", "color": "#fff"},
    "blue": {"background": "#1b48c4", "color": "#fff"},
    "orange": {"background": "#a85800", "color": "#fff"},
    "amber": {"background": "#92400e", "color": "#fff"},
    "red": {"background": "#b91c1c", "color": "#fff"},
    "gray": {"background": "#7188a4", "color": "#fff"},
}

STATUS_STYLES = {
    "completed": {"background": "#d1fae5", "color": "#0a7c52"},
    "failed": {"background": "#fee2e2", "color": "#b91c1c"},
}


def verdict_badge(verdict: str | rx.Var, color: str | rx.Var) -> rx.Component:
    """Inline verdict badge. `color` is one of: emerald, blue, orange, amber, red, gray."""
    bg = rx.match(
        color,
        ("emerald", "#0a7c52"),
        ("blue", "#1b48c4"),
        ("orange", "#a85800"),
        ("amber", "#92400e"),
        ("red", "#b91c1c"),
        "#7188a4",  # default
    )
    return rx.box(
        rx.text(verdict, style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.02em", "color": "white"}),
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "padding": "3px 9px",
            "borderRadius": "4px",
            "background": bg,
            "whiteSpace": "nowrap",
        },
    )


def score_bar(score: int | rx.Var, height: str = "4px", max_width: str = "100px") -> rx.Component:
    """Horizontal score progress bar colored by threshold."""
    bar_color = rx.cond(
        score >= 70,
        "#0a7c52",
        rx.cond(score >= 50, "#1b48c4", "#b91c1c"),
    )
    return rx.box(
        rx.box(
            style={
                "height": "100%",
                "borderRadius": "2px",
                "background": bar_color,
                "width": score.to(str) + "%",
                "transition": "width 1.2s cubic-bezier(0.16,1,0.3,1)",
            }
        ),
        style={
            "width": max_width,
            "height": height,
            "background": "#e5ecf7",
            "borderRadius": "2px",
            "overflow": "hidden",
        },
    )


def score_number(score: int | rx.Var, font_size: str = "18px") -> rx.Component:
    """Colored score number."""
    color = rx.cond(
        score >= 70,
        "#0a7c52",
        rx.cond(score >= 50, "#1b48c4", "#b91c1c"),
    )
    return rx.text(
        score,
        style={
            "fontFamily": "'Georgia', serif",
            "fontSize": font_size,
            "fontWeight": "900",
            "color": color,
            "lineHeight": "1",
        },
    )


def status_pill(status: str | rx.Var) -> rx.Component:
    bg = rx.match(
        status,
        ("completed", "#d1fae5"),
        ("failed", "#fee2e2"),
        "#f0f4fb",
    )
    color = rx.match(
        status,
        ("completed", "#0a7c52"),
        ("failed", "#b91c1c"),
        "#7188a4",
    )
    return rx.box(
        rx.text(
            status,
            style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.04em"},
        ),
        style={
            "display": "inline-flex",
            "padding": "3px 8px",
            "borderRadius": "4px",
            "background": bg,
            "color": color,
        },
    )


def section_marker(label: str | rx.Var) -> rx.Component:
    """AltaLab-style section label with leading line."""
    return rx.hstack(
        rx.box(
            style={
                "width": "20px",
                "height": "1.5px",
                "background": "#1b48c4",
                "borderRadius": "1px",
                "flexShrink": "0",
            }
        ),
        rx.text(
            label,
            style={
                "fontSize": "11px",
                "fontWeight": "700",
                "letterSpacing": "0.1em",
                "textTransform": "uppercase",
                "color": "#1b48c4",
                "fontFamily": "'Plus Jakarta Sans', sans-serif",
            },
        ),
        spacing="2",
        align="center",
    )

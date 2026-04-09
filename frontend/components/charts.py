"""Chart component wrappers using rx.recharts."""

from __future__ import annotations

import reflex as rx

# Verdict → hex color for pie chart
VERDICT_COLORS = {
    "Top VC Candidate": "#0a7c52",
    "Promising, Needs Sharper Focus": "#1b48c4",
    "Promising, But Needs Pivot": "#3b6fd4",
    "Good Small Business, Not Venture-Scale": "#a85800",
    "Feature, Not a Company": "#92400e",
    "AI Wrapper With Weak Moat": "#92400e",
    "Reject": "#b91c1c",
}

VERDICT_COLOR_LIST = list(VERDICT_COLORS.values())


def radar_chart(data: list[dict] | rx.Var, height: int = 280) -> rx.Component:
    """Radar chart for 10 startup dimensions. data: [{subject, score}]."""
    return rx.recharts.radar_chart(
        rx.recharts.polar_grid(),
        rx.recharts.polar_angle_axis(data_key="subject"),
        rx.recharts.radar(
            data_key="score",
            stroke="#1b48c4",
            fill="#1b48c4",
            fill_opacity=0.25,
        ),
        rx.recharts.graphing_tooltip(),
        data=data,
        width="100%",
        height=height,
    )


def bar_chart(data: list[dict] | rx.Var, height: int = 155) -> rx.Component:
    """Bar chart for batch leaderboard. data: [{name, score}]."""
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="score",
            fill="#1b48c4",
            radius=[4, 4, 0, 0],
        ),
        rx.recharts.x_axis(data_key="name", tick={"fontSize": 11}),
        rx.recharts.y_axis(domain=[0, 100], tick={"fontSize": 11}),
        rx.recharts.graphing_tooltip(),
        data=data,
        width="100%",
        height=height,
    )


def pie_chart(data: list[dict] | rx.Var, height: int = 200) -> rx.Component:
    """Donut/pie chart for verdict distribution. data: [{name, value}]."""
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            data=data,
            data_key="value",
            name_key="name",
            cx="50%",
            cy="50%",
            inner_radius=50,
            outer_radius=80,
            label=True,
        ),
        rx.recharts.graphing_tooltip(),
        rx.recharts.legend(),
        width="100%",
        height=height,
    )

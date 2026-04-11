"""Run Batch page — /run route."""

from __future__ import annotations

import reflex as rx

from frontend.components.badges import section_marker
from frontend.components.navbar import page_layout
from frontend.state.run import RunState

# ── Colors ────────────────────────────────────────────────────────────────────
BLUE = "#1b48c4"
BLUE_2 = "#163a9e"
BLUE_BG = "#eef2fd"
RED = "#b91c1c"
RED_BG = "#fee2e2"
GREEN = "#4ade80"
TEXT = "#0c1829"
TEXT_2 = "#374f6a"
TEXT_3 = "#7188a4"
TEXT_4 = "#aebdd0"
SURFACE = "#ffffff"
SURFACE_2 = "#f0f4fb"
SURFACE_3 = "#e5ecf7"
BORDER = "#dce3f0"
BORDER_2 = "#c2cfe4"

# Dark terminal colors
DARK_BG = "#0c1829"
DARK_SURFACE = "rgba(0,0,0,0.15)"
DARK_BLUE = "#4a8fd6"
DARK_GREEN = "#4ade80"
DARK_RED = "#f87171"


# ── Per-startup agent dot (reads from the startup's entry dict) ────────────────

def _agent_dot(n: int, entry: dict) -> rx.Component:
    """Small square agent indicator — reads precomputed done/active from entry."""
    is_done = entry[f"a{n}_done"]
    is_active = entry[f"a{n}_active"]

    bg = rx.cond(
        is_done,
        "rgba(74,222,128,0.18)",
        rx.cond(is_active, "rgba(74,143,214,0.25)", "rgba(255,255,255,0.04)"),
    )
    border = rx.cond(
        is_done,
        "rgba(74,222,128,0.4)",
        rx.cond(is_active, "rgba(74,143,214,0.5)", "rgba(255,255,255,0.07)"),
    )
    icon = rx.cond(
        is_done,
        rx.html('<svg width="8" height="8" viewBox="0 0 8 8" fill="none"><polyline points="1.5,4 3,5.5 6.5,2" stroke="rgba(74,222,128,0.9)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
        rx.cond(
            is_active,
            rx.spinner(size="1", style={"color": DARK_BLUE, "width": "9px", "height": "9px"}),
            rx.text(str(n), style={"fontFamily": "'Courier New', monospace", "fontSize": "8px", "color": "rgba(255,255,255,0.2)", "fontWeight": "600", "lineHeight": "1"}),
        ),
    )

    return rx.box(
        icon,
        style={
            "width": "26px", "height": "26px", "borderRadius": "6px",
            "background": bg, "border": f"1px solid {border}",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "transition": "all 0.35s",
        },
    )


# ── Active startup card (one per concurrently-running startup) ─────────────────

def startup_card(entry: dict) -> rx.Component:
    """Compact card showing one startup's live agent progress."""
    has_active = (
        entry["a1_active"] | entry["a2_active"] | entry["a3_active"]
        | entry["a4_active"] | entry["a5_active"] | entry["a6_active"]
    )
    return rx.box(
        rx.hstack(
            rx.text(
                entry["name"],
                style={"fontSize": "13px", "fontWeight": "700", "color": "white",
                       "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap", "flex": "1"},
            ),
            rx.text(
                entry["elapsed_s"].to(str) + "s",
                style={"fontFamily": "'Courier New', monospace", "fontSize": "10px",
                       "color": "rgba(74,143,214,0.5)", "flexShrink": "0"},
            ),
            align="center", width="100%",
            style={"marginBottom": "10px"},
        ),
        rx.hstack(
            *[_agent_dot(n, entry) for n in range(1, 7)],
            spacing="1",
        ),
        rx.cond(
            has_active,
            rx.text(
                entry["current_role"],
                style={"fontFamily": "'Courier New', monospace", "fontSize": "9px",
                       "color": "rgba(74,143,214,0.45)", "marginTop": "8px",
                       "letterSpacing": "0.04em", "overflow": "hidden",
                       "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
            ),
            rx.box(),
        ),
        style={
            "background": "rgba(74,143,214,0.07)",
            "border": "1px solid rgba(74,143,214,0.13)",
            "borderRadius": "11px",
            "padding": "14px 16px",
            "flex": "1",
            "minWidth": "220px",
        },
    )


# ── Staged startup row ────────────────────────────────────────────────────────

def staged_row(s: dict) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(s["name"], style={"fontSize": "13px", "fontWeight": "700", "color": TEXT}),
            rx.cond(
                s["files"],
                rx.text("files", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "marginTop": "1px"}),
                rx.text("—", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "marginTop": "1px"}),
            ),
            spacing="0",
            align="start",
            flex="1",
            style={"minWidth": "0"},
        ),
        rx.el.button(
            "Remove",
            on_click=RunState.remove_startup(s["name"]),
            disabled=RunState.status == "running",
            style={
                "fontSize": "11px",
                "fontWeight": "600",
                "color": RED,
                "background": RED_BG,
                "border": "1px solid rgba(185,28,28,0.15)",
                "padding": "3px 9px",
                "borderRadius": "4px",
                "cursor": "pointer",
                "fontFamily": "'Plus Jakarta Sans', sans-serif",
                "marginLeft": "10px",
                "flexShrink": "0",
                "transition": "background 0.12s",
                "_hover": {"background": "#fecaca"},
                "_disabled": {"opacity": "0.4", "cursor": "not-allowed"},
            },
        ),
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "8px 12px",
            "background": SURFACE_2,
            "border": f"1px solid {BORDER}",
            "borderLeft": f"3px solid {BLUE}",
            "borderRadius": "7px",
        },
        width="100%",
    )


# ── Completed startup entry (in terminal) ─────────────────────────────────────

def completed_entry(entry: dict) -> rx.Component:
    return rx.cond(
        entry["timed_out"],
        # Timed-out style (red)
        rx.hstack(
            rx.hstack(
                rx.text(entry["name"], style={"fontSize": "11px", "fontWeight": "600", "color": "rgba(248,113,113,0.8)", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}),
                rx.text("⏰", style={"fontSize": "9px", "flexShrink": "0"}),
                spacing="1", align="center", flex="1", style={"minWidth": "0"},
            ),
            rx.text(
                entry["elapsed_s"].to(str) + "s",
                style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(248,113,113,0.4)", "flexShrink": "0"},
            ),
            justify="between", align="center",
            style={"padding": "4px 8px", "background": "rgba(248,113,113,0.05)", "borderRadius": "4px", "borderLeft": "2px solid rgba(248,113,113,0.35)"},
            width="100%",
        ),
        # Success style (green)
        rx.hstack(
            rx.text(entry["name"], style={"fontSize": "11px", "fontWeight": "600", "color": "rgba(74,222,128,0.8)", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}),
            rx.text(
                entry["elapsed_s"].to(str) + "s",
                style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(74,222,128,0.4)", "flexShrink": "0"},
            ),
            justify="between", align="center",
            style={"padding": "4px 8px", "background": "rgba(74,222,128,0.05)", "borderRadius": "4px", "borderLeft": "2px solid rgba(74,222,128,0.35)"},
            width="100%",
        ),
    )


# ── Log line ─────────────────────────────────────────────────────────────────

def log_line(line: str) -> rx.Component:
    return rx.text(line, style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": DARK_GREEN, "lineHeight": "1.9", "display": "block"})


# ── Pipeline monitor (terminal-style) ──────────────────────────────────────────

def pipeline_monitor() -> rx.Component:
    is_running = RunState.status == "running"
    is_done = RunState.status == "done"
    is_error = RunState.status == "error"
    is_idle = (RunState.status == "idle") | (RunState.status == "interrupted")

    status_label = rx.match(
        RunState.status,
        ("done", "● DONE"),
        ("error", "● ERROR"),
        ("running", "● RUNNING"),
        "○ IDLE",
    )
    status_bg = rx.match(
        RunState.status,
        ("done", "rgba(74,222,128,0.14)"),
        ("error", "rgba(248,113,113,0.14)"),
        ("running", "rgba(74,143,214,0.18)"),
        "rgba(255,255,255,0.05)",
    )
    status_color = rx.match(
        RunState.status,
        ("done", "#4ade80"),
        ("error", "#f87171"),
        ("running", "#7ab3e8"),
        "rgba(255,255,255,0.22)",
    )

    return rx.box(
        # Chrome titlebar
        rx.hstack(
            rx.hstack(
                rx.box(style={"width": "10px", "height": "10px", "borderRadius": "50%", "background": "rgba(255,255,255,0.07)"}),
                rx.box(style={"width": "10px", "height": "10px", "borderRadius": "50%", "background": "rgba(255,255,255,0.07)"}),
                rx.box(style={"width": "10px", "height": "10px", "borderRadius": "50%", "background": "rgba(255,255,255,0.07)"}),
                spacing="1",
            ),
            rx.text("pipeline.monitor", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "letterSpacing": "0.1em", "color": "rgba(255,255,255,0.18)"}),
            spacing="2",
            align="center",
        ),
        rx.box(
            rx.text(
                status_label,
                style={
                    "fontFamily": "'Courier New', monospace",
                    "fontSize": "9px",
                    "fontWeight": "700",
                    "letterSpacing": "0.1em",
                    "textTransform": "uppercase",
                    "padding": "3px 9px",
                    "borderRadius": "3px",
                    "background": status_bg,
                    "color": status_color,
                    "transition": "all 0.4s",
                },
            ),
        ),

        # Idle state
        rx.cond(
            is_idle,
            rx.hstack(
                rx.box(
                    rx.box(style={"position": "absolute", "inset": "20px", "borderRadius": "50%", "border": "1px solid rgba(255,255,255,0.1)", "display": "flex", "alignItems": "center", "justifyContent": "center"},
                    ),
                    rx.box(style={"position": "absolute", "inset": "0", "width": "14px", "height": "14px", "borderRadius": "50%", "background": "rgba(255,255,255,0.1)", "top": "50%", "left": "50%", "transform": "translate(-50%,-50%)"}),
                    style={"flexShrink": "0", "position": "relative", "width": "72px", "height": "72px"},
                ),
                rx.vstack(
                    rx.text("READY", style={"fontFamily": "'Georgia', serif", "fontSize": "28px", "fontWeight": "900", "color": "rgba(255,255,255,0.1)", "letterSpacing": "0.18em"}),
                    rx.text("6 AGENTS STANDING BY — AWAITING BATCH", style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.14)", "letterSpacing": "0.07em"}),
                    rx.hstack(
                        *[
                            rx.box(
                                rx.text(f"Agent {n}", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(255,255,255,0.15)"}),
                                style={"padding": "4px 10px", "borderRadius": "4px", "background": "rgba(255,255,255,0.04)", "border": "1px solid rgba(255,255,255,0.05)"},
                            )
                            for n in range(1, 7)
                        ],
                        spacing="1",
                        wrap="wrap",
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                ),
                spacing="8",
                align="center",
                style={"padding": "36px 24px"},
            ),
            rx.box(),
        ),

        # Running state
        rx.cond(
            is_running,
            rx.box(
                # Batch progress bar
                rx.cond(
                    RunState.progress_total > 0,
                    rx.vstack(
                        rx.hstack(
                            rx.text("Batch Progress", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(255,255,255,0.22)", "letterSpacing": "0.07em", "textTransform": "uppercase"}),
                            rx.text(
                                RunState.progress_completed.length().to(str) + " / " + RunState.progress_total.to(str) + " startups",
                                style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": "rgba(255,255,255,0.4)"},
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.box(
                            rx.box(
                                style={
                                    "height": "100%",
                                    "background": DARK_BLUE,
                                    "borderRadius": "2px",
                                    "width": (RunState.progress_completed.length() * 100 // RunState.progress_total).to(str) + "%",
                                    "transition": "width 0.8s cubic-bezier(0.16,1,0.3,1)",
                                }
                            ),
                            style={"height": "3px", "background": "rgba(255,255,255,0.06)", "borderRadius": "2px", "overflow": "hidden"},
                        ),
                        spacing="1",
                        style={"marginBottom": "18px"},
                        width="100%",
                    ),
                    rx.box(),
                ),
                # Active startup cards (parallel grid)
                rx.cond(
                    RunState.progress_active.length() > 0,
                    rx.box(
                        rx.foreach(RunState.progress_active, startup_card),
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                            "gap": "12px",
                            "marginBottom": "18px",
                        },
                    ),
                    # Show spinner while waiting for first STARTUP_START
                    rx.hstack(
                        rx.spinner(size="1", style={"color": "rgba(255,255,255,0.2)"}),
                        rx.text("Initialising…", style={"fontSize": "11px", "color": "rgba(255,255,255,0.2)", "fontFamily": "'Courier New', monospace"}),
                        spacing="2",
                        align="center",
                        style={"padding": "12px 0", "marginBottom": "12px"},
                    ),
                ),
                # Ranking phase indicator
                rx.cond(
                    RunState.progress_ranking,
                    rx.hstack(
                        rx.spinner(size="1", style={"color": DARK_BLUE}),
                        rx.text("Ranking cohort…", style={"fontFamily": "'Courier New', monospace", "fontSize": "11px", "color": "rgba(74,143,214,0.65)", "letterSpacing": "0.04em"}),
                        spacing="2",
                        align="center",
                        style={"padding": "10px 0", "marginBottom": "12px"},
                    ),
                    rx.box(),
                ),
                # Completed startups
                rx.cond(
                    RunState.progress_completed.length() > 0,
                    rx.vstack(
                        rx.text("Done", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(255,255,255,0.2)", "letterSpacing": "0.07em", "textTransform": "uppercase", "marginBottom": "6px"}),
                        rx.vstack(
                            rx.foreach(RunState.progress_completed, completed_entry),
                            spacing="1",
                            style={"maxHeight": "160px", "overflowY": "auto"},
                            width="100%",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.box(),
                ),
                style={"padding": "22px 24px"},
            ),
            rx.box(),
        ),

        # Done state
        rx.cond(
            is_done,
            rx.hstack(
                rx.box(
                    rx.html('<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><polyline points="4,12 10,18 20,6" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
                    style={"width": "52px", "height": "52px", "background": "rgba(74,222,128,0.1)", "border": "1.5px solid rgba(74,222,128,0.22)", "borderRadius": "50%", "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                ),
                rx.vstack(
                    rx.text("Batch complete!", style={"fontFamily": "'Georgia', serif", "fontSize": "22px", "fontWeight": "900", "color": DARK_GREEN}),
                    rx.cond(
                        RunState.completed_batch_id != "",
                        rx.text("Results saved.", style={"fontSize": "12px", "color": "rgba(74,222,128,0.55)"}),
                        rx.text("Results saved.", style={"fontSize": "12px", "color": "rgba(74,222,128,0.55)"}),
                    ),
                    spacing="1",
                    align="start",
                    flex="1",
                ),
                rx.cond(
                    RunState.completed_batch_id != "",
                    rx.link(
                        "View Results →",
                        href="/batch/" + RunState.completed_batch_id,
                        style={
                            "display": "inline-flex",
                            "alignItems": "center",
                            "padding": "9px 20px",
                            "background": "rgba(74,222,128,0.1)",
                            "border": "1px solid rgba(74,222,128,0.22)",
                            "borderRadius": "8px",
                            "color": DARK_GREEN,
                            "fontSize": "13px",
                            "fontWeight": "600",
                            "textDecoration": "none",
                            "fontFamily": "'Plus Jakarta Sans', sans-serif",
                            "flexShrink": "0",
                            "transition": "background 0.15s",
                            "_hover": {"background": "rgba(74,222,128,0.18)"},
                        },
                    ),
                    rx.link("Dashboard →", href="/", style={"color": DARK_GREEN, "fontSize": "13px", "fontWeight": "600", "textDecoration": "none"}),
                ),
                spacing="6",
                align="center",
                style={"padding": "40px 24px"},
            ),
            rx.box(),
        ),

        # Error state
        rx.cond(
            is_error,
            rx.hstack(
                rx.box(
                    rx.text("!", style={"color": DARK_RED, "fontSize": "26px", "fontWeight": "900", "lineHeight": "1"}),
                    style={"width": "52px", "height": "52px", "background": "rgba(248,113,113,0.1)", "border": "1.5px solid rgba(248,113,113,0.22)", "borderRadius": "50%", "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                ),
                rx.vstack(
                    rx.text("Batch failed", style={"fontFamily": "'Georgia', serif", "fontSize": "22px", "fontWeight": "900", "color": DARK_RED}),
                    rx.text("Check the raw log below for details.", style={"fontSize": "12px", "color": "rgba(248,113,113,0.55)"}),
                    spacing="1",
                    align="start",
                ),
                spacing="6",
                align="center",
                style={"padding": "40px 24px"},
            ),
            rx.box(),
        ),

        # Raw log toggle
        rx.box(
            rx.el.button(
                rx.hstack(
                    rx.text(">_ Raw Log", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "fontWeight": "700", "color": "rgba(255,255,255,0.18)", "letterSpacing": "0.1em", "textTransform": "uppercase"}),
                    rx.cond(RunState.show_log, rx.text("▲", style={"fontSize": "8px", "color": "rgba(255,255,255,0.14)"}), rx.text("▼", style={"fontSize": "8px", "color": "rgba(255,255,255,0.14)"})),
                    spacing="2",
                    align="center",
                    justify="between",
                    width="100%",
                ),
                on_click=RunState.toggle_log,
                style={
                    "width": "100%",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "padding": "11px 20px",
                    "background": "none",
                    "border": "none",
                    "cursor": "pointer",
                    "transition": "background 0.12s",
                    "_hover": {"background": "rgba(255,255,255,0.02)"},
                },
            ),
            rx.cond(
                RunState.show_log,
                rx.box(
                    rx.cond(
                        RunState.log_lines.length() == 0,
                        rx.text("No output yet…", style={"color": "rgba(74,222,128,0.22)"}),
                        rx.vstack(
                            rx.foreach(RunState.log_lines, log_line),
                            spacing="0",
                            align="start",
                        ),
                    ),
                    style={
                        "background": "#060d18",
                        "padding": "14px 18px",
                        "fontFamily": "'Courier New', monospace",
                        "fontSize": "10px",
                        "color": DARK_GREEN,
                        "height": "230px",
                        "overflowY": "auto",
                        "whiteSpace": "pre-wrap",
                        "lineHeight": "1.9",
                        "borderTop": "1px solid rgba(255,255,255,0.04)",
                    },
                ),
                rx.box(),
            ),
            style={"borderTop": "1px solid rgba(255,255,255,0.05)"},
        ),

        style={
            "background": DARK_BG,
            "borderRadius": "16px",
            "overflow": "hidden",
            "boxShadow": "0 8px 48px rgba(7,16,30,0.2)",
        },
    )


# ── Full run page ──────────────────────────────────────────────────────────────

def run_page() -> rx.Component:
    return page_layout(
        # Page title
        rx.hstack(
            rx.vstack(
                section_marker("Pipeline Control"),
                rx.text(
                    "Run Batch",
                    style={"fontFamily": "'Georgia', serif", "fontSize": "36px", "fontWeight": "900", "color": TEXT, "letterSpacing": "-0.03em", "lineHeight": "1.05"},
                ),
                spacing="1",
                align="start",
            ),
            rx.hstack(
                rx.cond(
                    RunState.run_error != "",
                    rx.text(RunState.run_error, style={"fontSize": "12px", "color": RED, "fontWeight": "500"}),
                    rx.box(),
                ),
                rx.el.button(
                    rx.cond(
                        RunState.status != "running",
                        rx.hstack(
                            rx.html('<svg width="10" height="12" viewBox="0 0 10 12" fill="currentColor"><polygon points="0,0 10,6 0,12"/></svg>'),
                            rx.text(RunState.run_label, style={"color": "white", "fontSize": "14px", "fontWeight": "700"}),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.spinner(size="2", style={"color": "white"}),
                            rx.text("Running…", style={"color": "white", "fontSize": "14px", "fontWeight": "700"}),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    on_click=RunState.start_run,
                    disabled=(RunState.staged.length() == 0) | (RunState.status == "running"),
                    style={
                        "display": "inline-flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "gap": "8px",
                        "padding": "10px 24px",
                        "background": BLUE,
                        "border": "none",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontFamily": "'Plus Jakarta Sans', sans-serif",
                        "transition": "background 0.15s",
                        "_hover": {"background": BLUE_2},
                        "_disabled": {"opacity": "0.4", "cursor": "not-allowed"},
                    },
                ),
                spacing="3",
                align="center",
            ),
            justify="between",
            align="end",
            wrap="wrap",
            style={"marginBottom": "28px"},
        ),

        # Controls card
        rx.box(
            # Upload row
            rx.box(
                rx.hstack(
                    rx.box(
                        rx.text("1", style={"fontFamily": "'Georgia', serif", "fontSize": "9px", "fontWeight": "900", "color": "white", "lineHeight": "1"}),
                        style={"width": "20px", "height": "20px", "borderRadius": "50%", "background": BLUE, "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                    ),
                    section_marker("Add startup(s)"),
                    spacing="2",
                    align="center",
                    style={"marginBottom": "14px"},
                ),
                # Hidden native file inputs — JS wires webkitdirectory + onchange after mount
                rx.el.input(
                    type="file",
                    id="evalbot-folder-input",
                    style={"display": "none"},
                ),
                rx.el.input(
                    type="file",
                    id="evalbot-batch-input",
                    style={"display": "none"},
                ),
                # Two upload mode buttons side-by-side
                rx.hstack(
                    # Single Startup
                    rx.vstack(
                        rx.el.button(
                            rx.hstack(
                                rx.html(
                                    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
                                    'stroke="currentColor" stroke-width="2">'
                                    '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
                                    "</svg>"
                                ),
                                rx.text("Single Startup"),
                                spacing="2",
                                align="center",
                            ),
                            on_click=rx.call_script(
                                "document.getElementById('evalbot-folder-input').click()"
                            ),
                            disabled=RunState.status == "running",
                            style={
                                "padding": "8px 18px",
                                "background": SURFACE_2,
                                "border": f"1.5px solid {BORDER}",
                                "borderRadius": "7px",
                                "fontSize": "13px",
                                "color": TEXT_2,
                                "cursor": "pointer",
                                "fontFamily": "'Plus Jakarta Sans', sans-serif",
                                "fontWeight": "500",
                                "transition": "border-color 0.15s",
                                "_hover": {"borderColor": BLUE},
                                "_disabled": {"opacity": "0.5", "cursor": "not-allowed"},
                            },
                        ),
                        rx.text(
                            "Pick the startup folder directly — folder name becomes the startup name.",
                            style={"fontSize": "11px", "color": TEXT_3, "marginTop": "4px"},
                        ),
                        spacing="0",
                        align="start",
                        flex="1",
                    ),
                    # Vertical divider
                    rx.box(
                        style={
                            "width": "1px",
                            "alignSelf": "stretch",
                            "background": BORDER,
                            "margin": "0 8px",
                        }
                    ),
                    # Batch Folder
                    rx.vstack(
                        rx.el.button(
                            rx.hstack(
                                rx.html(
                                    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
                                    'stroke="currentColor" stroke-width="2">'
                                    '<path d="M3 7a2 2 0 0 1 2-2h3.586a1 1 0 0 1 .707.293L11 7h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>'
                                    '<rect x="3" y="10" width="18" height="9" rx="1"/>'
                                    "</svg>"
                                ),
                                rx.text("Batch Folder"),
                                spacing="2",
                                align="center",
                            ),
                            on_click=rx.call_script(
                                "document.getElementById('evalbot-batch-input').click()"
                            ),
                            disabled=RunState.status == "running",
                            style={
                                "padding": "8px 18px",
                                "background": SURFACE_2,
                                "border": f"1.5px solid {BORDER_2}",
                                "borderRadius": "7px",
                                "fontSize": "13px",
                                "color": TEXT_2,
                                "cursor": "pointer",
                                "fontFamily": "'Plus Jakarta Sans', sans-serif",
                                "fontWeight": "500",
                                "transition": "border-color 0.15s",
                                "_hover": {"borderColor": "#7c3aed"},
                                "_disabled": {"opacity": "0.5", "cursor": "not-allowed"},
                            },
                        ),
                        rx.text(
                            "Pick a folder containing startup subfolders — each subfolder becomes one startup.",
                            style={"fontSize": "11px", "color": TEXT_3, "marginTop": "4px"},
                        ),
                        spacing="0",
                        align="start",
                        flex="1",
                    ),
                    spacing="0",
                    align="start",
                    width="100%",
                ),
                style={"padding": "20px 24px", "borderBottom": f"1px solid {BORDER}"},
            ),

            # Staged list
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            rx.text("2", style={"fontFamily": "'Georgia', serif", "fontSize": "9px", "fontWeight": "900", "color": TEXT_2, "lineHeight": "1"}),
                            style={"width": "20px", "height": "20px", "borderRadius": "50%", "background": SURFACE_3, "border": f"1.5px solid {BORDER_2}", "display": "flex", "alignItems": "center", "justifyContent": "center", "flexShrink": "0"},
                        ),
                        section_marker("Staged"),
                        rx.cond(
                            RunState.staged.length() > 0,
                            rx.box(
                                rx.text(RunState.staged.length().to(str) + " startup" + rx.cond(RunState.staged.length() == 1, "", "s"), style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "fontWeight": "700", "color": BLUE}),
                                style={"background": BLUE_BG, "padding": "2px 7px", "borderRadius": "3px"},
                            ),
                            rx.box(),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.cond(
                        RunState.has_multi_file,
                        rx.el.button(
                            rx.cond(RunState.filter_single, "✓ Multi-file only", "Hide single-file"),
                            on_click=RunState.toggle_filter,
                            style={
                                "fontSize": "11px",
                                "fontWeight": "600",
                                "padding": "4px 10px",
                                "borderRadius": "5px",
                                "border": "1.5px solid",
                                "cursor": "pointer",
                                "fontFamily": "'Plus Jakarta Sans', sans-serif",
                                "transition": "all 0.15s",
                                "color": rx.cond(RunState.filter_single, BLUE, TEXT_3),
                                "background": rx.cond(RunState.filter_single, BLUE_BG, SURFACE_2),
                                "borderColor": rx.cond(RunState.filter_single, "rgba(27,72,196,0.3)", BORDER_2),
                            },
                        ),
                        rx.box(),
                    ),
                    justify="between",
                    align="center",
                    style={"marginBottom": "12px"},
                ),
                rx.cond(
                    RunState.staged_visible.length() == 0,
                    rx.text(
                        rx.cond(
                            RunState.staged.length() == 0,
                            "No startups staged yet — choose a folder above.",
                            "All staged startups have a single file (filter active).",
                        ),
                        style={"padding": "16px 0", "textAlign": "center", "color": TEXT_4, "fontSize": "13px"},
                    ),
                    rx.vstack(
                        rx.foreach(
                            RunState.staged_visible,
                            staged_row,
                        ),
                        spacing="1",
                        style={"maxHeight": "220px", "overflowY": "auto"},
                        width="100%",
                    ),
                ),
                style={"padding": "18px 24px"},
            ),

            style={
                "background": SURFACE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "marginBottom": "20px",
                "overflow": "hidden",
                "boxShadow": "0 2px 12px rgba(12,24,41,0.05)",
            },
        ),

        # Pipeline monitor
        pipeline_monitor(),
    )

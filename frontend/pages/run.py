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


# ── Agent progress bars ────────────────────────────────────────────────────────

def agent_bar(n: int) -> rx.Component:
    is_done = RunState.progress_done_agents.contains(n)
    is_current = (RunState.progress_current_agent == n) & ~is_done

    bar_bg = rx.cond(
        is_done,
        "rgba(74,222,128,0.7)",
        rx.cond(is_current, DARK_BLUE, "rgba(255,255,255,0.0)"),
    )
    bar_w = rx.cond(is_done | is_current, "100%", "0%")

    icon = rx.cond(
        is_done,
        rx.html('<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><circle cx="5.5" cy="5.5" r="5" stroke="rgba(74,222,128,0.55)" stroke-width="0.8"/><polyline points="2.5,5.5 4.5,7.5 8.5,3.5" stroke="rgba(74,222,128,0.9)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
        rx.cond(
            is_current,
            rx.spinner(size="1", style={"color": DARK_BLUE}),
            rx.box(style={"width": "11px", "height": "11px"}),
        ),
    )

    return rx.hstack(
        rx.text(f"A{n}", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(255,255,255,0.18)", "width": "18px", "flexShrink": "0"}),
        rx.box(
            rx.box(
                style={
                    "height": "100%",
                    "borderRadius": "2px",
                    "background": bar_bg,
                    "width": bar_w,
                    "transition": "width 0.4s, background 0.4s",
                }
            ),
            style={"flex": "1", "height": "3px", "background": "rgba(255,255,255,0.06)", "borderRadius": "2px", "overflow": "hidden"},
        ),
        rx.box(icon, style={"width": "14px", "flexShrink": "0", "display": "flex", "justifyContent": "center"}),
        spacing="2",
        align="center",
        width="100%",
    )


# ── Staged startup row ────────────────────────────────────────────────────────

def staged_row(s: dict) -> rx.Component:
    files_str = s["files"].join(" · ")
    return rx.hstack(
        rx.vstack(
            rx.text(s["name"], style={"fontSize": "13px", "fontWeight": "700", "color": TEXT}),
            rx.text(files_str, style={"fontFamily": "'Courier New', monospace", "fontSize": "10px", "color": TEXT_3, "marginTop": "1px", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}),
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
    return rx.hstack(
        rx.text(entry["name"], style={"fontSize": "11px", "fontWeight": "600", "color": "rgba(74,222,128,0.8)", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}),
        rx.text(
            entry["elapsed_s"].to(str) + "s",
            style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(74,222,128,0.4)", "flexShrink": "0"},
        ),
        justify="between",
        align="center",
        style={"padding": "4px 8px", "background": "rgba(74,222,128,0.05)", "borderRadius": "4px", "borderLeft": "2px solid rgba(74,222,128,0.35)"},
        width="100%",
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
                rx.hstack(
                    # Left: current startup + agent bars
                    rx.vstack(
                        rx.box(
                            rx.text("Now Processing", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(74,143,214,0.55)", "letterSpacing": "0.08em", "textTransform": "uppercase", "marginBottom": "6px"}),
                            rx.cond(
                                RunState.progress_current_name != "",
                                rx.vstack(
                                    rx.text(RunState.progress_current_name, style={"fontSize": "16px", "fontWeight": "700", "color": "white", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap", "marginBottom": "3px"}),
                                    rx.cond(
                                        RunState.progress_current_role != "",
                                        rx.text(RunState.progress_current_role, style={"fontSize": "11px", "color": "rgba(255,255,255,0.3)"}),
                                        rx.box(),
                                    ),
                                    spacing="0",
                                    align="start",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.spinner(size="1", style={"color": "rgba(255,255,255,0.2)"}),
                                    rx.text("Initialising…", style={"fontSize": "11px", "color": "rgba(255,255,255,0.2)"}),
                                    spacing="2",
                                    align="center",
                                ),
                            ),
                            style={"padding": "14px 16px", "background": "rgba(74,143,214,0.08)", "borderRadius": "9px", "border": "1px solid rgba(74,143,214,0.14)", "marginBottom": "16px"},
                        ),
                        rx.vstack(
                            *[agent_bar(n) for n in range(1, 7)],
                            spacing="2",
                            width="100%",
                        ),
                        spacing="0",
                        align="start",
                        flex="1",
                    ),
                    # Right: elapsed + completed
                    rx.vstack(
                        rx.vstack(
                            rx.text(
                                RunState.progress_elapsed.to(str) + "s",
                                style={"fontFamily": "'Georgia', serif", "fontSize": "38px", "fontWeight": "900", "color": DARK_BLUE, "lineHeight": "1", "letterSpacing": "-0.03em"},
                            ),
                            rx.text("ELAPSED", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(74,143,214,0.4)", "letterSpacing": "0.06em", "marginTop": "3px"}),
                            spacing="0",
                            align="end",
                            style={"marginBottom": "16px"},
                        ),
                        rx.cond(
                            RunState.progress_completed.length() > 0,
                            rx.vstack(
                                rx.text("Done", style={"fontFamily": "'Courier New', monospace", "fontSize": "9px", "color": "rgba(255,255,255,0.2)", "letterSpacing": "0.07em", "textTransform": "uppercase", "marginBottom": "6px"}),
                                rx.vstack(
                                    rx.foreach(RunState.progress_completed, completed_entry),
                                    spacing="1",
                                    style={"maxHeight": "120px", "overflowY": "auto"},
                                    width="100%",
                                ),
                                spacing="0",
                                align="start",
                            ),
                            rx.box(),
                        ),
                        spacing="0",
                        align="end",
                        style={"minWidth": "160px"},
                    ),
                    spacing="5",
                    align="start",
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
                            rx.text("Run Batch", style={"color": "white", "fontSize": "14px", "fontWeight": "700"}),
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
                    section_marker("Add startup"),
                    spacing="2",
                    align="center",
                    style={"marginBottom": "14px"},
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Name", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "marginBottom": "5px", "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                        rx.el.input(
                            value=RunState.new_startup_name,
                            on_change=RunState.set_new_startup_name,
                            placeholder="e.g. AcmeCorp",
                            disabled=RunState.status == "running",
                            style={
                                "width": "100%",
                                "background": SURFACE,
                                "border": f"1.5px solid {BORDER}",
                                "color": TEXT,
                                "borderRadius": "7px",
                                "padding": "8px 12px",
                                "fontFamily": "'Plus Jakarta Sans', sans-serif",
                                "fontSize": "13px",
                                "outline": "none",
                                "_focus": {"borderColor": BLUE, "boxShadow": "0 0 0 3px rgba(27,72,196,0.12)"},
                                "_disabled": {"opacity": "0.5"},
                            },
                        ),
                        spacing="1",
                        align="start",
                        flex="1",
                    ),
                    rx.vstack(
                        rx.text("Files (.pdf .docx .txt .md)", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_3, "marginBottom": "5px", "letterSpacing": "0.06em", "textTransform": "uppercase"}),
                        rx.upload(
                            rx.el.button(
                                "Choose files",
                                style={
                                    "padding": "8px 14px",
                                    "background": SURFACE_2,
                                    "border": f"1.5px solid {BORDER}",
                                    "borderRadius": "7px",
                                    "fontSize": "13px",
                                    "color": TEXT_2,
                                    "cursor": "pointer",
                                    "fontFamily": "'Plus Jakarta Sans', sans-serif",
                                    "fontWeight": "500",
                                    "_hover": {"borderColor": BLUE},
                                },
                            ),
                            id="startup_upload",
                            multiple=True,
                            accept={
                                "application/pdf": [".pdf"],
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                                "text/plain": [".txt"],
                                "text/markdown": [".md"],
                            },
                            style={"width": "100%"},
                        ),
                        spacing="1",
                        align="start",
                        flex="1",
                    ),
                    rx.el.button(
                        "+ Add",
                        on_click=RunState.upload_files(rx.upload_files(upload_id="startup_upload")),
                        disabled=(RunState.status == "running") | (RunState.new_startup_name.strip() == ""),
                        style={
                            "padding": "8px 18px",
                            "background": BLUE,
                            "color": "white",
                            "border": "none",
                            "borderRadius": "7px",
                            "fontSize": "13px",
                            "fontWeight": "700",
                            "cursor": "pointer",
                            "alignSelf": "flex-end",
                            "fontFamily": "'Plus Jakarta Sans', sans-serif",
                            "transition": "background 0.15s",
                            "_hover": {"background": BLUE_2},
                            "_disabled": {"opacity": "0.4", "cursor": "not-allowed"},
                        },
                    ),
                    spacing="3",
                    align="end",
                    style={"marginBottom": "8px"},
                ),
                rx.cond(
                    RunState.upload_error != "",
                    rx.text(RunState.upload_error, style={"fontSize": "11px", "color": RED, "fontWeight": "500"}),
                    rx.box(style={"minHeight": "16px"}),
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
                    justify="between",
                    align="center",
                    style={"marginBottom": "12px"},
                ),
                rx.cond(
                    RunState.staged.length() == 0,
                    rx.text("No startups staged yet — upload files above.", style={"padding": "16px 0", "textAlign": "center", "color": TEXT_4, "fontSize": "13px"}),
                    rx.vstack(
                        rx.foreach(
                            RunState.staged,
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

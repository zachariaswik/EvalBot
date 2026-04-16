"""Tests for main.py helper and export behaviors."""

from __future__ import annotations

import main as main_mod


def test_sorted_agent_numbers_handles_mixed_keys():
    outputs = {3: {"ok": True}, "1": {"ok": True}, "_tags": ["x"], "bad": {}}
    assert main_mod._sorted_agent_numbers(outputs) == [1, 3]


def test_int_keyed_agent_outputs_normalizes_numeric_string_keys():
    outputs = {1: {"a": 1}, "2": {"b": 2}, "_tags": ["x"], "not_an_agent": {"y": 3}}
    normalized = main_mod._int_keyed_agent_outputs(outputs)
    assert normalized == {1: {"a": 1}, 2: {"b": 2}}


def test_export_results_writes_startup_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(main_mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(main_mod, "_write_batch_summary", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        main_mod,
        "generate_startup_feedback_pdf",
        lambda batch_id, startup_name, outputs: b"%PDF-1.4\nfake",
    )

    result = {
        1: {"problem": "Painful workflow"},
        "2": {"verdict": "Promising"},
        "_tags": ["alpha"],
    }
    out_dir = main_mod.export_results("batch_42", {"Acme Co": result}, is_batch_mode=False)

    safe_name = main_mod._sanitize_filename("Acme Co")
    startup_dir = out_dir / safe_name
    pdf_path = startup_dir / f"{safe_name}_evalbot_feedback.pdf"

    assert (startup_dir / f"{safe_name}.json").exists()
    assert (startup_dir / f"{safe_name}.md").exists()
    assert pdf_path.exists()
    assert pdf_path.read_bytes().startswith(b"%PDF")

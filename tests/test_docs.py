"""Tests for src/docs.py — document loading."""

from __future__ import annotations

import pytest

from src.docs import load_submission


class TestLoadSubmissionSingleFile:
    def test_text_file(self, tmp_path):
        f = tmp_path / "pitch.txt"
        f.write_text("We build rockets.", encoding="utf-8")
        result = load_submission(f)
        assert result == "We build rockets."

    def test_md_file(self, tmp_path):
        f = tmp_path / "pitch.md"
        f.write_text("# Startup\nWe solve problems.", encoding="utf-8")
        result = load_submission(f)
        assert "Startup" in result

    def test_pdf_file_returns_reference_marker(self, tmp_path):
        f = tmp_path / "deck.pdf"
        f.write_bytes(b"%PDF-1.4")
        result = load_submission(f)
        assert result.startswith("[PDF_FILE:")
        assert str(f.absolute()) in result

    def test_pdf_marker_format(self, tmp_path):
        f = tmp_path / "deck.pdf"
        f.write_bytes(b"%PDF-1.4")
        result = load_submission(f)
        # Must be in the exact format Agent 1 expects
        assert result == f"[PDF_FILE: {f.absolute()}]"


class TestLoadSubmissionDirectory:
    def test_single_md_file(self, tmp_path):
        (tmp_path / "pitch.md").write_text("# MyStartup\nWe fix things.", encoding="utf-8")
        result = load_submission(tmp_path)
        assert "MyStartup" in result
        assert "We fix things" in result

    def test_multiple_md_files_combined(self, tmp_path):
        (tmp_path / "pitch.md").write_text("# Pitch\nHere is the idea.")
        (tmp_path / "team.md").write_text("# Team\nBob and Alice.")
        result = load_submission(tmp_path)
        assert "Pitch" in result
        assert "Team" in result

    def test_pdf_file_in_directory(self, tmp_path):
        (tmp_path / "deck.pdf").write_bytes(b"%PDF-1.4")
        result = load_submission(tmp_path)
        assert "[PDF_FILE:" in result

    def test_mixed_md_and_pdf(self, tmp_path):
        (tmp_path / "notes.md").write_text("Some notes.")
        (tmp_path / "deck.pdf").write_bytes(b"%PDF-1.4")
        result = load_submission(tmp_path)
        assert "Some notes" in result
        assert "[PDF_FILE:" in result

    def test_empty_directory_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match=tmp_path.name):
            load_submission(tmp_path)

    def test_directory_with_unsupported_files_raises(self, tmp_path):
        (tmp_path / "data.csv").write_text("a,b,c")
        with pytest.raises(FileNotFoundError):
            load_submission(tmp_path)

    def test_separator_between_md_files(self, tmp_path):
        (tmp_path / "a.md").write_text("Part A.")
        (tmp_path / "b.md").write_text("Part B.")
        result = load_submission(tmp_path)
        # Files should be separated by the standard separator
        assert "---" in result


class TestLoadSubmissionDocx:
    def test_docx_extraction_failure_raises(self, tmp_path, monkeypatch):
        """If DOCX extraction returns None, ValueError is raised."""
        import src.docs as docs_module
        monkeypatch.setattr(docs_module, "_extract_text_from_docx", lambda _: None)
        f = tmp_path / "deck.docx"
        f.write_bytes(b"fake docx content")
        with pytest.raises(ValueError, match="Could not extract content"):
            load_submission(f)

    def test_docx_extraction_success(self, tmp_path, monkeypatch):
        """Successful DOCX extraction returns the extracted text."""
        import src.docs as docs_module
        monkeypatch.setattr(docs_module, "_extract_text_from_docx",
                            lambda _: "Extracted text from deck")
        f = tmp_path / "deck.docx"
        f.write_bytes(b"fake docx content")
        result = load_submission(f)
        assert result == "Extracted text from deck"

    def test_docx_in_directory(self, tmp_path, monkeypatch):
        """DOCX files in a directory are included in the output."""
        import src.docs as docs_module
        monkeypatch.setattr(docs_module, "_extract_text_from_docx",
                            lambda p: f"Content of {p.name}")
        (tmp_path / "pitch.docx").write_bytes(b"fake")
        result = load_submission(tmp_path)
        assert "pitch.docx" in result

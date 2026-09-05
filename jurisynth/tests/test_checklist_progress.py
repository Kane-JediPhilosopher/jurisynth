from jurisynth.checklist_progress import progress


def test_progress_counts_markdown_checkboxes(tmp_path):
    checklist = tmp_path / "CHECKLIST.md"
    checklist.write_text("- [x] done\n  - [ ] open\n", encoding="utf-8")
    assert progress(checklist) == {"complete": 1, "remaining": 1, "total": 2, "percent": 50.0}

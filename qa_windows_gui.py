"""Disposable Windows desktop GUI acceptance for Folder Automation Engine -2.

Runs on a hosted Windows CI desktop, not the customer's PC. Generates
screenshots and a JSON report. Exercises only synthetic files under a temporary
directory. No real user folders, Store operations, or external services.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab

from folder_desktop_app import FolderDesktop


def pump(root: tk.Tk, predicate, *, seconds: float = 15.0) -> None:
    until = time.monotonic() + seconds
    while time.monotonic() < until:
        root.update()
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError("GUI did not reach the expected state within the test deadline")


def screenshot(root: tk.Tk, out: Path, filename: str) -> dict:
    root.deiconify()
    root.lift()
    root.focus_force()
    root.update()
    time.sleep(0.25)
    root.update()
    left, top = root.winfo_rootx(), root.winfo_rooty()
    width, height = root.winfo_width(), root.winfo_height()
    if width < 700 or height < 550:
        raise AssertionError(f"Unexpectedly small GUI: {width} x {height}")
    image = ImageGrab.grab(bbox=(left, top, left + width, top + height))
    path = out / filename
    image.save(path)
    if path.stat().st_size < 4500:
        raise AssertionError(f"Screenshot looks empty/truncated: {path}")
    return {"file": str(path), "resolution": [width, height], "bytes": path.stat().st_size}


def button_texts(widget: tk.Misc) -> set[str]:
    texts: set[str] = set()
    for child in widget.winfo_children():
        if isinstance(child, ttk.Button):
            texts.add(str(child.cget("text")))
        texts.update(button_texts(child))
    return texts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("gui-review-evidence"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="folder-v2-gui-qa-") as tmp:
        safe = Path(tmp)
        inbox, output = safe / "inbox", safe / "processed"
        inbox.mkdir()
        output.mkdir()
        sample = inbox / "report.pdf"
        sample.write_bytes(b"consumer v2 synthetic Windows GUI test")

        root = tk.Tk()
        try:
            root.title("Folder Automation Engine -2 | Windows QA")
            app = FolderDesktop(root)
            app.root_path.set(str(safe))
            root.geometry("1024x768+30+30")
            pump(root, lambda: root.winfo_ismapped() == 1)
            assert "試運転（変更なし）" in button_texts(root)
            assert "確認して1回実行" in button_texts(root)
            if app.watch_panel.winfo_manager():
                raise AssertionError("Advanced auto-watch must be collapsed by default")
            if not app.run_btn.winfo_ismapped():
                raise AssertionError("Main execution button must remain visible")
            checks.append({"case": "japanese_1024x768", **screenshot(root, args.output, "folder-v2-ja-1024x768.png")})

            # Native picker selection is patched to only return synthetic folders.
            with patch("folder_desktop_app.filedialog.askdirectory", return_value=str(inbox)):
                app._choose_child_folder(for_input=True)
            with patch("folder_desktop_app.filedialog.askdirectory", return_value=str(output)):
                app._choose_child_folder(for_input=False)
            if app.input_folder.get() != "inbox" or app.output_folder.get() != "processed":
                raise AssertionError("Folder picker did not populate configured source/destination")

            app.preview()
            pump(root, lambda: app.preview_revision is not None and not app.busy)
            if not sample.exists() or (output / sample.name).exists():
                raise AssertionError("Dry Run unexpectedly wrote or removed files")
            if len(app.preview_table.get_children()) != 1:
                raise AssertionError("Plan table missing the exact one-file preview")
            values = app.preview_table.item(app.preview_table.get_children()[0], "values")
            if tuple(values) != ("report.pdf", "processed/report.pdf", "コピー", "予定"):
                raise AssertionError("Incorrect visual file plan: " + str(values))
            checks.append({"case": "plan_table_shows_real_engine_output", "passed": True})
            checks.append({"case": "dry_run_local_only", "passed": True,
                           "source_retained": True, "destination_absent": True})

            # Approve copy only on synthetic temporary input/output. Never
            # allow tests to read any other local location.
            with patch("folder_desktop_app.messagebox.askyesno", return_value=True):
                app.run_live()
            pump(root, lambda: (output / sample.name).exists() and not app.busy)
            if not sample.exists() or (output / sample.name).read_bytes() != sample.read_bytes():
                raise AssertionError("Approved copy damaged synthetic original")
            checks.append({"case": "approved_copy", "passed": True, "source_retained": True})
            app.toggle_watcher()
            if not app.watch_panel.winfo_manager():
                raise AssertionError("Optional watcher section did not open")
            app.toggle_watcher()
            if app.watch_panel.winfo_manager():
                raise AssertionError("Optional watcher section did not close")
            checks.append({"case": "optional_watcher_expand_and_collapse", "passed": True})

            # A saved configuration must survive UI changes and never reuse approval.
            saved = safe / "safe-settings.json"
            with patch("folder_desktop_app.filedialog.asksaveasfilename", return_value=str(saved)):
                app.save_config()
            if not saved.is_file():
                raise AssertionError("Saved settings file was not created")
            app.set_quick_pattern("*.png")
            with patch("folder_desktop_app.filedialog.askopenfilename", return_value=str(saved)):
                app.load_config()
            if app.pattern.get() != "*.pdf" or app.preview_revision is not None:
                raise AssertionError("Saved rules did not restore safely")
            checks.append({"case": "saved_rules_restore_and_revoke_preview", "passed": True})

            # Rebuild the visible widget tree in English and verify action remains copy.
            app.lang.set("English")
            app.change_language()
            root.geometry("1280x720+30+30")
            pump(root, lambda: "Dry Run (no changes)" in button_texts(root))
            if app.action.get() != "copy" or app.pattern.get() != "*.pdf":
                raise AssertionError("UI translation changed folder rules")
            checks.append({"case": "english_requested1280x720", **screenshot(root, args.output, "folder-v2-en-requested1280x720.png")})
            # UI-only language switch may not grant a new preview if the user
            # has altered a rule. Verify changing file pattern does invalidate.
            app.set_quick_pattern("*.png")
            if app.preview_revision is not None or app.preview_input_snapshot is not None:
                raise AssertionError("Changing file type did not revoke old preview")
            checks.append({"case": "changed_rule_requires_preview", "passed": True})

            # Higher Windows text scaling with the same 1024x768 viewport.
            original_scaling = float(root.tk.call("tk", "scaling"))
            try:
                root.tk.call("tk", "scaling", original_scaling * 1.5)
                app.build()
                root.geometry("1024x768+30+30")
                root.update()
                checks.append({"case": "english_high_scaling_1024x768",
                               **screenshot(root, args.output, "folder-v2-en-1024x768-large-text.png")})
            finally:
                root.tk.call("tk", "scaling", original_scaling)
        finally:
            root.destroy()

    result = {"product": "Folder Automation Engine -2", "scope": "CI Windows GUI QA, synthetic files only",
              "store_submission": False, "installed_msix": False,
              "human_review_complete": False,
              "full_1280x720_viewport_verified": any(
                  item.get("case") == "english_requested1280x720"
                  and item.get("resolution", [0, 0])[0] >= 1280
                  and item.get("resolution", [0, 0])[1] >= 720 for item in checks),
              "checks": checks}
    (args.output / "gui_qa_report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("WINDOWS-GUI-QA PASS: " + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

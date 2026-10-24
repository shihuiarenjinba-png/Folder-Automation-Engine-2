"""Read-only display adapter for Folder -2 engine audit events."""
import json
from pathlib import Path

def parse_preview_rows(raw: str, *, japanese: bool, max_rows: int = 300) -> list[tuple[str,str,str,str]]:
    rows = []
    for line in raw.splitlines():
        if line.startswith("BLOCKED destination exists:"):
            if rows:
                name, dest, action, _ = rows[-1]
                rows[-1] = (name, dest, action, "上書き回避" if japanese else "Already exists")
            continue
        try:
            item = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(item, dict) or not {"file", "action", "destination"} <= item.keys():
            continue
        if item["action"] not in {"copy", "move"} or len(rows) >= max_rows:
            continue
        dest = Path(str(item["destination"]))
        action = ("コピー" if item["action"] == "copy" else "移動") if japanese else (
            "Copy" if item["action"] == "copy" else "Move")
        status = ("予定" if item.get("dry_run") else "実行ログ") if japanese else (
            "Planned" if item.get("dry_run") else "Execution log")
        rows.append((Path(str(item["file"])).name, str(dest.parent.name + "/" + dest.name), action, status))
    return rows

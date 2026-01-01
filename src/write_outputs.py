import json
from datetime import datetime, timezone
from pathlib import Path

def write_data_json(rows: list[dict], out_path: str = "docs/data.json") -> None:
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "updated_utc": updated,
        "rows": rows,
    }
    Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

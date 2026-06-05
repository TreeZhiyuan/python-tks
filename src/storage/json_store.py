from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class JsonSnapshotStore:
    output_dir: Path

    def write_snapshot(
        self,
        task_name: str,
        rows: list[dict[str, Any]],
        request_params: dict[str, Any] | None = None,
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / f"{task_name}.json"
        payload = {
            "task_name": task_name,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "request_params": request_params or {},
            "row_count": len(rows),
            "rows": rows,
        }
        output_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_file

    def read_snapshot(self, task_name: str) -> dict[str, Any]:
        input_file = self.output_dir / f"{task_name}.json"
        return json.loads(input_file.read_text(encoding="utf-8"))

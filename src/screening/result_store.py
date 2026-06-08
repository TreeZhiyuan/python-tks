from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class StrategyResultStore:
    output_dir: Path

    def write_result(
        self,
        run_date: str,
        mode: str,
        strategy_names: list[str],
        strategy_descriptions: dict[str, str],
        rows: list[dict[str, Any]],
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        strategy_slug = "_".join(strategy_names)
        output_file = self.output_dir / f"{run_date}_{mode}_{strategy_slug}.json"
        payload = {
            "task_name": "strategy_runner",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "run_date": run_date,
            "mode": mode,
            "strategies": [
                {
                    "name": strategy_name,
                    "description": strategy_descriptions[strategy_name],
                }
                for strategy_name in strategy_names
            ],
            "row_count": len(rows),
            "rows": rows,
        }
        output_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_file

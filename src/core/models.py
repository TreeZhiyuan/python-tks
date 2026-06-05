from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskRunResult:
    task_name: str
    trade_date: Optional[str]
    row_count: int
    written_count: int
    output_path: Optional[str] = None

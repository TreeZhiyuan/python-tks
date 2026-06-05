from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.tasks.moneyflow import MoneyflowTask
from src.tasks.moneyflow_cnt_ths import MoneyflowCntThsTask
from src.tasks.moneyflow_dc import MoneyflowDcTask
from src.tasks.moneyflow_ind_dc import MoneyflowIndDcTask
from src.tasks.moneyflow_ths import MoneyflowThsTask
from src.tasks.stock_basic import StockBasicTask


TaskFactory = Callable[[], Any]


@dataclass(frozen=True)
class TaskDefinition:
    name: str
    description: str
    doc_url: str
    factory: TaskFactory
    schedule_hour: int
    schedule_minute: int
    uses_trade_date: bool = True
    interval_days: int | None = None
    interval_start_date: str | None = None

    @property
    def schedule_id(self) -> str:
        suffix = f"every_{self.interval_days}_days" if self.interval_days else "daily"
        return f"{self.name}_{suffix}"


TASK_REGISTRY: dict[str, TaskDefinition] = {
    "moneyflow_cnt_ths": TaskDefinition(
        name="moneyflow_cnt_ths",
        description="同花顺概念板块每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=371",
        factory=MoneyflowCntThsTask,
        schedule_hour=1,
        schedule_minute=0,
    ),
    "moneyflow_ind_dc": TaskDefinition(
        name="moneyflow_ind_dc",
        description="东财概念及行业板块每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=344",
        factory=MoneyflowIndDcTask,
        schedule_hour=1,
        schedule_minute=5,
    ),
    "moneyflow": TaskDefinition(
        name="moneyflow",
        description="沪深A股个股每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=170",
        factory=MoneyflowTask,
        schedule_hour=1,
        schedule_minute=10,
    ),
    "moneyflow_dc": TaskDefinition(
        name="moneyflow_dc",
        description="东方财富个股每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=349",
        factory=MoneyflowDcTask,
        schedule_hour=1,
        schedule_minute=15,
    ),
    "moneyflow_ths": TaskDefinition(
        name="moneyflow_ths",
        description="同花顺个股每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=348",
        factory=MoneyflowThsTask,
        schedule_hour=1,
        schedule_minute=20,
    ),
    "stock_basic": TaskDefinition(
        name="stock_basic",
        description="股票基础信息，包括股票代码、名称、上市日期、退市日期等",
        doc_url="https://tushare.pro/document/2?doc_id=25",
        factory=StockBasicTask,
        schedule_hour=0,
        schedule_minute=30,
        uses_trade_date=False,
        interval_days=7,
        interval_start_date="2026-06-05 00:30:00",
    ),
}


def available_task_names() -> list[str]:
    return list(TASK_REGISTRY.keys())


def available_task_definitions() -> list[TaskDefinition]:
    return list(TASK_REGISTRY.values())


def get_task_definition(task_name: str) -> TaskDefinition:
    try:
        return TASK_REGISTRY[task_name]
    except KeyError as exc:
        available = ", ".join(available_task_names())
        raise ValueError(f"Unknown task '{task_name}'. Available tasks: {available}") from exc


def build_task(task_name: str) -> Any:
    return get_task_definition(task_name).factory()


def resolve_task_names(task_names: list[str]) -> list[str]:
    if "all" in task_names:
        return available_task_names()

    seen: set[str] = set()
    resolved: list[str] = []
    for task_name in task_names:
        if task_name not in TASK_REGISTRY:
            available = ", ".join(["all", *available_task_names()])
            raise ValueError(f"Unknown task '{task_name}'. Available tasks: {available}")
        if task_name not in seen:
            seen.add(task_name)
            resolved.append(task_name)
    return resolved

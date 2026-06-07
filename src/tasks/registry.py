from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.tasks.daily import DailyTask
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
    uses_trade_date: bool = True


TASK_REGISTRY: dict[str, TaskDefinition] = {
    "moneyflow_cnt_ths": TaskDefinition(
        name="moneyflow_cnt_ths",
        description="同花顺概念板块每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=371",
        factory=MoneyflowCntThsTask,
    ),
    "moneyflow_ind_dc": TaskDefinition(
        name="moneyflow_ind_dc",
        description="东财概念及行业板块每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=344",
        factory=MoneyflowIndDcTask,
    ),
    "moneyflow": TaskDefinition(
        name="moneyflow",
        description="沪深A股个股每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=170",
        factory=MoneyflowTask,
    ),
    "moneyflow_dc": TaskDefinition(
        name="moneyflow_dc",
        description="东方财富个股每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=349",
        factory=MoneyflowDcTask,
    ),
    "moneyflow_ths": TaskDefinition(
        name="moneyflow_ths",
        description="同花顺个股每日资金流向",
        doc_url="https://tushare.pro/document/2?doc_id=348",
        factory=MoneyflowThsTask,
    ),
    "stock_basic": TaskDefinition(
        name="stock_basic",
        description="股票基础信息，默认只保留 list_status=L 且 market 为主板/创业板的上市股票",
        doc_url="https://tushare.pro/document/2?doc_id=25",
        factory=StockBasicTask,
        uses_trade_date=False,
    ),
    "daily": TaskDefinition(
        name="daily",
        description="A股日线行情，未复权行情，停牌期间不提供数据",
        doc_url="https://tushare.pro/document/2?doc_id=27",
        factory=DailyTask,
    ),
}


def available_task_names() -> list[str]:
    return list(TASK_REGISTRY.keys())


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

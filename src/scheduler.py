from __future__ import annotations

import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.tasks.registry import available_task_definitions, build_task


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def run_registered_task(task_name: str) -> None:
    logger.info("Starting scheduled task: %s", task_name)
    result = build_task(task_name).run()
    target = f"trade_date={result.trade_date}" if result.trade_date else "scope=snapshot"
    logger.info(
        "Task finished, task=%s, %s, rows=%s, written=%s",
        result.task_name,
        target,
        result.row_count,
        result.written_count,
    )


def main() -> None:
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    for task_definition in available_task_definitions():
        trigger = (
            IntervalTrigger(
                days=task_definition.interval_days,
                start_date=task_definition.interval_start_date,
                timezone="Asia/Shanghai",
            )
            if task_definition.interval_days
            else CronTrigger(
                hour=task_definition.schedule_hour,
                minute=task_definition.schedule_minute,
            )
        )
        scheduler.add_job(
            run_registered_task,
            trigger,
            args=[task_definition.name],
            id=task_definition.schedule_id,
            replace_existing=True,
        )

    logger.info("Scheduler started. Jobs use registry schedule rules in Asia/Shanghai.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        time.sleep(0.1)


if __name__ == "__main__":
    main()

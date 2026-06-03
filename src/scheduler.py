from __future__ import annotations

import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.tasks.moneyflow_cnt_ths import MoneyflowCntThsTask


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def run_moneyflow_cnt_ths() -> None:
    logger.info("Starting scheduled task: moneyflow_cnt_ths")
    result = MoneyflowCntThsTask().run()
    logger.info(
        "Task finished, trade_date=%s, rows=%s, csv=%s",
        result.trade_date,
        result.row_count,
        result.output_file,
    )


def main() -> None:
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        run_moneyflow_cnt_ths,
        CronTrigger(hour=1, minute=0),
        id="moneyflow_cnt_ths_daily",
        replace_existing=True,
    )

    logger.info("Scheduler started. Job runs daily at 01:00 Asia/Shanghai.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        time.sleep(0.1)


if __name__ == "__main__":
    main()

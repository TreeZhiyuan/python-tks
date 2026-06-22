# Local Debug Scripts

本目录用于存放只在本地调试、补数或验证时使用的脚本。线上 GitHub Actions 定时任务仍以仓库现有 workflow 和 `src.main` 为准。

运行本目录脚本时，建议在仓库根目录执行命令，确保 `src` 包和 `.env` 能被正常加载。

## `run_daily_month.py`

按输入的自然日期范围逐日执行 `daily` 拉取任务，并写入本地 SQLite。

脚本实际执行的任务命令是：

```powershell
python -m src.main --tasks daily --dates YYYYMMDD --local-sqlite
```

### 参数

- `start_date`：开始日期，支持 `YYYYMMDD` 或 `YYYY-MM-DD`。
- `end_date`：结束日期，支持 `YYYYMMDD` 或 `YYYY-MM-DD`。
- `--interval-seconds`：相邻执行日期之间的等待秒数，默认 `180` 秒。

`start_date` 必须小于或等于 `end_date`。日期范围包含开始日期和结束日期。

脚本会按北京时间自然日判断周末。如果某一天是周六或周日，会直接跳过，不执行 Tushare 拉取。

### 用法示例

执行 2024 年 5 月 1 日到 2024 年 5 月 31 日之间的工作日：

```powershell
python -m src.localdebug.run_daily_month 20240501 20240531
```

也可以使用带短横线的日期格式：

```powershell
python -m src.localdebug.run_daily_month 2024-05-01 2024-05-31
```

本地快速验证参数和日期循环时，可以把等待时间设为 `0`：

```powershell
python -m src.localdebug.run_daily_month 20240501 20240503 --interval-seconds 0
```

查看脚本帮助：

```powershell
python -m src.localdebug.run_daily_month --help
```

### 前置条件

`daily` 会读取 `data/stock_basic/stock_basic.json` 中的股票池。如果该文件不存在，请先执行：

```powershell
python -m src.main --tasks stock_basic
```

本地 SQLite 默认路径来自 `src.db.sqlite.DEFAULT_SQLITE_DB_PATH`。如需初始化本地表结构，请先在对应 SQLite 数据库中执行 `DDL/007_create_daily_d1.sql`。

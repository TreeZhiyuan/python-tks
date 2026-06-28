# Local Debug Scripts

本目录用于存放只在本地调试、补数或验证时使用的脚本。线上 GitHub Actions 定时任务仍以仓库现有 workflow 和 `src.main` 为准。

建议在仓库根目录执行本目录脚本，确保 `src` 包、`.env` 和相对路径能被正常加载。

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

## `sync_daily_d1_to_sqlite.py`

从 Cloudflare D1 的 `daily` 表读取指定日期的数据，并同步写入本地 SQLite 的 `daily` 表。

该脚本不会请求 Tushare，只负责把已经存在于 D1 的 `daily` 数据回填到本地 SQLite。写入使用 `INSERT OR REPLACE`，因此同一 `trade_date + ts_code` 重复同步会覆盖本地旧记录。

### 参数

- `start_date`：需要同步的单个日期，或日期范围开始日期，支持 `YYYYMMDD` 或 `YYYY-MM-DD`。
- `end_date`：可选，日期范围结束日期，支持 `YYYYMMDD` 或 `YYYY-MM-DD`。不传时只同步 `start_date` 当天。
- `--sqlite-db-path`：本地 SQLite 文件路径，默认来自 `.env` 的 `LOCAL_SQLITE_DB_PATH` 配置。
- `--batch-size`：每批写入 SQLite 的行数，默认 `100`。
- `--continue-on-error`：某一天同步失败后继续后续日期。
- `--debug-traceback`：发生错误时打印 Python traceback，便于定位本地环境、D1 配置或 SQL 问题。

`start_date` 必须小于或等于 `end_date`。日期范围包含开始日期和结束日期。

脚本执行时会打印以下调试信息：

- 本地 SQLite 文件路径。
- 每个日期的 D1 查询行数。
- 每个日期写入 SQLite 的行数。
- 写入后本地 SQLite 中该日期的记录数。
- 最终汇总的日期数、空数据日期数、失败日期数、读取总行数和写入总行数。

### 用法示例

同步单个日期：

```powershell
python -m src.localdebug.sync_daily_d1_to_sqlite 20240506
```

同步日期范围：

```powershell
python -m src.localdebug.sync_daily_d1_to_sqlite 20240501 20240531
```

使用带短横线的日期格式：

```powershell
python -m src.localdebug.sync_daily_d1_to_sqlite 2024-05-01 2024-05-31
```

指定本地 SQLite 路径：

```powershell
python -m src.localdebug.sync_daily_d1_to_sqlite 20240506 --sqlite-db-path D:\devtools\sqlite\dbs\tushare.db
```

某一天失败后继续同步后续日期，并打印详细 traceback：

```powershell
python -m src.localdebug.sync_daily_d1_to_sqlite 20240501 20240531 --continue-on-error --debug-traceback
```

查看脚本帮助：

```powershell
python -m src.localdebug.sync_daily_d1_to_sqlite --help
```

## 前置条件

本地运行这些脚本前，请确认已经安装依赖：

```powershell
pip install -r requirements.txt
```

需要访问 Cloudflare D1 的脚本还要求 `.env` 中已经配置：

```env
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_D1_DATABASE_ID=...
```

本地 SQLite 表结构会由 `src.db.sqlite.SQLiteClient` 按 `DDL/*_d1.sql` 自动初始化。默认 SQLite 文件路径由 `.env` 中的 `LOCAL_SQLITE_DB_PATH` 配置：

```env
LOCAL_SQLITE_DB_PATH=D:/devtools/sqlite/dbs/tushare.db
```

如果未配置 `LOCAL_SQLITE_DB_PATH`，程序会使用 `D:/devtools/sqlite/dbs/tushare.db`。脚本参数 `--sqlite-db-path` 可临时覆盖该配置。

`run_daily_month.py` 会读取 `data/stock_basic/stock_basic.json` 中的股票池。如果该文件不存在，请先执行：

```powershell
python -m src.main --tasks stock_basic
```

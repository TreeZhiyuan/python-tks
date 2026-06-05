# Python Scheduled Tasks

这个项目用于拉取 Tushare 数据。日频资金流数据写入 Cloudflare D1，股票基础信息保存为仓库内 JSON 快照。

## 已接入 Tushare 接口

后续每新增一个 Tushare 接口，都需要在本清单中补充接口名称、功能描述、接口文档链接、定时执行时间和执行说明。

| 任务名 | Tushare 接口 | 功能描述 | 文档 | 定时执行时间 | 执行说明 |
| --- | --- | --- | --- | --- | --- |
| `stock_basic` | `stock_basic` | 股票基础信息，包括股票代码、名称、上市日期、退市日期等 | [doc_id=25](https://tushare.pro/document/2?doc_id=25) | 每 7 天执行一次，从 `2026-06-05 00:30` 开始 | 快照类接口，不按交易日；每次执行拉取当前股票基础信息并保存到 `data/stock_basic/stock_basic.json` |
| `moneyflow_cnt_ths` | `moneyflow_cnt_ths` | 同花顺概念板块每日资金流向 | [doc_id=371](https://tushare.pro/document/2?doc_id=371) | 每天 `01:00` | 日频接口；每次执行拉取昨天的资金流向数据 |
| `moneyflow_ind_dc` | `moneyflow_ind_dc` | 东财概念及行业板块每日资金流向 | [doc_id=344](https://tushare.pro/document/2?doc_id=344) | 每天 `01:05` | 日频接口；每次执行拉取昨天的资金流向数据 |
| `moneyflow` | `moneyflow` | 沪深A股个股每日资金流向 | [doc_id=170](https://tushare.pro/document/2?doc_id=170) | 每天 `01:10` | 日频接口；每次执行拉取昨天的个股资金流向数据 |
| `moneyflow_dc` | `moneyflow_dc` | 东方财富个股每日资金流向 | [doc_id=349](https://tushare.pro/document/2?doc_id=349) | 每天 `01:15` | 日频接口；每次执行拉取昨天的个股资金流向数据 |
| `moneyflow_ths` | `moneyflow_ths` | 同花顺个股每日资金流向 | [doc_id=348](https://tushare.pro/document/2?doc_id=348) | 每天 `01:20` | 日频接口；每次执行拉取昨天的个股资金流向数据 |

## 环境要求

- Python 3.10
- 推荐使用本地 Conda 环境：
  - `C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10`

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

复制环境变量模板：

```bash
copy .env.example .env
```

`.env` 示例：

```env
TUSHARE_TOKEN=REPLACE_WITH_YOUR_TUSHARE_TOKEN
CLOUDFLARE_API_TOKEN=REPLACE_WITH_YOUR_CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID=REPLACE_WITH_YOUR_CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_D1_DATABASE_ID=REPLACE_WITH_YOUR_D1_DATABASE_ID
```

## 数据库准备

日频资金流任务写入前，请先在 Cloudflare D1 中执行对应的 DDL 脚本。

已提供脚本：

- `DDL/001_create_moneyflow_cnt_ths.sql`
- `DDL/001_create_moneyflow_cnt_ths_d1.sql`
- `DDL/002_create_moneyflow_ind_dc.sql`
- `DDL/002_create_moneyflow_ind_dc_d1.sql`
- `DDL/004_create_moneyflow.sql`
- `DDL/004_create_moneyflow_d1.sql`
- `DDL/005_create_moneyflow_dc.sql`
- `DDL/005_create_moneyflow_dc_d1.sql`
- `DDL/006_create_moneyflow_ths.sql`
- `DDL/006_create_moneyflow_ths_d1.sql`

当前程序写入的目标表：

- `moneyflow_cnt_ths`
- `moneyflow_ind_dc`
- `moneyflow`
- `moneyflow_dc`
- `moneyflow_ths`

`stock_basic` 不写入 Cloudflare D1，也不需要建表脚本。它会保存为仓库内 JSON 文件：

- `data/stock_basic/stock_basic.json`

## 单次执行

默认执行 `moneyflow_cnt_ths`，抓取昨天的数据并写入 D1：

```bash
python -m src.main
```

选择一个任务执行：

```bash
python -m src.main --tasks moneyflow_ind_dc
```

选择多个任务执行：

```bash
python -m src.main --tasks moneyflow_cnt_ths moneyflow_ind_dc
```

执行全部已接入任务：

```bash
python -m src.main --tasks all
```

`stock_basic` 是快照类接口，不按交易日拉取。即使命令中传入 `--dates`，该任务也只会执行一次当前基础信息快照，并保存到 `data/stock_basic/stock_basic.json`。

指定多个日期：

```bash
python -m src.main --tasks moneyflow_cnt_ths moneyflow_ind_dc --dates 20240506 20240507
```

指定日期区间：

```bash
python -m src.main --tasks all --start-date 20240501 --end-date 20240531
```

如果使用批处理脚本：

```bash
run_once.bat
run_once.bat --tasks moneyflow_ind_dc
run_once.bat --tasks moneyflow_cnt_ths moneyflow_ind_dc --dates 20240506 20240507
run_once.bat --tasks all --start-date 20240501 --end-date 20240531
```

兼容旧参数：

```bash
python -m src.main --task moneyflow_ind_dc
```

执行成功后，命令行会输出每个任务和交易日的：

- `task`
- `trade_date`
- `rows`
- `written`

## 读取数据

按交易日读取 THS 数据：

```bash
python -m src.read_moneyflow_cnt_ths --trade-date 20240506
```

按交易日读取 DC 数据：

```bash
python -m src.read_moneyflow_ind_dc --trade-date 20240506
```

股票基础信息读取来源是 JSON 快照文件：`data/stock_basic/stock_basic.json`。

读取个股资金流向数据：

```bash
python -m src.read_moneyflow --trade-date 20240506
python -m src.read_moneyflow_dc --trade-date 20240506
python -m src.read_moneyflow_ths --trade-date 20240506
```

## 定时任务

项目使用 `APScheduler`。

当前调度规则也可在“已接入 Tushare 接口”表中查看：

- `moneyflow_cnt_ths`：每天 `01:00`
- `moneyflow_ind_dc`：每天 `01:05`
- `stock_basic`：每 7 天执行一次，从 `2026-06-05 00:30` 开始
- `moneyflow`：每天 `01:10`
- `moneyflow_dc`：每天 `01:15`
- `moneyflow_ths`：每天 `01:20`

调度任务来源于 `src/tasks/registry.py`。新增接口时，在 registry 中配置 `schedule_hour` 和 `schedule_minute` 后，调度器会自动注册对应任务。

启动调度器：

```bash
python -m src.scheduler
```

或使用：

```bash
run_scheduler.bat
```

只有在你主动启动调度器后，才会开始按计划执行。

## 项目结构

```text
src/
  core/                通用结果模型
  db/                  Cloudflare D1 访问封装
  repositories/        数据表仓储层
  tasks/               Tushare 任务实现和任务注册表
  main.py              单次执行入口
  scheduler.py         定时调度入口
  read_moneyflow_cnt_ths.py
  read_moneyflow_ind_dc.py
  read_moneyflow.py
  read_moneyflow_dc.py
  read_moneyflow_ths.py
  storage/             JSON 快照存储封装
```

## 设计说明

为了后续继续扩展更多 Tushare 接口，当前代码做了三层抽象：

- `Template Method`：统一“分页抓取 Tushare -> 汇总 -> 写入 D1”的任务流程
- `JSON Snapshot Task`：支持不依赖交易日、适合保存为仓库 JSON 快照的基础信息接口
- `Repository`：统一数据库写入和查询操作
- `Task Registry`：统一管理已接入任务、接口描述、文档链接和调度时间，供单次执行、定时调度和文档维护复用

新增接口时，通常需要补：

- 一个任务类
- 一个仓储类，或一个 JSON 快照存储任务
- MySQL 版和 Cloudflare D1 版建表脚本；如果该接口明确保存为仓库 JSON 快照，则不需要数据库 DDL
- 在 `src/tasks/registry.py` 注册任务元数据
- 在 README 的“已接入 Tushare 接口”清单补充接口信息、定时执行时间和执行说明

## 新增 Tushare 接口接入步骤

1. 阅读接口文档，确认接口名称、输出字段、主键字段、是否支持 `trade_date + limit + offset` 分页。
2. 对写入 Cloudflare D1 的接口，在 `DDL/` 下新增 MySQL 版和 Cloudflare D1 版建表脚本，表名建议与 Tushare 接口名保持一致。
3. 对写入 Cloudflare D1 的接口，在 `src/repositories/` 下新增仓储类，继承 `BaseD1Repository`，配置 `table_name`、`select_columns`、`source_to_db_field_map`。
4. 对保存为 JSON 快照的接口，使用 `src/storage/json_store.py` 写入仓库内 JSON 文件，并在 `.gitignore` 中确保该 JSON 文件可提交。
5. 在 `src/tasks/` 下新增任务类。日频分页接口继承 `BaseMoneyflowTask` 并实现 `fetch_page()`；JSON 快照接口自行实现 `run()` 并返回 `TaskRunResult`。
6. 在 `src/tasks/registry.py` 注册任务名、描述、文档链接、factory 和调度规则。
7. 如需要独立读取入口，在 `src/read_<task_name>.py` 下新增读取脚本。
8. 更新 README 的接口清单、定时执行时间、执行说明和数据库脚本清单。
9. 运行 `python -m compileall src`，再用 `python -m src.main --tasks <task_name> --dates YYYYMMDD` 做单接口验证。

建表脚本要求：

- MySQL 版使用表注释和字段注释。
- D1 版使用 SQLite 兼容语法，并用 SQL 注释保留表和字段说明。
- 字段需要覆盖 Tushare 文档的输出参数。
- 主键需要能避免同一业务数据重复写入。
- 索引需要覆盖常用查询字段，例如 `trade_date`、`ts_code`、`name` 或业务分类字段。

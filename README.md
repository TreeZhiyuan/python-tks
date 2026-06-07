# Python Scheduled Tasks

这个项目用于拉取 Tushare 数据。日频资金流数据写入 Cloudflare D1，股票基础信息保存为仓库内 JSON 快照。

## 已接入 Tushare 接口

后续每新增一个 Tushare 接口，都需要在本清单中补充接口名称、功能描述、接口文档链接、定时执行时间和执行说明。

| 任务名 | Tushare 接口 | 功能描述 | 文档 | 定时执行时间 | 执行说明 |
| --- | --- | --- | --- | --- | --- |
| `stock_basic` | `stock_basic` | 股票基础信息，包括股票代码、名称、上市日期、退市日期等 | [doc_id=25](https://tushare.pro/document/2?doc_id=25) | 每周日 `01:00` | 快照类接口，不按交易日；默认只保留 `list_status=L` 且 `market` 为主板/创业板的上市股票，并保存到 `data/stock_basic/stock_basic.json`；GitHub Actions 定时执行后会提交快照变更 |
| `moneyflow_cnt_ths` | `moneyflow_cnt_ths` | 同花顺概念板块每日资金流向 | [doc_id=371](https://tushare.pro/document/2?doc_id=371) | 每个工作日 `01:00` | 日频接口；GitHub Actions 按北京时间计算最近一个工作日并写入 D1 |
| `moneyflow_ind_dc` | `moneyflow_ind_dc` | 东财概念及行业板块每日资金流向 | [doc_id=344](https://tushare.pro/document/2?doc_id=344) | 每个工作日 `01:00` | 日频接口；GitHub Actions 按北京时间计算最近一个工作日并写入 D1 |
| `moneyflow` | `moneyflow` | 沪深A股个股每日资金流向 | [doc_id=170](https://tushare.pro/document/2?doc_id=170) | 每个工作日 `01:00` | 日频接口；GitHub Actions 按北京时间计算最近一个工作日并写入 D1 |
| `moneyflow_dc` | `moneyflow_dc` | 东方财富个股每日资金流向 | [doc_id=349](https://tushare.pro/document/2?doc_id=349) | 每个工作日 `01:00` | 日频接口；GitHub Actions 按北京时间计算最近一个工作日并写入 D1 |
| `moneyflow_ths` | `moneyflow_ths` | 同花顺个股每日资金流向 | [doc_id=348](https://tushare.pro/document/2?doc_id=348) | 每个工作日 `01:00` | 日频接口；GitHub Actions 按北京时间计算最近一个工作日并写入 D1 |
| `daily` | `daily` | A股日线行情，未复权行情，停牌期间不提供数据 | [doc_id=27](https://tushare.pro/document/2?doc_id=27) | 每个工作日 `20:00` | 日频接口；GitHub Actions 按北京时间当天日期执行；任务先读取 `stock_basic` 快照中的 `ts_code` 股票池，再按多股票代码批量拉取 `daily` 并分批写入 D1 |

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
- `DDL/007_create_daily.sql`
- `DDL/007_create_daily_d1.sql`

当前程序写入的目标表：

- `moneyflow_cnt_ths`
- `moneyflow_ind_dc`
- `moneyflow`
- `moneyflow_dc`
- `moneyflow_ths`
- `daily`

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

`stock_basic` 是快照类接口，不按交易日拉取。即使命令中传入 `--dates`，该任务也只会执行一次当前基础信息快照。默认请求入参为 `list_status=L`，并只保存 `market` 为主板/创业板的上市股票到 `data/stock_basic/stock_basic.json`。

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

股票基础信息读取来源是 JSON 快照文件：`data/stock_basic/stock_basic.json`。该文件的 `request_params` 会记录本次请求入参。

读取个股资金流向数据：

```bash
python -m src.read_moneyflow --trade-date 20240506
python -m src.read_moneyflow_dc --trade-date 20240506
python -m src.read_moneyflow_ths --trade-date 20240506
```

读取 A股日线行情数据：

```bash
python -m src.read_daily --trade-date 20240506
```

`daily` 写入逻辑会先读取 `data/stock_basic/stock_basic.json` 中的 `ts_code` 列表作为股票池，再按批次把多个股票代码用英文逗号拼接后请求 Tushare `daily`。如果该快照不存在，请先执行：

```bash
python -m src.main --tasks stock_basic
```

## GitHub Actions 定时任务

项目使用 GitHub Actions 负责线上定时执行，workflow 文件是 `.github/workflows/tushare-tasks.yml`。GitHub Actions 的 cron 使用 UTC，当前北京时间调度规则如下：

| 任务范围 | 北京时间 | GitHub Actions cron | 执行命令 |
| --- | --- | --- | --- |
| `stock_basic` | 每周日 `01:00` | `0 17 * * 6` | `python -m src.main --tasks stock_basic` |
| 资金流任务组 | 每个工作日 `01:00` | `0 17 * * 0-4` | `python -m src.main --tasks moneyflow_cnt_ths moneyflow_ind_dc moneyflow moneyflow_dc moneyflow_ths --dates <最近一个工作日>` |
| `daily` | 每个工作日 `20:00` | `0 12 * * 1-5` | `python -m src.main --tasks daily --dates <北京时间当天>` |

资金流任务组包含：

- `moneyflow_cnt_ths`
- `moneyflow_ind_dc`
- `moneyflow`
- `moneyflow_dc`
- `moneyflow_ths`

GitHub Actions 需要在仓库 `Settings` -> `Secrets and variables` -> `Actions` 中配置：

- `TUSHARE_TOKEN`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_D1_DATABASE_ID`

workflow 同时支持手动触发 `workflow_dispatch`。手动执行时可以填写 `tasks`，例如 `stock_basic`、`daily`、`moneyflow_cnt_ths moneyflow_ind_dc` 或 `all`；也可以填写 `dates` 指定一个或多个 `YYYYMMDD` 日期。

本地不再维护长驻定时调度器。如需本地调试，请继续使用“单次执行”中的 `run_once.bat`。

## 项目结构

```text
src/
  core/                通用结果模型
  db/                  Cloudflare D1 访问封装
  repositories/        数据表仓储层
  tasks/               Tushare 任务实现和任务注册表
  main.py              单次执行入口
  read_moneyflow_cnt_ths.py
  read_moneyflow_ind_dc.py
  read_moneyflow.py
  read_moneyflow_dc.py
  read_moneyflow_ths.py
  read_daily.py
  storage/             JSON 快照存储封装
```

## 设计说明

为了后续继续扩展更多 Tushare 接口，当前代码做了三层抽象：

- `Template Method`：统一“分页抓取 Tushare -> 汇总 -> 写入 D1”的任务流程
- `JSON Snapshot Task`：支持不依赖交易日、适合保存为仓库 JSON 快照的基础信息接口
- `Repository`：统一数据库写入和查询操作
- `Code Batch Task`：支持先读取股票池，再按多个 `ts_code + trade_date` 批量拉取数据的接口，例如 `daily`
- `Task Registry`：统一管理已接入任务、接口描述和文档链接，供单次执行、GitHub Actions 和文档维护复用

新增接口时，通常需要补：

- 一个任务类
- 一个仓储类，或一个 JSON 快照存储任务
- MySQL 版和 Cloudflare D1 版建表脚本；如果该接口明确保存为仓库 JSON 快照，则不需要数据库 DDL
- 在 `src/tasks/registry.py` 注册任务元数据
- 在 README 的“已接入 Tushare 接口”清单补充接口信息、定时执行时间和执行说明
- 如需定时执行，在 `.github/workflows/tushare-tasks.yml` 中补充对应 GitHub Actions 调度规则

## 新增 Tushare 接口接入步骤

1. 阅读接口文档，确认接口名称、输出字段、主键字段、是否支持 `trade_date + limit + offset` 分页。
2. 对写入 Cloudflare D1 的接口，在 `DDL/` 下新增 MySQL 版和 Cloudflare D1 版建表脚本，表名建议与 Tushare 接口名保持一致。
3. 对写入 Cloudflare D1 的接口，在 `src/repositories/` 下新增仓储类，继承 `BaseD1Repository`，配置 `table_name`、`select_columns`、`source_to_db_field_map`。
4. 对保存为 JSON 快照的接口，使用 `src/storage/json_store.py` 写入仓库内 JSON 文件，并在 `.gitignore` 中确保该 JSON 文件可提交。
5. 在 `src/tasks/` 下新增任务类。日频分页接口继承 `BaseMoneyflowTask` 并实现 `fetch_page()`；JSON 快照接口自行实现 `run()` 并返回 `TaskRunResult`。
6. 在 `src/tasks/registry.py` 注册任务名、描述、文档链接、factory 和 `uses_trade_date`。
7. 如需要独立读取入口，在 `src/read_<task_name>.py` 下新增读取脚本。
8. 更新 README 的接口清单、定时执行时间、执行说明和数据库脚本清单；如需定时执行，同步更新 `.github/workflows/tushare-tasks.yml`。
9. 运行 `python -m compileall src`，再用 `python -m src.main --tasks <task_name> --dates YYYYMMDD` 做单接口验证。

建表脚本要求：

- MySQL 版使用表注释和字段注释。
- D1 版使用 SQLite 兼容语法，并用 SQL 注释保留表和字段说明。
- 字段需要覆盖 Tushare 文档的输出参数。
- 主键需要能避免同一业务数据重复写入。
- 索引需要覆盖常用查询字段，例如 `trade_date`、`ts_code`、`name` 或业务分类字段。

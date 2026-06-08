# Agent Notes

本项目是 Tushare 数据拉取任务集合。日频资金流数据写入 Cloudflare D1，股票基础信息保存为仓库内 JSON 快照。

## 当前已接入接口

| 任务名 | Tushare 接口 | 功能描述 | 文档 |
| --- | --- | --- | --- |
| `moneyflow_cnt_ths` | `moneyflow_cnt_ths` | 同花顺概念板块每日资金流向 | https://tushare.pro/document/2?doc_id=371 |
| `moneyflow_ind_dc` | `moneyflow_ind_dc` | 东财概念及行业板块每日资金流向 | https://tushare.pro/document/2?doc_id=344 |
| `stock_basic` | `stock_basic` | 股票基础信息，默认只保留 `list_status=L` 且 `market` 为主板/创业板的上市股票 | https://tushare.pro/document/2?doc_id=25 |
| `moneyflow` | `moneyflow` | 沪深A股个股每日资金流向 | https://tushare.pro/document/2?doc_id=170 |
| `moneyflow_dc` | `moneyflow_dc` | 东方财富个股每日资金流向 | https://tushare.pro/document/2?doc_id=349 |
| `moneyflow_ths` | `moneyflow_ths` | 同花顺个股每日资金流向 | https://tushare.pro/document/2?doc_id=348 |
| `daily` | `daily` | A股日线行情，未复权行情，停牌期间不提供数据 | https://tushare.pro/document/2?doc_id=27 |

## 架构约定

- Tushare 客户端创建逻辑在 `src/tushare_client.py`。
- 日频资金流分页任务基类在 `src/tasks/base.py`。
- D1 数据库访问封装在 `src/db/d1.py`。
- 数据表写入和读取复用逻辑在 `src/repositories/base.py`。
- 已接入任务统一注册在 `src/tasks/registry.py`。
- 单次执行入口是 `src/main.py`，支持 `--tasks` 多选和 `all`。
- 选股策略执行入口是 `src/strategy_runner.py`，支持 `--strategies` 多选和 `--mode intersection|union`。
- 选股策略统一注册在 `src/strategies/registry.py`。
- 线上定时任务由 GitHub Actions 执行，workflow 文件是 `.github/workflows/tushare-tasks.yml`。
- 本地调试只保留单次执行脚本 `run_once.bat`。

## 当前已接入选股策略

| 策略名 | 功能描述 | 数据来源 |
| --- | --- | --- |
| `stock_pool` | 当前股票基础信息快照中的全部股票 | `data/stock_basic/stock_basic.json` |
| `has_industry` | 股票基础信息中已包含行业分类 | `data/stock_basic/stock_basic.json` |
| `hs_connect` | 沪深股通标的股票 | `data/stock_basic/stock_basic.json` |

## 当前 GitHub Actions 调度规则

| 任务范围 | 北京时间 | GitHub Actions cron | 执行说明 |
| --- | --- | --- | --- |
| `stock_basic` | 每周日 `01:00` | `0 17 * * 6` | 更新 `data/stock_basic/stock_basic.json`，并提交快照变更 |
| `moneyflow_cnt_ths`、`moneyflow_ind_dc`、`moneyflow`、`moneyflow_dc`、`moneyflow_ths` | 每个工作日 `01:00` | `0 17 * * 0-4` | 按北京时间计算最近一个工作日，写入 Cloudflare D1 |
| `daily` | 每个工作日 `20:00` | `0 12 * * 1-5` | 按北京时间当天日期写入 Cloudflare D1，并清理超过 1 年的 `daily` 历史数据 |

资金流任务组支持 GitHub Actions Repository Variables 单独开关：

- `ENABLE_MONEYFLOW_CNT_THS` 控制 `moneyflow_cnt_ths`
- `ENABLE_MONEYFLOW_IND_DC` 控制 `moneyflow_ind_dc`
- `ENABLE_MONEYFLOW` 控制 `moneyflow`
- `ENABLE_MONEYFLOW_DC` 控制 `moneyflow_dc`
- `ENABLE_MONEYFLOW_THS` 控制 `moneyflow_ths`

变量值不区分大小写。配置为 `true`、`1`、`yes`、`on` 或 `enabled` 时执行；未配置、空值、`false`、`0`、`no`、`off` 或 `disabled` 时跳过对应任务。如果 5 个资金流任务全部未开启，GitHub Actions 会跳过本次资金流定时执行并正常结束。

`daily` 的实现不是全市场 `trade_date + limit + offset` 分页；它会先读取 `data/stock_basic/stock_basic.json` 中的 `ts_code` 股票池，再按多个 `ts_code + trade_date` 批量请求 Tushare `daily`，最后分批写入 Cloudflare D1。

`daily` 写入完成后会删除 `trade_date < <北京时间当天往前一年>` 的记录。该清理逻辑与 `daily` 定时规则一致，不受资金流任务组 GitHub Actions 开关控制。

## 新增 Tushare 接口最小变更

新增一个同类 `trade_date + limit + offset` 分页接口时，通常只需要改这些位置：

- 新增 `DDL/<序号>_create_<task_name>.sql`
- 新增 `DDL/<序号>_create_<task_name>_d1.sql`
- 新增 `src/repositories/<task_name>_repository.py`
- 新增 `src/tasks/<task_name>.py`
- 更新 `src/tasks/registry.py`
- 更新 `README.md` 的接口清单和 DDL 清单
- 如需定时执行，更新 `.github/workflows/tushare-tasks.yml`
- 可选新增 `src/read_<task_name>.py`

数据库建表脚本是每次新增 Tushare 接口的必选改动，不是可选项。即使代码暂时只写入 Cloudflare D1，也要同时提供 MySQL 版和 D1 版 DDL，便于字段审查、迁移和后续数据库适配。

## 数据库建表脚本要求

每次新增接口都必须包含：

- MySQL DDL：`DDL/<序号>_create_<task_name>.sql`
- Cloudflare D1 DDL：`DDL/<序号>_create_<task_name>_d1.sql`
- 表名：优先使用 Tushare 接口名，保持与任务名一致
- 字段：覆盖 Tushare 文档的输出参数
- 主键：根据接口语义选择稳定唯一键，日频数据通常包含 `trade_date`
- 注释：MySQL 版使用表注释和字段注释，D1 版使用 SQL 注释保留说明
- 索引：至少覆盖常用查询字段，例如 `trade_date`、`ts_code`、`name` 或业务分类字段
- README：同步把新增 DDL 文件加入“数据库准备”清单

## 接入检查清单

- README 已列出接口名称、功能描述和 Tushare 文档链接。
- 新增接口已包含 MySQL 版和 Cloudflare D1 版建表脚本。
- DDL 字段与 Tushare 输出参数一致。
- DDL 已包含合理主键、常用查询索引、表说明和字段说明。
- D1 版 DDL 使用 SQLite 语法，不使用 MySQL 的 `ENGINE`、`CHARSET`、`COMMENT`。
- Repository 的 `source_to_db_field_map` 覆盖全部需要写入的字段。
- Task 的 `fetch_page()` 使用正确的 Tushare 接口名和参数。
- `src/tasks/registry.py` 已注册任务元数据。
- 如需定时执行，`.github/workflows/tushare-tasks.yml` 已注册对应 GitHub Actions cron。
- `python -m compileall src` 通过。
- 单次验证命令可运行：`python -m src.main --tasks <task_name> --dates YYYYMMDD`。

## 注意事项

- 当前任务基类主要适合支持 `trade_date`、`limit`、`offset` 的日频分页接口。
- `daily` 是按股票代码批量请求的例外，不继承 `BaseMoneyflowTask`。
- 如果后续接口是不依赖交易日且短期变化不大的快照类接口，可保存为仓库 JSON 文件，例如 `stock_basic` 写入 `data/stock_basic/stock_basic.json`。
- 如果后续接口既不是日频分页，也不是快照模式，先扩展或新增任务基类，不要硬塞到 `BaseMoneyflowTask`。
- 当前数据库写入目标是 Cloudflare D1；SQLite/MySQL 需要额外数据库适配层。
- GitHub Actions runner 默认使用 UTC；涉及默认日期时必须显式按 `Asia/Shanghai` 计算。
- 新增选股策略时，优先复用已同步数据和 `StrategyContext`，不要在策略里直接调用 Tushare。
- 选股策略结果当前保存到 `data/strategy_results/`，结果文件默认不提交仓库，仅提交 `.gitkeep`。

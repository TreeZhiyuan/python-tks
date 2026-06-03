# Python Scheduled Tasks

这个项目用于运行一系列定时任务。

当前已包含任务：

- `moneyflow_cnt_ths`：获取同花顺概念板块每日资金流向数据，并写入 Cloudflare D1 数据库。

## 环境

- Python 3.10
- 推荐使用你本地已有的 Conda 环境：
  - `C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10`

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制环境变量模板并填写：

```bash
copy .env.example .env
```

`.env` 示例：

```env
TUSHARE_TOKEN=REPLACE_WITH_YOUR_TUSHARE_TOKEN
OUTPUT_DIR=data
CLOUDFLARE_API_TOKEN=REPLACE_WITH_YOUR_CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID=REPLACE_WITH_YOUR_CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_D1_DATABASE_ID=REPLACE_WITH_YOUR_D1_DATABASE_ID
```

## 单次执行任务

默认执行“昨天”的同花顺概念板块资金流向抓取，并写入 D1：

```bash
python -m src.main
```

也可以指定多个日期补数：

```bash
python -m src.main --dates 20240506 20240507 20240508
```

或者按起止日期批量补数：

```bash
python -m src.main --start-date 20240501 --end-date 20240531
```

如果你使用项目根目录下的批处理脚本，也支持透传参数：

```bash
run_once.bat --dates 20240506 20240507 20240508
run_once.bat --start-date 20240501 --end-date 20240531
```

## 读取数据库

按交易日读取已写入的 D1 数据：

```bash
python -m src.read_moneyflow_cnt_ths --trade-date 20240506
```

## 定时执行

项目内使用 `APScheduler` 配置定时任务：

- 每天 `01:00`
- 自动抓取“昨天”的数据

启动调度器：

```bash
python -m src.scheduler
```

或使用：

```bash
run_scheduler.bat
```

只有在你主动启动调度器后，才会开始每天 `01:00` 自动抓取昨天数据。你可以先通过单次执行把预期日期的数据补齐，再启动定时任务。

## 数据库表

请先在 Cloudflare D1 中执行建表脚本：

- MySQL 版：`DDL/001_create_moneyflow_cnt_ths.sql`
- D1 版：`DDL/001_create_moneyflow_cnt_ths_d1.sql`

当前程序写入的目标表为：

- `moneyflow_cnt_ths`

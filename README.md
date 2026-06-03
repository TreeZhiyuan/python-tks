# Python Scheduled Tasks

这个项目用于运行一系列定时任务。

当前已包含任务：

- `moneyflow_cnt_ths`：获取同花顺概念板块每日资金流向数据，并保存为 CSV 文件。

## 环境

- Python 3.10
- 推荐使用你本地已有的 Conda 环境：
  - `C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10`

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制环境变量模板并填写 `TUSHARE_TOKEN`：

```bash
copy .env.example .env
```

`.env` 示例：

```env
TUSHARE_TOKEN=REPLACE_WITH_YOUR_TUSHARE_TOKEN
OUTPUT_DIR=data
```

## 单次执行任务

默认执行“昨天”的同花顺概念板块资金流向抓取：

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

程序会为每个日期分别生成一个 CSV 文件。

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

如果希望在 Windows 下常驻运行，可以配合任务计划程序、nssm 或服务方式启动。

## 输出

CSV 文件默认输出到：

- `data/moneyflow_cnt_ths/`

文件名格式：

- `moneyflow_cnt_ths_YYYYMMDD.csv`

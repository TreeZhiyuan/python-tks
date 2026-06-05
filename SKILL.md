# Tushare D1 Interface Onboarding Skill

Use this skill when adding a new Tushare interface to this project and writing the pulled data into Cloudflare D1.

## Goal

Add a new Tushare task with the smallest maintainable change set:

- Required database table DDL for MySQL and Cloudflare D1
- Repository mapping
- Tushare task implementation
- Task registry entry
- README interface documentation
- Optional read script

## Workflow

1. Open the Tushare interface document and identify:
   - Interface name
   - Description
   - Input parameters
   - Output fields
   - Per-request limit
   - Whether `trade_date + limit + offset` pagination is supported

2. Add DDL scripts in `DDL/`:
   - `<number>_create_<task_name>.sql` for MySQL
   - `<number>_create_<task_name>_d1.sql` for Cloudflare D1
   - This step is required for every new Tushare interface.
   - Use the Tushare interface name as the table name unless there is a strong reason not to.
   - Include every output field that will be persisted.
   - Define a stable primary key based on the interface semantics.
   - Add indexes for common query fields such as `trade_date`, `ts_code`, `name`, or category fields.
   - Add table comments and field comments in MySQL.
   - Preserve comments as SQL comments in D1.
   - Use SQLite-compatible syntax in D1; do not use MySQL `ENGINE`, `CHARSET`, or `COMMENT`.

3. Add a repository in `src/repositories/`:
   - Inherit `BaseD1Repository`.
   - Set `table_name`.
   - Set `select_columns`.
   - Set `source_to_db_field_map`.
   - Map Tushare source field names to database column names.

4. Add a task in `src/tasks/`:
   - Inherit `BaseMoneyflowTask` for `trade_date + limit + offset` interfaces.
   - Implement `fetch_page(pro, trade_date, offset, limit)`.
   - Call the exact Tushare SDK method documented by Tushare.

5. Register the task in `src/tasks/registry.py`:
   - `name`
   - `description`
   - `doc_url`
   - `factory`
   - `schedule_hour`
   - `schedule_minute`

6. Update `README.md`:
   - Add the interface to “已接入 Tushare 接口”.
   - Add the new DDL scripts to “数据库准备”.
   - Confirm the README table list includes the new target database table.
   - Add run examples only if the interface requires special parameters.

7. Optional: add `src/read_<task_name>.py` if users need a dedicated read command.

8. Verify:
   - Review both DDL files against the Tushare output parameter table.
   - `python -m compileall src`
   - `python -m src.main --help`
   - `python -m src.main --tasks <task_name> --dates YYYYMMDD`

## Design Pattern Notes

- Use Template Method through `BaseMoneyflowTask` for shared Tushare pagination flow.
- Use JSON snapshot storage for Tushare interfaces that return current snapshot data, do not depend on `trade_date`, and do not need Cloudflare D1 persistence.
- Use Repository through `BaseD1Repository` for shared D1 write/read behavior.
- Use Task Registry in `src/tasks/registry.py` as the single source of truth for task discovery and scheduling.

## When Not To Use `BaseMoneyflowTask`

Do not force a new interface into `BaseMoneyflowTask` if it does not support the current daily pagination shape:

- No `trade_date`
- No `limit` / `offset`
- Requires symbol/code loops
- Requires date range input instead of one trading day

For those interfaces, create a new base task class and still reuse the repository and registry patterns.

Use `src/storage/json_store.py` when the interface returns a full current-state list and should be committed as a repository JSON snapshot, such as `stock_basic`.

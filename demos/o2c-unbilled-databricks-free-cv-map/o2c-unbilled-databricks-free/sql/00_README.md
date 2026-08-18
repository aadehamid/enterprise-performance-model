# `00_lakebase_ods.sql` — Act 0 ODS write, not the Metric View

This file is the **Lakebase ODS load**. It is not the compiler and not
the Metric View.

Run it in **Lakebase Postgres** against project **dataexpert-day1**.
It creates schema `o2c_unbilled` only, then `CREATE TABLE IF NOT EXISTS`
+ idempotent `DELETE` / `INSERT` for the seven seeds in `data/`.
Expected counts: **8 / 10 / 3 / 3 / 19 / 6 / 6**.

The Lakebase replica lands into **`workspace.o2c_unbilled`**. Warehouse
facts and `CREATE VIEW … WITH METRICS` stay in `01`–`04` / `99`. Do
not treat this script as a second Unbilled formula.

No Azure. No workspace URL. Not demo 1. Do not edit
`demos/o2c-unbilled-semantic-layer/`.

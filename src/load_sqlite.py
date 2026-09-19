"""
Loads the cleaned CSVs into a local SQLite database so the SQL in sql/ can run.

Run:  python src/load_sqlite.py
Then: sqlite3 data/appeals.db < sql/06_sql_analysis.sql
"""

import os
import sqlite3

import pandas as pd

DB = os.path.join("data", "appeals.db")

TABLES = {
    "appeals_fact": os.path.join("data", "clean", "appeals_fact.csv"),
    "dq_exceptions": os.path.join("data", "clean", "dq_exceptions.csv"),
    "appeal_events": os.path.join("data", "raw", "appeal_events.csv"),
    "dim_payer": os.path.join("data", "raw", "dim_payer.csv"),
    "dim_team": os.path.join("data", "raw", "dim_team.csv"),
    "dim_reason_code": os.path.join("data", "raw", "dim_reason_code.csv"),
    "dim_date": os.path.join("data", "raw", "dim_date.csv"),
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_events_appeal ON appeal_events(Appeal_ID)",
    "CREATE INDEX IF NOT EXISTS ix_events_stage ON appeal_events(Process_Stage)",
    "CREATE INDEX IF NOT EXISTS ix_appeals_payer ON appeals_fact(Payer_ID)",
    "CREATE INDEX IF NOT EXISTS ix_appeals_status ON appeals_fact(Status)",
]


def main():
    if os.path.exists(DB):
        os.remove(DB)

    con = sqlite3.connect(DB)
    for name, path in TABLES.items():
        df = pd.read_csv(path)
        df.to_sql(name, con, if_exists="replace", index=False)
        print(f"{name:<18} {len(df):>7} rows")

    for stmt in INDEXES:
        con.execute(stmt)
    con.commit()
    con.close()
    print(f"\nwrote {DB}")


if __name__ == "__main__":
    main()

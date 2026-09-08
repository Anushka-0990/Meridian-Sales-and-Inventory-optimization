"""Runner: executes 02_business_SQL_analysis.sql against warehouse.db,
saves each result to outputs/ and prints a compact preview.
Demonstrates the SQL-analyst layer of the engagement."""
import sqlite3, re, os
import pandas as pd

DB, SQL = "warehouse.db", "02_business_SQL_analysis.sql"
os.makedirs("outputs", exist_ok=True)

text = open(SQL).read()
# drop pure-comment lines, then split into statements on ';'
lines = [l for l in text.splitlines() if not l.strip().startswith("--")]
script = "\n".join(lines)
statements = [s.strip() for s in script.split(";") if s.strip()]

conn = sqlite3.connect(DB)
labels = []
for i, stmt in enumerate(statements, start=1):
    # name the query from its comment block if present in original text
    m = re.search(r"Q(\d+)\s*\.", stmt)
    tag = f"Q{m.group(1)}" if m else f"Q{i}"
    try:
        df = pd.read_sql_query(stmt, conn)
    except Exception as e:
        print(f"!! {tag} FAILED: {e}\n  stmt: {stmt[:80]}")
        continue
    csv = f"outputs/sql_{tag}.csv"
    df.to_csv(csv, index=False)
    labels.append(tag)
    print(f"\n===== {tag}  ({df.shape[0]} rows x {df.shape[1]} cols) -> {csv} =====")
    with pd.option_context("display.width", 200, "display.max_rows", 30, "display.max_columns", 30):
        print(df.head(12).to_string(index=False))
conn.close()
print(f"\nSaved {len(labels)} SQL outputs: {', '.join(labels)}")

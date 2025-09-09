# nl2sql.py
import os, re, sqlite3, textwrap, json
from pathlib import Path
from tabulate import tabulate
from dotenv import load_dotenv

# ---- CONFIG ----
DB_PATH = Path("Chinook_Sqlite.sqlite")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")   # fast/cheap; change if you like

# ---- LLM client (OpenAI SDK v1) ----
load_dotenv()
try:
    from openai import OpenAI
    client = OpenAI()
except Exception as e:
    client = None

def assert_db():
    assert DB_PATH.exists(), f"{DB_PATH} not found. Run from the folder that contains it."

def get_schema(conn: sqlite3.Connection) -> dict:
    """Return a minimal schema description: tables -> columns + types."""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    ).fetchall()
    schema = {}
    for (t,) in tables:
        cols = conn.execute(f"PRAGMA table_info({t});").fetchall()
        schema[t] = [{"name": c[1], "type": c[2]} for c in cols]
    return schema

def schema_as_text(schema: dict) -> str:
    lines = []
    for t, cols in schema.items():
        cols_txt = ", ".join([f"{c['name']} {c['type']}" for c in cols])
        lines.append(f"- {t}({cols_txt})")
    return "\n".join(lines)

SYS_PROMPT = """\
You are a senior analytics engineer. Convert natural-language questions into a single, safe, \
dialect-correct **SQLite** SELECT query using only the provided schema. Rules:
- Return **only** the SQL, no prose, no backticks.
- Use explicit table names and qualified columns when joins are involved.
- Prefer COUNT(*), SUM(), AVG(), ORDER BY… LIMIT…
- Do NOT invent tables/columns not in the schema.
- Absolutely NO data-modifying statements (INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/ATTACH).
- One statement only.
"""

def llm_sql(question: str, schema_txt: str) -> str:
    if client is None:
        raise RuntimeError("OpenAI SDK not available. `pip install openai` and set OPENAI_API_KEY in .env")
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": f"Schema:\n{schema_txt}\n\nQuestion: {question}\nSQL:"},
        ],
    )
    sql = resp.choices[0].message.content.strip()
    # strip surrounding code fences if the model added them
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql).strip()
    return sql

WRITE_REGEX = re.compile(
    r"\b(INSERT|UPDATE|DELETE|ALTER|DROP|TRUNCATE|CREATE|REPLACE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)

def is_safe_select(sql: str) -> bool:
    if ";" in sql.strip()[:-1]:  # allow single trailing semicolon only
        return False
    if WRITE_REGEX.search(sql):
        return False
    return sql.strip().upper().startswith("SELECT")

def explain_results(question: str, sql: str, rows_preview: list, schema_txt: str) -> str:
    """Ask the LLM for a short explanation (1–2 sentences)."""
    if client is None:
        return ""
    preview = json.dumps(rows_preview[:5], ensure_ascii=False)
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Explain query results briefly for a business user in one or two sentences."},
            {"role": "user", "content": f"Question: {question}\nSQL: {sql}\nPreview rows: {preview}"},
        ],
    )
    return resp.choices[0].message.content.strip()

def run_query(conn, sql: str):
    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return cols, rows

def main():
    assert_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        schema = get_schema(conn)
        schema_txt = schema_as_text(schema)
        print("Loaded schema:")
        print(textwrap.indent(schema_txt, "  "))
        print("\nAsk a question (e.g., 'Top 5 countries by revenue', "
              "'Which albums have the most tracks?', 'Total revenue by year').")
        question = input("\nYour question: ").strip()
        if not question:
            print("No question provided. Exiting.")
            return

        sql = llm_sql(question, schema_txt)
        print("\n--- Generated SQL ---")
        print(sql)

        if not is_safe_select(sql):
            print("\n[BLOCKED] The generated SQL is not a single safe SELECT statement.")
            return

        # Optional confirmation
        ok = input("\nRun this query? [Y/n]: ").strip().lower()
        if ok and ok != "y":
            print("Canceled.")
            return

        cols, rows = run_query(conn, sql)
        print("\n--- Results ---")
        if rows:
            print(tabulate(rows, headers=cols, tablefmt="github"))
        else:
            print("(no rows)")

        # Short explanation
        try:
            expl = explain_results(question, sql, rows[:5], schema_txt)
            if expl:
                print("\n--- Explanation ---")
                print(expl)
        except Exception as _e:
            pass

    finally:
        conn.close()

if __name__ == "__main__":
    main()


# nl2sql.py
import os, re, sqlite3, textwrap, json, datetime
from pathlib import Path
from tabulate import tabulate
from dotenv import load_dotenv
try:
    import readline  # command history in many terminals
except Exception:
    pass

# ---- CONFIG ----
DB_PATH = Path("Chinook_Sqlite.sqlite")  # <-- change to your other .sqlite to switch datasets
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_HISTORY_TURNS = 15         # how many prior Q&A turns to include as context
ENABLE_EXPORTS = True         # set False to disable saving outputs
EXPORT_DIR = Path("outputs")

# ---- LLM client (OpenAI SDK v1) ----
load_dotenv()
try:
    from openai import OpenAI
    client = OpenAI()
except Exception:
    client = None

def assert_db():
    assert DB_PATH.exists(), f"{DB_PATH} not found. Run from the folder that contains it."

def get_schema(conn: sqlite3.Connection) -> dict:
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
You are a senior analytics engineer. Convert natural-language questions into a single, safe,
dialect-correct **SQLite** SELECT query using only the provided schema and (when given) the prior
Q&A history. Rules:
- Return **only** the SQL, no prose, no backticks.
- Use explicit table names and qualified columns when joins are involved.
- Prefer COUNT(*), SUM(), AVG(), ORDER BY … LIMIT …
- Do NOT invent tables/columns not in the schema.
- Absolutely NO data-modifying statements (INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/ATTACH).
- One statement only.
- Follow-ups may refer to earlier answers; infer intent from the provided history.
"""

WRITE_REGEX = re.compile(
    r"\b(INSERT|UPDATE|DELETE|ALTER|DROP|TRUNCATE|CREATE|REPLACE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)

def is_safe_select(sql: str) -> bool:
    if ";" in sql.strip()[:-1]:  # allow a single trailing semicolon only
        return False
    if WRITE_REGEX.search(sql):
        return False
    return sql.strip().upper().startswith("SELECT")

def build_history_context(history: list) -> str:
    """
    Compact prior turns for the LLM. Each item: {"q": str, "sql": str, "preview": [row tuples]}
    We only include last MAX_HISTORY_TURNS turns.
    """
    if not history:
        return ""
    chunks = []
    for i, h in enumerate(history[-MAX_HISTORY_TURNS:], 1):
        preview_json = json.dumps(h.get("preview", [])[:3], ensure_ascii=False)
        chunks.append(
            f"Turn {i}:\n"
            f"Q: {h.get('q','')}\n"
            f"SQL: {h.get('sql','')}\n"
            f"PreviewRows: {preview_json}\n"
        )
    return "\n".join(chunks)

def llm_sql(question: str, schema_txt: str, history_txt: str) -> str:
    if client is None:
        raise RuntimeError("OpenAI SDK not available. `pip install openai` and set OPENAI_API_KEY in .env")
    user_content = f"Schema:\n{schema_txt}\n\n"
    if history_txt:
        user_content += f"History (use for context if relevant):\n{history_txt}\n\n"
    user_content += f"Question: {question}\nSQL:"
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    sql = resp.choices[0].message.content.strip()
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql).strip()
    return sql

def explain_results(question: str, sql: str, rows_preview: list) -> str:
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

def export_run(slug: str, question: str, sql: str, cols, rows, explanation: str):
    if not ENABLE_EXPORTS:
        return
    EXPORT_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = EXPORT_DIR / f"{ts}_{slug}"
    # .sql
    (base.with_suffix(".sql")).write_text(sql + ("\n" if not sql.endswith("\n") else ""), encoding="utf-8")
    # .md
    md = []
    md.append(f"# Query: {question}\n")
    md.append("## SQL\n")
    md.append("```sql\n" + sql + "\n```\n")
    md.append("## Results\n")
    if rows:
        # tabulate to GitHub markdown
        md.append(tabulate(rows, headers=cols, tablefmt="github") + "\n")
    else:
        md.append("(no rows)\n")
    if explanation:
        md.append("## Explanation\n" + explanation + "\n")
    (base.with_suffix(".md")).write_text("\n".join(md), encoding="utf-8")

def slugify(text: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    return (s[:maxlen] or "query").strip("-")

def main():
    assert_db()
    conn = sqlite3.connect(DB_PATH)
    history = []  # list of {"q":..., "sql":..., "preview":[...]}
    try:
        schema = get_schema(conn)
        schema_txt = schema_as_text(schema)
        print("Loaded schema:")
        print(textwrap.indent(schema_txt, "  "))
        print("\nAsk questions (e.g., 'Top 5 countries by revenue', "
              "'Which albums have the most tracks?', 'Total revenue by year').")
        print("Type ':history' to view history, ':clear' to clear, ':schema' to reprint schema, "
              "or 'exit'/'quit' to stop.\n")

        while True:
            question = input("\nYour question: ").strip()
            low = question.lower()

            # Commands
            if low in {"exit", "quit", "q"}:
                print("Exiting. Goodbye!")
                break
            if low == ":history":
                if not history:
                    print("(no history)")
                else:
                    print("\n--- History (last turns) ---")
                    for i, h in enumerate(history[-MAX_HISTORY_TURNS:], 1):
                        print(f"{i}. Q: {h['q']}\n   SQL: {h['sql']}\n   Preview: {h.get('preview', [])[:2]}\n")
                continue
            if low == ":clear":
                history.clear()
                print("History cleared.")
                continue
            if low == ":schema":
                print("\nSchema:")
                print(textwrap.indent(schema_txt, "  "))
                continue
            if not question:
                print("No question provided. Try again.")
                continue

            # ---- generate SQL from LLM with history context ----
            history_txt = build_history_context(history)
            sql = llm_sql(question, schema_txt, history_txt)
            print("\n--- Generated SQL ---")
            print(sql)

            # ---- safety check ----
            if not is_safe_select(sql):
                print("\n[BLOCKED] The generated SQL is not a single safe SELECT statement.")
                continue

            # ---- confirm & run ----
            ok = input("\nRun this query? [Y/n]: ").strip().lower()
            if ok and ok != "y":
                print("Canceled.")
                continue

            cols, rows = run_query(conn, sql)
            print("\n--- Results ---")
            if rows:
                print(tabulate(rows, headers=cols, tablefmt="github"))
            else:
                print("(no rows)")

            # ---- brief explanation ----
            expl = ""
            try:
                expl = explain_results(question, sql, rows[:5])
                if expl:
                    print("\n--- Explanation ---")
                    print(expl)
            except Exception:
                pass

            # update history
            preview = rows[:3] if rows else []
            history.append({"q": question, "sql": sql, "preview": preview})

            # optional export
            try:
                slug = slugify(question)
                export_run(slug, question, sql, cols, rows, expl)
            except Exception:
                pass

    finally:
        conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")


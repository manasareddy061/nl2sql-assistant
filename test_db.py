import sqlite3
from pathlib import Path

DB_PATH = Path("Chinook_Sqlite.sqlite")

def show_tables(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    ).fetchall()
    print("Tables:")
    for (name,) in rows:
        print(" -", name)

def table_schema(conn, table):
    print(f"\nSchema for {table}:")
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    for cid, name, ctype, notnull, dflt, pk in rows:
        print(f"  {name:15} {ctype:10} NOTNULL={notnull} PK={pk}")

def sample_queries(conn):
    print("\nTop 5 tracks by length (ms):")
    rows = conn.execute("""
        SELECT t.Name AS track, a.Title AS album, t.Milliseconds AS ms
        FROM Track t
        JOIN Album a ON a.AlbumId = t.AlbumId
        ORDER BY t.Milliseconds DESC
        LIMIT 5;
    """).fetchall()
    for r in rows:
        print(" ", r)

    print("\nRevenue by country (top 5):")
    rows = conn.execute("""
        SELECT BillingCountry, ROUND(SUM(total),2) AS revenue
        FROM Invoice
        GROUP BY BillingCountry
        ORDER BY revenue DESC
        LIMIT 5;
    """).fetchall()
    for r in rows:
        print(" ", r)

if __name__ == "__main__":
    assert DB_PATH.exists(), "Chinook_Sqlite.sqlite not found in current folder."
    conn = sqlite3.connect(DB_PATH)
    try:
        show_tables(conn)
        table_schema(conn, "Invoice")
        sample_queries(conn)
    finally:
        conn.close()




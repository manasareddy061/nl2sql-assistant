



from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///Chinook_Sqlite.sqlite", echo=False)

with engine.connect() as conn:
    tables = conn.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )).fetchall()
    print("Tables:", [t[0] for t in tables])

    res = conn.execute(text("""
        SELECT c.FirstName || ' ' || c.LastName AS customer, COUNT(*) AS orders
        FROM customer c
        JOIN Invoice i ON i.CustomerId = c.CustomerId
        GROUP BY c.CustomerId
        ORDER BY orders DESC
        LIMIT 5;
    """)).fetchall()
    print("\nTop customers by orders:")
    for row in res:
        print(" ", row)


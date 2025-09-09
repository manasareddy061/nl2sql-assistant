# 🧠 NL2SQL Assistant

A Python-based assistant that converts **natural language questions into SQL queries** and runs them on the classic Chinook SQLite database — powered by OpenAI GPT models.

This project demonstrates **Agentic AI + LLMs** for database query automation. Perfect for showcasing **Data Engineering, AI/ML, and LLM integration skills**.

---

## 🚀 Features
- Natural language → **SQL** (safe, SELECT-only queries)
- Executes queries directly on the **Chinook SQLite** dataset
- Results displayed in clean, tabulated format
- **Explanations** generated for every query
- Secrets handled via `.env` (never exposed in GitHub)
- Ready for extension into **Streamlit UI** or CSV/Markdown exports

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/manasareddy061/nl2sql-assistant.git
cd nl2sql-assistant

### 2) Python env + deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 3) Get the Chinook database (kept out of Git)
git clone https://github.com/lerocha/chinook-database.git
cp chinook-database/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite .

### 4) API key
cp .env.example .env
nano .env         # set: OPENAI_API_KEY=sk-... (your real key)

### 5) Sanity tests
python3 test_db.py          # sqlite: list tables, sample queries
python3 test_sqlalchemy.py  # sqlalchemy: sample joins
python3 test_key.py         # OpenAI API key check

### 6) Run the NL→SQL assistant
python3 nl2sql.py



## 🧪 Example Prompts

Top 5 countries by revenue

Which customers placed the most invoices?

List the 10 longest tracks with album names

Total revenue by year, descending


## 📂 Project Structure


nl2sql-assistant/
├─ nl2sql.py               # NL → SQL assistant (uses OpenAI)
├─ test_db.py              # Raw sqlite checks
├─ test_sqlalchemy.py      # SQLAlchemy demo queries
├─ test_key.py             # API key verification
├─ requirements.txt        # Dependencies
├─ .env.example            # Template for secrets
└─ .gitignore              # Keeps .env & DB out of git

## 🔑 Environment

Create .env in the project root:

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

Tip: If a shell variable is overriding your file while testing, run:

unset OPENAI_API_KEY

## 🧰 Troubleshooting

Incorrect API key provided: sk-REPLACE_ME
Update .env with your real key and unset OPENAI_API_KEY, then re-run python3 test_key.py.

Chinook_Sqlite.sqlite not found
Ensure you copied the DB into the project root:

cp chinook-database/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite .

no such table: ...
Use exact Chinook table names (singular, capitalized):
Customer, Invoice, InvoiceLine, Track, etc.


## 🛠 Tech Stack

Python 3.10+

SQLite, SQLAlchemy

OpenAI Python SDK

python-dotenv, tabulate


## 📌 Roadmap

Multi-question chat loop with history

CSV/Markdown export of results

Streamlit UI

Support for Postgres/MySQL

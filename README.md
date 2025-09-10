# 🧠 NL2SQL Assistant

A Python-based assistant that converts **natural language questions into SQL queries** and runs them on the classic Chinook SQLite database — powered by OpenAI GPT models.

This project demonstrates **Agentic AI + LLMs** for database query automation.

---

## 🚀 Features
- Natural language → **SQL** (safe, SELECT-only queries)
- Executes queries directly on the **Chinook SQLite** dataset
- Results displayed in clean, tabulated format
- **Explanations** generated for every query
- **Multi-question interactive chat loop with history
- **Exports each run to `.sql` + `.md` (and optionally `.csv`)**  
- Secrets handled via `.env` (never exposed in GitHub)
- Ready for extension into **Streamlit UI** or other UIs

---

## ⚙️ Setup Instruction

### 1) Clone the repository
~~~bash
git clone https://github.com/manasareddy061/nl2sql-assistant.git
cd nl2sql-assistant
~~~

### 2) Create a virtual environment
~~~bash
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
~~~

### 3) Install dependencies
~~~bash
pip install -r requirements.txt
~~~

### 4) Configure environment variables
Create a `.env` file in the root with your OpenAI key:

~~~ini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=sqlite:///chinook.db
~~~

Unset any shell variable that might override:
~~~bash
unset OPENAI_API_KEY
~~~

### 5) Run quick connectivity checks
~~~bash
python3 test_db.py
python3 test_sqlalchemy.py
~~~

### 6) Verify OpenAI API key
~~~bash
python3 test_key.py
~~~

---

## 🧪 Example Prompts

- Top 5 countries by revenue  
- Which customers placed the most invoices?  
- List the 10 longest tracks with album names  
- Total revenue by year, descending  

---

## 📂 Project Structure
~~~text
nl2sql-assistant/
├─ nl2sql.py               # NL → SQL assistant (uses OpenAI, supports history + exports)
├─ test_db.py              # Raw sqlite checks
├─ test_sqlalchemy.py      # SQLAlchemy demo queries
├─ test_key.py             # API key verification
├─ requirements.txt        # Dependencies
├─ .env.example            # Template for secrets
├─ .gitignore              # Keeps .env, outputs/, and DB out of git
├─ outputs/                # Auto-saved query results (.sql + .md, ignored in Git)
└─ sample_outputs.zip      # Curated sample outputs (for demo in GitHub)
~~~

---

## 🔑 Environment

Create a `.env` file in the project root:

~~~ini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
~~~

Tip: If a shell variable is overriding your file while testing, run:

~~~bash
unset OPENAI_API_KEY
~~~

---

## 🧰 Troubleshooting

**Incorrect API key provided: `sk-REPLACE_ME`**  
Update `.env` with your real key and unset `OPENAI_API_KEY`, then re-run:
~~~bash
python3 test_key.py
~~~

**Chinook_Sqlite.sqlite not found**  
Ensure you copied the DB into the project root:
~~~bash
cp chinook-database/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
~~~


---

## 🛠 Tech Stack

- Python 3.10+  
- SQLite, SQLAlchemy  
- OpenAI Python SDK  
- python-dotenv, tabulate  

---

## 📌 Roadmap

- Multi-question chat loop with history  
- CSV/Markdown export of results  
- Streamlit UI  
- Support for Postgres/MySQL  


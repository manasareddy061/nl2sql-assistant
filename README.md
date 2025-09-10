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


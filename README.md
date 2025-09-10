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
```bash
git clone https://github.com/manasareddy061/nl2sql-assistant.git
cd nl2sql-assistant


` ### 2)` Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate


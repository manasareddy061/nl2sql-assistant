# app.py
import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Reuse your functions/constants from the CLI module
from nl2sql import (
    DB_PATH, MODEL, MAX_HISTORY_TURNS,
    get_schema, schema_as_text,
    build_history_context, llm_sql, is_safe_select,
    run_query, explain_results, export_run, slugify
)

load_dotenv()

st.set_page_config(page_title="NL2SQL Assistant", page_icon="🧠", layout="wide")
st.title("🧠 NL2SQL Assistant")
st.caption("Natural language → SQLite queries on the Chinook database")

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    db_ok = Path(DB_PATH).exists()
    st.write(f"**Database**: `{DB_PATH}` {'✅' if db_ok else '❌ not found'}")

    export_enabled = st.checkbox("Auto-export runs to outputs/", value=True)
    max_hist = st.number_input("History turns", min_value=0, max_value=50, value=MAX_HISTORY_TURNS, step=1)

    # Lazy-load schema once
    if "schema_txt" not in st.session_state:
        if db_ok:
            conn = sqlite3.connect(DB_PATH)
            with conn:
                schema = get_schema(conn)
            st.session_state.schema_txt = schema_as_text(schema)
            conn.close()
        else:
            st.session_state.schema_txt = "(DB not found)"

    with st.expander("Show schema", expanded=False):
        st.code(st.session_state.schema_txt, language="text")

    # History tools
    if st.button("Clear history"):
        st.session_state.history = []
        st.success("History cleared.")

# --- Session state init ---
if "history" not in st.session_state:
    st.session_state.history = []

if "conn" not in st.session_state and Path(DB_PATH).exists():
    st.session_state.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# --- Main input area ---
col_q, col_btn = st.columns([5,1])
with col_q:
    question = st.text_input("Ask a question", placeholder="e.g., Top 5 countries by revenue")
with col_btn:
    run_clicked = st.button("Run", use_container_width=True)

    
# --- Handle query run ---
if run_clicked:
    if not question.strip():
        st.warning("Please enter a question.")
    elif not Path(DB_PATH).exists():
        st.error(f"Database not found: {DB_PATH}")
    else:
        # Build history context
        hist_ctx = build_history_context(st.session_state.history[-max_hist:] if max_hist else [])
    
        # LLM -> SQL
        try:
            sql = llm_sql(question.strip(), st.session_state.schema_txt, hist_ctx)
        except Exception as e:
            st.error(f"Failed to generate SQL: {e}")
            sql = ""
        
        if sql:
            st.subheader("Generated SQL")
            st.code(sql, language="sql")
            
            # Safety check
            if not is_safe_select(sql):
                st.error("⚠️ Blocked: not a single safe SELECT statement.")
            else:
                # Run query
                try:
                    cols, rows = run_query(st.session_state.conn, sql)
                    df = pd.DataFrame(rows, columns=cols)
                except Exception as e:
                    st.error(f"Query error: {e}")
                    df = None

                if df is not None:
                    st.subheader("Results")   
                    st.dataframe(df, use_container_width=True)
        
                    # Explanation
                    try:
                        expl = explain_results(question, sql, rows[:5] if rows else [])
                    except Exception:
                        expl = ""
                    if expl:
                        with st.expander("Explanation"):
                            st.write(expl)
            
                    # Update history
                    preview = rows[:3] if rows else []
                    st.session_state.history.append({"q": question, "sql": sql, "preview": preview})
            
                    # Export
                    if export_enabled:
                        try:
                            slug = slugify(question)
                            export_run(slug, question, sql, cols, rows, expl)
                            st.toast("Saved to outputs/ ✅", icon="💾")
                        except Exception as e:
                            st.warning(f"Export failed: {e}")
# --- History panel ---
st.markdown("---")
st.subheader("Chat history")
if not st.session_state.history:
    st.caption("No history yet.")
else:
    for i, h in enumerate(st.session_state.history[-max_hist:][::-1], 1):
        with st.expander(f"{i}. {h['q']}", expanded=False):   
            st.code(h["sql"], language="sql")
            if h.get("preview"): 
                st.caption("Preview rows")
                st.write(pd.DataFrame(h["preview"]))

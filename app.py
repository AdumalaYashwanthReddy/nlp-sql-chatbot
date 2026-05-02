import streamlit as st
import sqlite3
import re
import time
import pandas as pd
from groq import Groq

# ── CONFIG ────────────────────────────────────────────────────────────────────
GROQ_API_KEY =  st.secrets["GROQ_API_KEY"]
DB_PATH      = "ecommerce.db"

client = Groq(api_key=GROQ_API_KEY)

# ── SCHEMA ────────────────────────────────────────────────────────────────────
SCHEMA_CONTEXT = """
You are an expert SQL analyst working with a SQLite database.
The database has TWO tables:

TABLE 1: amazon_sales (121,180 rows — one row per order)
  - order_id      TEXT    : unique order ID
  - date          TEXT    : format YYYY-MM-DD e.g. 2022-04-30
  - status        TEXT    : ONLY these 4 values: Shipped, Cancelled, Pending, Returned
  - fulfilment    TEXT    : Amazon or Merchant
  - service_level TEXT    : Expedited or Standard
  - sku           TEXT    : product SKU — JOIN key with sale_report
  - category      TEXT    : e.g. kurta, Set, Western Dress, Top
  - size          TEXT    : S, M, L, XL, XXL, 3XL
  - qty           INTEGER : units ordered
  - amount        REAL    : amount paid in INR
  - ship_city     TEXT    : e.g. MUMBAI, BENGALURU
  - ship_state    TEXT    : e.g. MAHARASHTRA, KARNATAKA
  - is_b2b        BOOLEAN : TRUE if B2B order
  - fulfilled_by  TEXT    : Easy Ship, Amazon, Merchant

TABLE 2: sale_report (9,188 rows — one row per SKU)
  - sku           TEXT    : JOIN key with amazon_sales
  - design_no     TEXT    : design number
  - stock         REAL    : stock quantity
  - category      TEXT    : e.g. KURTA, KURTA SET, DRESS
  - size          TEXT    : size
  - color         TEXT    : e.g. Red, Blue, Black

JOIN: amazon_sales s LEFT JOIN sale_report p ON s.sku = p.sku

BUSINESS RULES:
1. Always WHERE s.status = Shipped for revenue/sales questions
2. Use SUBSTR(date,1,7) for monthly grouping e.g. 2022-04
3. Always ROUND(SUM(amount), 2) for money
4. Always LEFT JOIN — never INNER JOIN
5. Never write DROP, DELETE, UPDATE, INSERT, ALTER
6. When using sale_report columns like color add WHERE p.color IS NOT NULL
"""

# ── HELPERS ───────────────────────────────────────────────────────────────────
def build_prompt(question):
    return f"""
{SCHEMA_CONTEXT}

Convert the question below into a valid SQLite SQL query.

STRICT RULES:
1. Return ONLY the raw SQL — no explanation, no markdown, no ```sql fences
2. Use aliases: amazon_sales AS s, sale_report AS p
3. Always LEFT JOIN when joining tables
4. LIMIT 10 for top-N questions unless specified
5. ROUND all money to 2 decimal places

QUESTION: {question}

SQL QUERY:
"""

def clean_sql(raw):
    sql = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    sql = sql.replace("```", "").strip()
    for word in ["DROP","DELETE","UPDATE","INSERT","ALTER","TRUNCATE"]:
        if word in sql.upper():
            raise ValueError(f"Unsafe SQL blocked: {word}")
    return sql

def ask(question):
    prompt = build_prompt(question)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        raw_sql = response.choices[0].message.content.strip()
        time.sleep(1)
        sql = clean_sql(raw_sql)
        conn   = sqlite3.connect(DB_PATH)
        result = pd.read_sql_query(sql, conn)
        conn.close()
        return result, sql, None
    except ValueError as e:
        return None, "", str(e)
    except Exception as e:
        return None, "", str(e)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce SQL Chatbot",
    page_icon="🛍️",
    layout="wide"
)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛍️ E-Commerce\\nSQL Chatbot")
    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "This chatbot converts natural language "
        "questions into SQL and queries a real "
        "Amazon India sales database with **121,180 orders**."
    )
    st.markdown("---")
    st.markdown("### Sample Questions")
    sample_questions = [
        "What is the total revenue from shipped orders?",
        "Which city received the most orders?",
        "Show me revenue by month",
        "What is the cancellation rate by fulfilment type?",
        "Which color has the highest revenue?",
        "Top 5 states by number of orders?",
        "How many B2B orders are there?",
        "Which SKU sold the most units?",
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state.selected_question = q

    st.markdown("---")
    st.markdown("### Database")
    st.markdown("📦 **amazon_sales** — 121,180 rows")
    st.markdown("🏷️ **sale_report** — 9,188 rows")
    st.markdown("🔗 Joined on `sku`")

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.title("Ask your data anything 💬")
st.markdown("Type a question in plain English — get answers from your real sales database.")
st.markdown("---")

# ── CHAT HISTORY ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            if msg.get("error"):
                st.error(msg["error"])
            else:
                st.dataframe(msg["result"], use_container_width=True)
                if msg.get("show_sql"):
                    st.code(msg["sql"], language="sql")
        else:
            st.markdown(msg["content"])

# ── INPUT ─────────────────────────────────────────────────────────────────────
if "selected_question" in st.session_state:
    prefill = st.session_state.pop("selected_question")
else:
    prefill = ""

user_input = st.chat_input("e.g. What are the top 5 states by revenue?")
question = user_input or prefill

# ── PROCESS QUESTION ──────────────────────────────────────────────────────────
if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL and querying database..."):
            result, sql, error = ask(question)

        if error:
            st.error(f"❌ {error}")
            st.session_state.messages.append({
                "role": "assistant",
                "error": f"❌ {error}",
                "result": None,
                "sql": "",
                "show_sql": False
            })
        else:
            if result is not None and not result.empty:
                st.success(f"✅ Found {len(result)} row(s)")
                st.dataframe(result, use_container_width=True)

                # SQL toggle
                show_sql = st.toggle("Show generated SQL", value=False)
                if show_sql:
                    st.code(sql, language="sql")

                st.session_state.messages.append({
                    "role": "assistant",
                    "result": result,
                    "sql": sql,
                    "error": None,
                    "show_sql": show_sql
                })
            else:
                msg = "⚠️ No results found. Try rephrasing your question."
                st.warning(msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "error": msg,
                    "result": None,
                    "sql": sql,
                    "show_sql": False
                })
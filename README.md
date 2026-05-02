# NLP-to-SQL E-Commerce Chatbot

A conversational AI chatbot that converts plain English questions into SQL queries and returns answers from a real Amazon India e-commerce database with 121,180 orders.

Built with LLaMA 3.3-70b (via Groq), SQLite, and Streamlit.

---

## Live Demo

👉 [Try the chatbot here]([httpsyour-app-url.streamlit.app](https://nlp-sql-chatbot-kknj5jywvrv9jupkn3qmw3.streamlit.app/))

---

## Example Questions You Can Ask

 Question  Type 
------
 What is the total revenue from shipped orders  Aggregation 
 Which city received the most orders  Grouping 
 Show me revenue by month  Time series 
 What is the cancellation rate by fulfilment type  Comparison 
 Which color has the highest revenue  JOIN query 
 Top 5 states by number of orders  Ranking 
 How many B2B orders are there  Filter 
 Which SKU sold the most units  JOIN + ranking 

---

## Architecture

```
User Question (plain English)
        ↓
Prompt Builder  ←  Schema Context + Business Rules
        ↓
LLaMA 3.3-70b via Groq API
        ↓
Generated SQL Query
        ↓
SQL Cleaner + Safety Check
        ↓
SQLite Database (ecommerce.db)
        ↓
Result → Streamlit UI
```

---

## 📂 Project Structure

```
nlp-sql-chatbot
├── app.py                  # Main Streamlit application
├── ecommerce.db            # SQLite database (2 tables, 130K+ rows)
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

## 🗄️ Database

The SQLite database contains two tables loaded from a real Kaggle e-commerce dataset

`amazon_sales` — 121,180 rows
 Column  Type  Description 
---------
 order_id  TEXT  Unique order identifier 
 date  TEXT  Sale date (YYYY-MM-DD) 
 status  TEXT  Shipped  Cancelled  Pending  Returned 
 fulfilment  TEXT  Amazon or Merchant 
 sku  TEXT  Product SKU — JOIN key 
 category  TEXT  Product category 
 amount  REAL  Amount paid in INR 
 ship_state  TEXT  Destination state 

`sale_report` — 9,188 rows
 Column  Type  Description 
---------
 sku  TEXT  Product SKU — JOIN key 
 category  TEXT  Product category 
 color  TEXT  Product color 
 size  TEXT  Product size 
 stock  REAL  Stock quantity 

---

##  Test Results

Tested against 15 natural language questions across 3 difficulty levels

 Difficulty  Questions  Passed 
---------
 Easy (single table)  5  5 
 Medium (aggregation + grouping)  5  5 
 Hard (JOIN across tables)  5  5 
 Total  15  15 (100%) 

---

## Key Insights from the Data

- Total revenue from shipped orders ₹6.97 Crore (Apr–Jun 2022)
- Top state by orders Maharashtra (18,837 orders)
- Peak month April 2022 (₹2.57 Cr revenue)
- Amazon cancellation rate 6.7% vs Merchant 13.7%
- Best selling category Kurta (42,731 units)
- Top color by revenue Blue (₹83.2 Lakhs)

---

## Tech Stack

 Component  Technology 
------
 LLM  LLaMA 3.3-70b via Groq API 
 Database  SQLite 
 Frontend  Streamlit 
 Data processing  Pandas 
 Language  Python 3.10+ 

---

## ⚙️ Run Locally

1. Clone the repository
```bash
git clone httpsgithub.comgithubusernamenlp-sql-chatbot.git
cd nlp-sql-chatbot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Add your Groq API key

Create a file `.streamlitsecrets.toml` in the project folder
```toml
GROQ_API_KEY = your_groq_api_key_here
```
Get a free key at [console.groq.com](httpsconsole.groq.com)

4. Run the app
```bash
streamlit run app.py
```

---

## Data Source

Dataset [E-Commerce Sales Dataset](httpswww.kaggle.com) — Amazon India sales data including orders, SKUs, fulfilment details, and product catalog.

---

## 👤 Author

Author
Built as part of my AI Engineer learning journey — roadmap.sh/ai-engineer

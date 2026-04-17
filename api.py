from fastapi import FastAPI
from db import get_connection
from nlp import convert_to_sql

app = FastAPI()

# ---------------- SAFETY CHECK ----------------
def is_safe(query):
    query = query.lower()
    dangerous = ["drop", "delete", "update", "insert", "alter", "--"]
    return not any(word in query for word in dangerous)

# ---------------- API ----------------
@app.get("/query")
def run_query(user_input: str):
    query = convert_to_sql(user_input)

    if "ERROR" in query:
        return {"error": query}

    if not is_safe(query):
        return {"error": "Unsafe query blocked"}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query)

        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]  # ✅ FIX

        conn.close()

        return {
            "query": query,
            "data": data,
            "columns": columns   # ✅ RETURN COLUMN NAMES
        }

    except Exception as e:
        return {"error": str(e)}
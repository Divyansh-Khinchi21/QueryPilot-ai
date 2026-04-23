from fastapi import FastAPI
from db import get_connection
from nlp import convert_to_sql

app = FastAPI()


# ---------------- SAFETY ----------------
def is_safe(query):
    return query.lower().strip().startswith("select")


# ---------------- API ----------------
@app.get("/query")
def run_query(user_input: str):
    try:
        # ✅ Quick test endpoint
        if user_input.lower() in ["test", "hello"]:
            return {
                "query": "SELECT 1",
                "data": [(1,)],
                "columns": ["result"]
            }

        # 🔹 Convert NL → SQL
        query = convert_to_sql(user_input)

        if "ERROR" in query:
            return {"error": query}

        if not is_safe(query):
            return {"error": "Only SELECT queries are allowed."}

        # 🔹 Execute Query
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query)

        except Exception as err:
            return {"error": f"SQL Error: {str(err)}"}

        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        cursor.close()
        conn.close()

        return {
            "query": query,
            "data": data,
            "columns": columns
        }

    except Exception as e:
        return {"error": str(e)}
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
        # 🔥 QUICK RESPONSE TEST (IMPORTANT)
        if user_input.lower() in ["test", "hello"]:
            return {
                "query": "SELECT 1",
                "data": [(1,)],
                "columns": ["result"]
            }

        # 🔥 STEP 1: NL → SQL
        query = convert_to_sql(user_input)

        if "ERROR" in query:
            return {"error": query}

        # 🔥 STEP 2: Safety check
        if not is_safe(query):
            return {"error": "Only SELECT queries are allowed."}

        # 🔥 STEP 3: DB connect
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query)

        except Exception as err:
            # 🔥 Auto-fix query
            fix_prompt = f"""
            Fix this SQL query:

            {query}

            Error:
            {err}

            Only return corrected SQL.
            """

            fixed_query = convert_to_sql(fix_prompt)

            if "ERROR" in fixed_query:
                return {"error": fixed_query}

            if not is_safe(fixed_query):
                return {"error": "Unsafe query after fix"}

            cursor.execute(fixed_query)
            query = fixed_query

        # 🔥 STEP 4: Fetch data
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
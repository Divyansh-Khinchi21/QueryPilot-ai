from fastapi import FastAPI
from db import get_connection
from nlp import convert_to_sql

app = FastAPI()


# ---------------- SAFETY ----------------
def is_safe(query):
    q = query.lower().strip()
    return q.startswith("select")


# ---------------- API ----------------
@app.get("/query")
def run_query(user_input: str):
    try:
        # 🔥 STEP 1: Detect NON-SELECT intent FIRST
        unsafe_keywords = ["create", "insert", "delete", "update", "drop"]

        if any(word in user_input.lower() for word in unsafe_keywords):
            explanation_prompt = f"""
            User asked: {user_input}

            Explain how to do this in SQL.
            Give example query.
            Do NOT execute anything.
            """

            explanation = convert_to_sql(explanation_prompt)

            return {
                "query": "Not executable",
                "data": [],
                "columns": [],
                "explanation": explanation
            }

        # 🔹 STEP 2: NL → SQL
        query = convert_to_sql(user_input)

        if "ERROR" in query:
            return {"error": query}

        # 🔹 STEP 3: Safety check on generated SQL
        if not is_safe(query):
            return {"error": "Only SELECT queries are allowed."}

        # 🔹 STEP 4: Execute query
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query)

        except Exception as err:
            # 🔥 STEP 5: Auto-fix SQL
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

        # 🔹 STEP 6: Fetch data
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
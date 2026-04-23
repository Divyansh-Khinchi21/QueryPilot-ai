import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def convert_to_sql(user_input):
    prompt = f"""
    You are an expert SQL generator.

    Convert natural language into SQL query.

    Database Schema:
    sales(customer, revenue, date)

    Rules:
    - ONLY SELECT queries
    - NO explanation
    - ALWAYS add LIMIT 10 if missing
    - Return ONLY SQL

    Input: {user_input}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ FIXED
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200
        )

        query = response.choices[0].message.content.strip()

        query = query.replace("```sql", "").replace("```", "").strip()

        if "SELECT" in query.upper():
            query = query[query.upper().find("SELECT"):]

        return query

    except Exception as e:
        return f"ERROR: {str(e)}"
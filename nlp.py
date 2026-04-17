import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def convert_to_sql(user_input):
    prompt = f"""
    You are an expert SQL generator.

    Convert natural language into SQL query.

    Database Schema:
    sales(customer, revenue, date)

    Rules:
    - Only SELECT queries
    - No explanation
    - Add LIMIT 10 if missing
    - Optimize query

    Input: {user_input}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        query = response.choices[0].message.content.strip()

        # cleanup
        query = query.replace("```sql", "").replace("```", "").strip()

        if "SELECT" in query:
            query = query[query.upper().find("SELECT"):]

        return query

    except Exception as e:
        return f"ERROR: {str(e)}"
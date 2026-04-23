import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="QueryPilot AI", layout="centered")

# ---------------- UI ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}
.title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🤖 QueryPilot AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask anything about your database</div>', unsafe_allow_html=True)

st.info("⚡ First query may take 10–20 sec (server wake-up)")

# ---------------- API ----------------
def call_api(user_input):
    url = "https://querypilot-ai.onrender.com/query"

    try:
        res = requests.get(url, params={"user_input": user_input}, timeout=30)

        # Server error
        if res.status_code != 200:
            return {"error": f"Server error: {res.status_code}"}

        # Empty response
        if not res.text.strip():
            return {"error": "Backend is sleeping, try again"}

        # JSON parsing
        try:
            return res.json()
        except:
            return {"error": "Invalid response from backend, try again"}

    except requests.exceptions.Timeout:
        return {"error": "Server is waking up, please try again"}
    except Exception:
        return {"error": "Backend not responding, please try again"}

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Ask your database...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call backend
    res = call_api(user_input)

    # Handle response
    if "error" in res:
        st.session_state.messages.append({
            "role": "assistant",
            "content": res["error"],
            "data": None
        })

    elif "explanation" in res:
        st.session_state.messages.append({
            "role": "assistant",
            "content": res["explanation"],
            "data": None
        })

    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Here is your result 👇",
            "data": res
        })

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # Show result
        if msg["role"] == "assistant" and msg.get("data"):
            res = msg["data"]

            # SQL Query
            st.markdown("### 🧾 SQL Query")
            st.code(res.get("query", ""), language="sql")

            # Data
            if res.get("data"):
                df = pd.DataFrame(res["data"], columns=res["columns"])

                st.markdown("### 📊 Result")
                st.dataframe(df, use_container_width=True)

                # Chart
                if not df.empty and df.shape[1] >= 2:
                    st.markdown("### 📈 Visualization")

                    num_cols = df.select_dtypes(include="number").columns

                    if len(num_cols) > 0:
                        try:
                            st.bar_chart(df.set_index(df.columns[0])[num_cols])
                        except:
                            st.line_chart(df[num_cols])

        # Explanation block
        if msg["role"] == "assistant" and msg.get("data") is None:
            if msg.get("content"):
                if any(word in msg["content"].upper() for word in ["CREATE", "INSERT", "UPDATE", "DELETE"]):
                    st.info("💡 This is an explanation (not executed)")
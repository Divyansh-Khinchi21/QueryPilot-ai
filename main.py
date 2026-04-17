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

# ---------------- API ----------------
def call_api(user_input):
    url = "http://127.0.0.1:8000/query"
    return requests.get(url, params={"user_input": user_input}).json()

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Ask your database...")

if user_input:
    # user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # call backend
    res = call_api(user_input)

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
            "content": res["query"],
            "data": res
        })

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # show result if exists
        if msg["role"] == "assistant" and msg.get("data"):
            res = msg["data"]

            # SQL
            st.markdown("### 🧾 SQL Query")
            st.code(res["query"], language="sql")

            # Data
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

        # show explanation if exists
        if msg["role"] == "assistant" and msg.get("data") is None and msg.get("content"):
            if "CREATE" in msg["content"] or "INSERT" in msg["content"]:
                st.info("💡 This is an explanation (not executed):")
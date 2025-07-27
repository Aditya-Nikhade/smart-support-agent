import requests
import streamlit as st

st.title("🤖 Smart Support Agent")
st.write("Ask me about refunds, shipping, or check the status of your order (e.g., 'order 12345').")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Thinking..."):
        api_url = "http://127.0.0.1:8000/support"
        response = requests.post(api_url, json={"message": prompt})
        if response.status_code == 200:
            bot_reply = response.json()["reply"]
        else:
            bot_reply = "Sorry, I'm having trouble connecting to my brain. Please try again."
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
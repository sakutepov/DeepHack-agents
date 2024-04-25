import os
import streamlit as st
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage
from langchain_core.messages import AIMessage

st.title("Научный конденсатор")

llm = GigaChat(credentials=os.getenv('GIGACHAT_TOKEN'),
               scope='GIGACHAT_API_CORP',
               verify_ssl_certs=False,
               model='GigaChat-Pro-preview',
               # stream=True,

               )

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.messages:
    last_user_message = next((m for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
    last_assistant_message = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
    if last_user_message:
        with st.chat_message(last_user_message["role"]):
            st.markdown(last_user_message["content"])
    if last_assistant_message:
        with st.chat_message(last_assistant_message["role"]):
            st.markdown(last_assistant_message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = llm.invoke([
            HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
            for m in st.session_state.messages
        ]
        )
        response = st.markdown(stream.content)
    st.session_state.messages.append({"role": "assistant", "content": stream.content})

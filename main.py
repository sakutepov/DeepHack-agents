import io
import os
import json
import streamlit as st
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage
from langchain_core.messages import AIMessage

from services.cal import create_ical
import services.conference_agent as conference_agent
import services.pubMed_search_agent as pubMed_search_agent

from dotenv import dotenv_values

config = dotenv_values("config.env")


st.title("Научный конденсатор")

llm = GigaChat(credentials=config['GIGACHAT_TOKEN'],
               scope='GIGACHAT_API_CORP',
               verify_ssl_certs=False,
               model='GigaChat-Pro-preview',
               # stream=True,
               profanity_check  = False
               )

ca  = conference_agent.ConferenceAgent(llm)
pma = pubMed_search_agent.PubMedSearchAgent(llm)

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
    try:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner('Собираю всю нужную информацию для ответа...'):
            assistant_responce = ""
            pubMed_info = pma.process_query(prompt)
            conf_info = ca.process_query(prompt)
            assistant_responce += pubMed_info
            if conf_info[0] != '':
                assistant_responce += '\n\n\n' + conf_info[0]
            print('output test: ', assistant_responce)
        st.success('Done!')
        with st.chat_message("assistant"):

            response = st.markdown(assistant_responce)
        st.session_state.messages.append({"role": "assistant", "content": assistant_responce})

        #st.session_state.messages.append({"role": "assistant", "content": assistant_responce})
        if conf_info[0] != '':
            conf_json = conf_info[1]# json.loads(conf_info[1])
            ical_data = create_ical(conf_json)

            # Пишем данные в объект BytesIO
            ical_stream = io.BytesIO(ical_data)

            # Предлагаем пользователю скачать файл
            st.download_button(
                label="Добавить в личный календарь", #Скачать iCal файл
                data=ical_stream,
                file_name="event.ics",
                mime="text/calendar"
            )
    except Exception as e:
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


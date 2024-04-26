import io
import os

import streamlit as st
from langchain.chat_models.gigachat import GigaChat
from langchain_core.messages import HumanMessage, AIMessage

from services import ConferenceAgent, PubMedSearchAgent, create_ical

st.title("Научный конденсатор")

llm = GigaChat(credentials=os.getenv('GIGACHAT_TOKEN'),
               scope='GIGACHAT_API_CORP',
               verify_ssl_certs=False,
               model='GigaChat-Pro-preview',
               profanity_check=False
               )

ca = ConferenceAgent(llm)
pma = PubMedSearchAgent(llm)

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

if prompt := st.chat_input("Что нового в медицине?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        assistant_responce = ""
        with st.spinner('Собираю всю нужную информацию для ответа...'):
            pubMed_info = pma.process_query(prompt)
            conf_info = ca.process_query(prompt)
            assistant_responce += pubMed_info
            if conf_info[0] != '':
                assistant_responce += '\n\n\n' + conf_info[0]
            print('output test: ', assistant_responce)
        st.success('Done!')
        response = st.markdown(assistant_responce)
    st.session_state.messages.append({"role": "assistant", "content": assistant_responce})

    if conf_info[0] != '':
        conf_json = conf_info[1]  # json.loads(conf_info[1])
        ical_data = create_ical(conf_json)

        # Пишем данные в объект BytesIO
        ical_stream = io.BytesIO(ical_data)

        # Предлагаем пользователю скачать файл
        st.download_button(
            label="Добавить в личный календарь",  # Скачать iCal файл
            data=ical_stream,
            file_name="event.ics",
            mime="text/calendar"
        )

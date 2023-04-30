import streamlit as st
from gtts import gTTS
import tempfile
import base64

def text_to_speech(text):
    tts = gTTS(text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + '.mp3')
        with open(fp.name + '.mp3', 'rb') as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode()
        audio_tag = f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg" /></audio>'
        st.markdown(audio_tag, unsafe_allow_html=True)

st.set_page_config(page_title="Chat App", page_icon=":speech_balloon:")

st.title("Chat Application")

user_input = st.text_input("Enter your message:")
send_button = st.button("Send")

if send_button and user_input:
    response = "This is the chatbot's response to: " + user_input
    text_to_speech(response)

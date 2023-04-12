import streamlit as st
from gtts import gTTS
from tempfile import NamedTemporaryFile
import base64

def get_audio_player(audio_data):
    audio_base64 = base64.b64encode(audio_data).decode()
    return f'<audio autoplay visibility="hidden" controls src="data:audio/mp3;base64,{audio_base64}">'

def text_to_speech(text):
    
    tts = gTTS(text=text, lang='en')
    with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio_data = open(tmp_file.name, "rb").read()
    audio_player = get_audio_player(audio_data)
    st.write(audio_player, unsafe_allow_html=True)

st.title('Text-to-Speech App')

user_input = st.text_input('Enter text to be spoken:')
if user_input:
    text_to_speech(user_input)
    
    

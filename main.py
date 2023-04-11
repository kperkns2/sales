import streamlit as st
from speech_to_text import speech_to_text

def transcribe_audio(audio_data, language="en-US"):
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language,
    )
    audio = speech.RecognitionAudio(content=audio_data)

    response = client.recognize(config=config, audio=audio)
    transcription = ""

    for result in response.results:
        transcription += result.alternatives[0].transcript

    return transcription

st.set_page_config(page_title="Speech to Text", layout="wide")
st.title("Speech to Text")

with st.form(key="my_form"):
    st.write("Press and hold the button while speaking:")
    audio_base64 = speech_to_text()
    
    if audio_base64:
        st.write("Processing the audio...")
        audio_data = base64.b64decode(audio_base64.split(",")[1])
        transcription = transcribe_audio(audio_data)
        st.write("Transcription:", transcription)
        
        submit_button = st.form_submit_button(label="Submit")
        if submit_button:
            st.write("You submitted:", transcription)


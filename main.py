import streamlit as st
import requests
import json
import time
import os

google_cred = {}
for k in ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url']:
  google_cred[k] = st.secrets[k]

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(google_cred)

# Set up Google APIs
from google.cloud import texttospeech
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import types

st.write('hi')

# Streamlit app
def main():
    st.write('hello')
    # Set up Google text-to-speech API
    client = texttospeech.TextToSpeechClient()
    
    # Set up Google speech-to-text API
    client_stt = speech.SpeechClient()

    # Set up Streamlit app
    st.title("Real-time chat with Google APIs")

    # Display initial prompt and read it using text-to-speech API
    prompt = "Welcome to the chat. Please say something."
    st.write("Agent: " + prompt)
    with st.spinner('Loading audio...'):
        synthesis_input = texttospeech.SynthesisInput(text=prompt)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
        os.system("afplay output.mp3")

    # Real-time chat loop
    conversation = []
    while True:
        # Use speech-to-text API to decode user's response
        with st.spinner('Listening...'):
            config = speech.RecognitionConfig(
                encoding=types.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            streaming_config = speech.StreamingRecognitionConfig(
                config=config, interim_results=True
            )

            def request_generator():
                yield speech.StreamingRecognizeRequest(
                    streaming_config=speech.StreamingRecognitionConfig(config=config, interim_results=True)
                )
                while True:
                    time.sleep(0.1)
                    data = {"audio": []}
                    while st._is_running:
                        if st.session_state.record:
                            data["audio"].append(st.session_state.record.pop(0))
                        else:
                            break
                    if not data["audio"]:
                        st.warning("No audio detected. Please try again.")
                    else:
                        # Decode the audio to text using the Speech-to-Text API
                        audio_data = data["audio"].getvalue()
                        text = transcribe_speech(audio_data, language_code)

                        # Add the user's message to the conversation history
                        conversation.append(('user', text))

                        # Generate a response using the conversation history
                        response = generate_response(conversation)

                        # Add the agent's message to the conversation history
                        conversation.append(('agent', response))

                        # Display the agent's message to the user
                        st.write("AI: ", response)

                        # Convert the agent's message to speech using the Text-to-Speech API
                        audio_content = synthesize_speech(response, language_code)
                        play_audio(audio_content)

main()

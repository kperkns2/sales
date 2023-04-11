import streamlit as st
import pyaudio
import io
import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech_v1 as tts

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/credentials.json'

# Initialize the Google Speech client
speech_client = speech.SpeechClient()

# Initialize the Google Text-to-Speech client
tts_client = tts.TextToSpeechClient()


def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    return b''.join(frames)


def transcribe_audio(audio_data):
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = speech_client.recognize(config=config, audio=audio)

    return response.results[0].alternatives[0].transcript


def synthesize_speech(text):
    input_text = tts.SynthesisInput(text=text)
    voice = tts.VoiceSelectionParams(
        language_code="en-US", ssml_gender=tts.SsmlVoiceGender.FEMALE
    )
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    return response.audio_content


def play_audio(audio_data):
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=24000,
                    output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    p.terminate()


st.title("Streamlit Chat with Google STT and TTS")

if st.button("Start conversation"):
    st.write("Please speak for 5 seconds...")

    audio_data = record_audio()
    transcript = transcribe_audio(audio_data)

    st.write(f"You said: {transcript}")

    response_text = f"You said: {transcript}"
    response_audio = synthesize_speech(response_text)
    play_audio(response_audio)

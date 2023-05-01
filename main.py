import streamlit as st
from streamlit.components.v1 import html

st.title("Text to Speech POC")

user_input = st.text_input("Enter your text:")

if st.button("Speak"):
    js_code = f"""
    <script>
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const utterance = new SpeechSynthesisUtterance("You said {user_input}");

        utterance.onstart = function (event) {{
            audioContext.resume();
        }};

        window.speechSynthesis.speak(utterance);
    </script>
    """

    html(js_code, height=0)

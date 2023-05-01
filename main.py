import streamlit as st
from streamlit.components.v1 import html

st.title("-- Text to Speech POC --")

user_input = st.text_input("Enter your text:")

js_code = """
<script>
    function speak(text) {
        console.log("speak() called with:", text);
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const utterance = new SpeechSynthesisUtterance(text);

        utterance.onstart = function (event) {
            audioContext.resume();
        };

        window.speechSynthesis.speak(utterance);
    }
</script>
"""

html(js_code)

if st.button("Speak"):
    # Call the speak function with the user input
    html(f"<script>speak('You said {user_input}')</script>")

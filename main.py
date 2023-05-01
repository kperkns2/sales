import streamlit as st

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



if st.button("Speak"):
    # Call the speak function with the user input
    st.markdown(f"<script>console.log("Hello world");</script>", unsafe_allow_html=True)
    st.markdown(js_code, unsafe_allow_html=True)
    st.markdown(f"<script>speak('You said {user_input}')</script>", unsafe_allow_html=True)

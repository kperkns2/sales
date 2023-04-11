import streamlit as st
from streamlit import components
import os

_RELEASE = False

if _RELEASE:
    _component_func = components.declare_component(
        "speech_to_text_component",
        url="https://your-deployed-component-url",
    )
else:
    _component_func = components.declare_component("speech_to_text_component", path="speech_to_text_component")


def speech_to_text(key=None):
    return _component_func(key=key)


if __name__ == "__main__":
    st.set_page_config(page_title="Speech to Text", layout="wide")
    st.title("Speech to Text")

    with st.form(key="my_form"):
        st.write("Press and hold the button while speaking:")
        transcription = speech_to_text()
        st.write("Transcription:", transcription)

        submit_button = st.form_submit_button(label="Submit")
        if submit_button:
            st.write("You submitted:", transcription)

import streamlit as st
from streamlit.components.v1 import declare_component
import os

_RELEASE = False

if _RELEASE:
    _component_func = declare_component(
        "speech_to_text_component",
        url="https://your-deployed-component-url",
    )
else:
    _component_func = declare_component("speech_to_text_component", path="speech_to_text_component")


def speech_to_text(key=None):
    return _component_func(key=key)

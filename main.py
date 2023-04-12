import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events



toggle_button = Button(label="Start Listening", width=100)

toggle_button.js_on_event("button_click", CustomJS(code="""
    console.log(this.label)
    if (this.label == "Start Listening") {
        this.label = "Speak";
        console.log('a')
    } else {
        this.label = "Start Listening"
        console.log('b')
    }
    """))

result = streamlit_bokeh_events(
    toggle_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        user_text = result.get("GET_TEXT")
        st.write(f'<script>document.getElementById("user-text").innerText = "{user_text}";</script>', unsafe_allow_html=True)

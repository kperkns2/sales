import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

st.write('<p id="user-text"></p>', unsafe_allow_html=True)

toggle_button = Button(label="Start Listening", width=100)

toggle_button.js_on_event("button_click", CustomJS(code="""
    if (this.label == "Start Listening") {
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        this.label = "Speak";
    } else {
        var u = new SpeechSynthesisUtterance();
        u.text = "You said " + document.getElementById("user-text").innerText;
        u.lang = 'en-US';
        speechSynthesis.speak(u);
        this.label = "Start Listening";
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

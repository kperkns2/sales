
import streamlit as st
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

st.write("Note: This app uses the SpeechRecognition API, which might not work on some hosted environments.")

stt_js = CustomJS(code="""
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
    """)

if st.button("Speak"):
    stt_js.execute()

result = streamlit_bokeh_events(
    None,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))

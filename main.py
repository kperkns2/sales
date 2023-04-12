
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

stt_button = Button(label="Speak", width=100)

stt_button.js_on_event("button_click", CustomJS(code="""
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
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        user_text = result.get("GET_TEXT")
        response = f"you said {user_text}"
        st.write(response)

        st.markdown(f'<p id="tts-response" style="display:none;">{response}</p>', unsafe_allow_html=True)

        st.markdown("""
            <script>
                var ttsResponse = document.getElementById("tts-response").textContent;
                var synth = window.speechSynthesis;
                var utterance = new SpeechSynthesisUtterance(ttsResponse);
                synth.speak(utterance);
            </script>
            """, unsafe_allow_html=True)


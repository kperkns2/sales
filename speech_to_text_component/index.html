import { Streamlit, ComponentMessageType } from "streamlit-component-lib";
import { useEffect } from "react";

const SpeechToText = () => {
  useEffect(() => {
    Streamlit.setFrameHeight();
  });

  const handleSpeechToText = () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      Streamlit.setComponentValue(transcript);
    };

    recognition.onspeechend = () => {
      recognition.stop();
    };
  };

  return (
    <button onClick={handleSpeechToText} type="button">
      Press and hold to speak
    </button>
  );
};

export default SpeechToText;

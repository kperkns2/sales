import { Streamlit, ComponentMessageType } from "streamlit-component-lib";
import { useEffect, useRef } from "react";

const SpeechToText = () => {
  const mediaRecorder = useRef(null);

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, []);

  const handleStartRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.current.addEventListener("dataavailable", (event) => {
      audioChunks.push(event.data);
    });

    mediaRecorder.current.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks);
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = () => {
        const base64data = reader.result;
        Streamlit.setComponentValue(base64data);
      };
    });

    mediaRecorder.current.start();
  };

  const handleStopRecording = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop();
    }
  };

  return (
    <div>
      <button onMouseDown={handleStartRecording} onMouseUp={handleStopRecording} type="button">
        Press and hold to speak
      </button>
    </div>
  );
};

export default SpeechToText;

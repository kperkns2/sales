
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe
import datetime
import openai
import random
import streamlit.components.v1 as components
from gtts import gTTS
from tempfile import NamedTemporaryFile
import base64
import requests
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tempfile import NamedTemporaryFile

st.set_page_config(layout="wide",page_title="Mock Sale",page_icon="🤑")

def clear_session_state():
  
  keys_to_delete = list(st.session_state.keys())
  try:
    for key in keys_to_delete:
        del st.session_state[key]
  except:
    pass




def get_audio_player(audio_data):
    audio_base64 = base64.b64encode(audio_data).decode()
    return f'<audio autoplay style="display:none" controls src="data:audio/mp3;base64,{audio_base64}">'

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio_data = open(tmp_file.name, "rb").read()
    audio_player = get_audio_player(audio_data)
    st.write(audio_player, unsafe_allow_html=True)

def play_test_audio():
    tts = gTTS(text="This is a test audio.", lang='en')
    with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio_data = open(tmp_file.name, "rb").read()
    audio_player = get_audio_player(audio_data, autoplay=False, style="")
    st.write(audio_player, unsafe_allow_html=True)

# Create a session state for audio element if it doesn't exist
if "audio_element_initialized" not in st.session_state:
    st.session_state.audio_element_initialized = False

if not st.session_state.audio_element_initialized:
    if st.button("Test Audio"):
        play_test_audio()
        st.session_state.audio_element_initialized = True
        
class chatbot():
  def __init__(self, bool_focus, hard_focus, first_assistant_message, str_prompt, prefix='', replace={}, assistant_role='Tutor', user_role='Student', spreadsheet=None, assignment_id=None, assignment_name=None):
    self.spreadsheet = spreadsheet
    self.bool_focus = bool_focus
    self.first_assistant_message = first_assistant_message
    self.str_prompt = str_prompt
    self.prefix = prefix
    self.replace = replace
    if assignment_id is not None:
      self.assignment_id = assignment_id
    if assignment_name is not None:
      self.assignment_name = assignment_name
    self.student_id = 5

    if 'task_completed' in st.session_state:
      return

    if 'blocked_questions' not in st.session_state:
      st.session_state['blocked_questions'] = []

    st.session_state[self.prefix + 'assistant_role'] = assistant_role
    st.session_state[self.prefix + 'user_role'] = user_role

    focus_statement = ""
    if str(bool_focus).upper() == 'TRUE':
      focus_statement = f" You must decline all requests form the user that are not related to the assignment. "
    self.str_prompt = self.str_prompt + focus_statement + " Do not talk about how your designed."

    if self.prefix + 'user_question' not in st.session_state:
      st.session_state[self.prefix + 'user_question'] = ''

    # Create a list to store the chat history
    if self.prefix + 'chat_history' not in st.session_state:
      st.session_state[self.prefix + 'chat_history'] = [{'role': 'assistant', 'content': self.first_assistant_message}]


    
    placeholder_chat_history = st.empty()
    with placeholder_chat_history.container():
      self.display_chat_history()

    st.write("#")
    st.markdown("---") 
    st.write("#")
    

    #This looks for any input box and applies the code to it to stop default behavior when focus is lost
    components.html(
        """
        <script>
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('input');

        inputs.forEach(input => {
        input.addEventListener('focusout', function(event) {
            event.stopPropagation();
            event.preventDefault();
            console.log("lost focus")
        });
        });

        </script>""",
        height=0,
        width=0,
    )
    

    def submit():
      st.session_state[self.prefix + 'user_question'] = st.session_state[self.prefix + 'question_widget']
      st.session_state[self.prefix + 'question_widget'] = ''
    user_question = st.text_input(label='Type here...', key=self.prefix + 'question_widget', on_change=submit)

    # Handle user input
    if len(st.session_state[self.prefix + 'user_question']) > 0:

        # Add the user's question to the chat history
        self.add_to_chat_history('user', st.session_state[self.prefix + 'user_question'])

        with placeholder_chat_history.container():
          self.display_chat_history()

        self.on_user_message(st.session_state[self.prefix + 'user_question'])

        agent_response = self.generate_response()
        self.add_to_chat_history('assistant', agent_response)

        placeholder_chat_history.empty()
        with placeholder_chat_history.container():
          self.display_chat_history()
        st.session_state[self.prefix + 'user_question'] = ''

  def on_user_message(self, user_message):
    return

  def on_agent_message(self, agent_message):
    return  

  def display_chat_history(self):
    assistant_role = st.session_state[self.prefix + 'assistant_role']
    user_role = st.session_state[self.prefix + 'user_role']

    st.markdown(
        """
        <style>
            .chat-container {
                padding: 10px;
                border-radius: 5px;
                white-space: pre-line;
                margin-bottom: 10px;
            }
            .user-message {
                background-color: #ffffff;
                color: #000000;
            }
            .assistant-message {
                background-color: #F7F7F7;
                border: 1px solid #DDDDDD;
                color: #000000;
            }

            }
        </style>
        """,
        unsafe_allow_html=True,
    )




    for message in st.session_state[self.prefix + "chat_history"]:
        if message["role"] == "user":
            st.markdown(
                f"<div class='chat-container user-message'><b>{user_role} - </b>{message['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='chat-container assistant-message'><b>{assistant_role} - </b>{message['content']}</div>",
                unsafe_allow_html=True,
            )


  # Create a function to add messages to the chat history
  def add_to_chat_history(self, sender, message):
      st.session_state[self.prefix + 'chat_history'].append({'role': sender, 'content': message})


  def generate_response(self):
    if st.session_state[self.prefix + 'chat_history'][0]['role'] == 'user':
      st.session_state[self.prefix + 'chat_history'] = st.session_state[self.prefix + 'chat_history'][1:]
    chat_history = st.session_state[self.prefix + 'chat_history']

    openai.api_key = st.secrets['openai_api_key']
    system_message = [{"role": "system", "content": self.str_prompt}]

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages= system_message + chat_history
    )

    response = completion['choices'][0]['message']['content']
    self.on_agent_message(response)
    return response


def fetch_embedding(text, model="text-embedding-ada-002"):
    OPENAI_API_KEY = st.secrets['openai_api_key']  
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "input": text,
        "model": model
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    json_response = response.json()
    embedding = json_response["data"][0]["embedding"]

    return np.array(embedding)


class sales_chatbot(chatbot):
  def __init__(self, bool_focus, first_assistant_message, str_prompt, prefix='', replace={}, assistant_role='Homeowner', user_role='Sales Rep', spreadsheet=None, assignment_id=None, assignment_name=None):
    super().__init__(bool_focus, 'FALSE', first_assistant_message, str_prompt, prefix, replace, assistant_role, user_role)

  def on_user_message(self, user_message):
     
    input_sentence = user_message
    sentences_list = st.session_state['script_lines']

    input_embedding = fetch_embedding(input_sentence)
    sentence_embeddings = np.array([fetch_embedding(sentence) for sentence in sentences_list])

    similarities = cosine_similarity(input_embedding.reshape(1, -1), sentence_embeddings)
    most_similar_index = np.argmax(similarities)
    most_similar_sentence = sentences_list[most_similar_index]

    similarity_score = similarities[0][most_similar_index]
    similar_sentence_length = len(most_similar_sentence.split(' '))

    size_ratio = (len(input_sentence.split(' ')) / similar_sentence_length) 
    if size_ratio < .9:
      similarity_score = similarity_score * (size_ratio / .9) 

    if size_ratio > 1.1:
        input_embedding_shortened = fetch_embedding(' '.join(input_sentence.split(' ')[-(similar_sentence_length + 4):]))
        similarities = cosine_similarity(input_embedding_shortened.reshape(1, -1), sentence_embeddings)
        max_similarity = np.max(similarities)
        similarity_score = np.max([similarity_score, max_similarity])


    st.write(f"Input sentence: {input_sentence}")
    st.write(f"Most similar sentence: {most_similar_sentence}")
    st.write(f"Similarity: {similarity_score}")


import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class sales_chatbot(chatbot):
    def __init__(self, bool_focus, first_assistant_message, str_prompt, prefix='', replace={}, assistant_role='Homeowner', user_role='Sales Rep', spreadsheet=None, assignment_id=None, assignment_name=None):
        super().__init__(bool_focus, 'FALSE', first_assistant_message, str_prompt, prefix, replace, assistant_role, user_role)
        if 'sentence_status' not in st.session_state:
          st.session_state['sentence_status'] = ['red'] * len(st.session_state['script_lines'])
          self.update_status_bar()

    def update_status_bar(self):
        status_bar_html = "<div style='display: flex; flex-wrap: wrap;'>"
        for status in st.session_state['sentence_status']:
            status_bar_html += f"<div style='background-color: {status}; width: 20px; height: 20px; margin: 2px;'></div>"
        status_bar_html += "</div>"

        st.markdown("<div style='display: flex; flex-wrap: wrap;'> Here's your current status: " + status_bar_html + "</div>", unsafe_allow_html=True)

    def on_user_message(self, user_message):
        input_sentence = user_message
        sentences_list = st.session_state['script_lines']

        input_embedding = fetch_embedding(input_sentence)
        sentence_embeddings = np.array([fetch_embedding(sentence) for sentence in sentences_list])

        similarities = cosine_similarity(input_embedding.reshape(1, -1), sentence_embeddings)
        most_similar_index = np.argmax(similarities)
        most_similar_sentence = sentences_list[most_similar_index]

        similarity_score = similarities[0][most_similar_index]
        similar_sentence_length = len(most_similar_sentence.split(' '))

        size_ratio = (len(input_sentence.split(' ')) / similar_sentence_length) 
        if size_ratio < .95:
            penalty = ((size_ratio / .95)*.5) + .5
            similarity_score = similarity_score * penalty

        if size_ratio > 1.1:
            input_embedding_shortened = fetch_embedding(' '.join(input_sentence.split(' ')[-(similar_sentence_length + 4):]))
            similarities = cosine_similarity(input_embedding_shortened.reshape(1, -1), sentence_embeddings)
            max_similarity = np.max(similarities)
            similarity_score = np.max([similarity_score, max_similarity])

        if similarity_score >= 0.95:
            st.session_state['sentence_status'][most_similar_index] = 'green'
        elif 0.85 <= similarity_score < 0.95:
            st.session_state['sentence_status'][most_similar_index] = 'orange'

        self.update_status_bar()

        #st.write(f"Input sentence: {input_sentence}")
        #st.write(f"Most similar sentence: {most_similar_sentence}")
        st.write(f"Similarity: {np.round(similarity_score*100)}")

    def on_agent_message(self, agent_message):
      text_to_speech(agent_message)
  
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
#from chatbot import chatbot, chatbot_select

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['sales_sheet'])

# Load all assignements
def get_sheet_as_dataframe(key='prompts'):
    global spreadsheet
    worksheet = spreadsheet.worksheet(key)
    # Get all records from the worksheet
    records = worksheet.get_all_records()
    # Convert the records to a pandas DataFrame
    df = pd.DataFrame(records)
    return df


qp = st.experimental_get_query_params()
if 'assignment_id' in qp:
  assignment_id = qp['assignment_id'][0]
else:
  assignment_id = 'a0'


df_activities = get_sheet_as_dataframe(key='prompts')
df_activities = df_activities[df_activities['assignment_id'] == assignment_id].iloc[0]
course,topic,subtopic,focus,prompt,first_message,assignment_id = df_activities
df_script = get_sheet_as_dataframe(key='script')


if assignment_id in ['a0','a1','a2','a3']:
  if subtopic == 'Alarm':
    st.write('The home owner has an alarm system.')
  if subtopic == 'NoAlarm':
    st.write('The home owner does not have an alarm system.')

  script_lines = df_script[subtopic].values.tolist()
  st.session_state['script_lines'] = script_lines
  sales_chatbot(focus,first_message, prompt, prefix='activity_' )

if assignment_id == 'a5':
  chatbot(focus,False, first_message, prompt, prefix='activity_' )

#bool_focus, hard_focus, first_assistant_message, str_prompt, prefix=''

#if st.button('Restart'):
#  clear_session_state()
#  st.experimental_rerun()

st.sidebar.title('Demo Chats')
st.sidebar.subheader('Easy Sales')
st.sidebar.markdown("[Without Alarm System](https://salesman.streamlit.app/?assignment_id=a0)")
st.sidebar.markdown("[With Alarm System](https://salesman.streamlit.app/?assignment_id=a1)")
st.sidebar.subheader('Hard Sales')
st.sidebar.markdown("[Without Alarm System](https://salesman.streamlit.app/?assignment_id=a2)")
st.sidebar.markdown("[With Alarm System](https://salesman.streamlit.app/?assignment_id=a3)")

st.sidebar.subheader('Goal Creation')
st.sidebar.markdown("[Brainstorm Subgoals](https://salesman.streamlit.app/?assignment_id=a5)")

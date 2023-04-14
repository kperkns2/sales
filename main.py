
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

        if self.prefix + 'backend_history' not in st.session_state:
          st.session_state[self.prefix + 'backend_history'] = [{'role': 'user', 'content': "This is a test sentence to make sure the system is working"},{'role': 'assistant', 'content': st.session_state['backend_first_message']}]

        # Add the user's question to the chat history
        self.add_to_chat_history('user', st.session_state[self.prefix + 'user_question'])

        with placeholder_chat_history.container():
          self.display_chat_history()

        agent_response = self.generate_response()
        self.add_to_chat_history('assistant', agent_response)

        placeholder_chat_history.empty()
        with placeholder_chat_history.container():
          self.display_chat_history()
        st.session_state[self.prefix + 'user_question'] = ''



  def display_chat_history(self):
    assistant_role = st.session_state[self.prefix + 'assistant_role']
    user_role = st.session_state[self.prefix + 'user_role']

    
    for message in st.session_state[self.prefix + 'chat_history']:
        if message['role'] == 'user':
            st.markdown(f"<div style='background-color: white; padding: 10px; border-radius: 5px; white-space: pre-line;'><font color='black'><b>{user_role} - </b>{message['content']}</font></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color: #F7F7F7; padding: 10px; border-radius: 5px; border: 1px solid #DDDDDD; white-space: pre-line;'><font color='black'><b>{assistant_role} - </b>{message['content']}</font></div>", unsafe_allow_html=True)


  # Create a function to add messages to the chat history
  def add_to_chat_history(self, sender, message):
      st.session_state[self.prefix + 'chat_history'].append({'role': sender, 'content': message})
      if sender == 'user':
        st.session_state[self.prefix + 'backend_history'].append({'role': sender, 'content': message})


  


  def generate_response(self):

    if len(self.str_prompt) > 2:
      system_message = [{"role": "system", "content": self.str_prompt}]

    if st.session_state[self.prefix + 'chat_history'][0]['role'] == 'user':
      st.session_state[self.prefix + 'chat_history'] = st.session_state[self.prefix + 'chat_history'][1:]
    chat_history = st.session_state[self.prefix + 'chat_history']
    backend_history = st.session_state[self.prefix + 'backend_history']


    openai.api_key = st.secrets['openai_api_key']

    backend_system_message = [{"role": "system", "content": st.session_state['backend_prompt']}]


    backend_completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages= backend_system_message + backend_history
    )
    backend_response = backend_completion['choices'][0]['message']['content']
    

    st.write(backend_system_message)
    st.write(backend_history)
    st.write(backend_response)

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages= system_message + chat_history
    )

    response = completion['choices'][0]['message']['content']

    json_command_in_response = self.get_json_command([completion['choices'][0]['message']]*2)
    if json_command_in_response is not None:
      text_to_speech(response)
    return response



import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
#from chatbot import chatbot, chatbot_select
st.set_page_config(layout="wide",page_title="Mock Sale",page_icon="🤑")

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['sales_sheet'])

# Load all assignements
def get_prompts_as_dataframe(key='prompts'):
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


df_activities = get_prompts_as_dataframe(key='prompts')
df_backend = df_activities[df_activities['assignment_id'] == 'backend'].iloc[0]
_,_,_,_,_,backend_prompt,backend_first_message,_ = df_backend
st.session_state['backend_prompt'] = backend_prompt
st.session_state['backend_first_message'] = backend_first_message


df_activities = df_activities[df_activities['assignment_id'] == assignment_id].iloc[0]
course,topic,subtopic,focus,hard_guardrail,prompt,first_message,assignment_id = df_activities


chatbot(focus, hard_guardrail, first_message, prompt, prefix='activity_' )
 
    
    

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
from chatbot import chatbot, chatbot_select
st.set_page_config(layout="wide",page_title="Mock Sale",page_icon="🤑")

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['sales_sheet'])

# Load all assignements
@st.cache_data
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
df_activities = df_activities[df_activities['assignment_id'] == assignment_id].iloc[0]
course,topic,subtopic,focus,hard_guardrail,prompt,first_message,assignment_id = df_activities
chatbot(focus, hard_guardrail, first_message, prompt, prefix='activity_' )
 
    
    

import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
import json
import os
import pyperclip
import urllib3

# Define the required scopes for Google Forms API
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_file_paths():
    credentials_path = os.environ.get('CREDENTIALS_PATH', 'client_secret.json')
    token_path = os.path.join(os.path.dirname(credentials_path), 'token.json')
    return credentials_path, token_path
    
def authenticate():
    creds = None
    
    # Get credentials from st.secrets
    client_id = st.secrets["web"]["client_id"]
    client_secret = st.secrets["web"]["client_secret"]
    s_url = st.secrets["web"]["streamlit_url"]

    # Define the path to the token file
    token_path = 'token.json'

# Check if token file exists
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except ValueError as e:
            st.error(f"Error loading credentials: {str(e)}")
            os.remove(token_path)  # Remove the invalid token file
            creds = None

    # If creds are not valid, authenticate and refresh
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use client_id and client_secret from st.secrets to authenticate
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": st.secrets["web"]["auth_uri"],
                        "token_uri": st.secrets["web"]["token_uri"],
                        "redirect_uris": 'https://idealistraj9-magic-form-main-nh0ojs.streamlit.app',
                        "scopes": SCOPES,
                    }
                },
                SCOPES
            )
            flow.redirect_uri = 'https://idealistraj9-magic-form-main-nh0ojs.streamlit.app'

            # Redirect user to authorization page
            authorization_url, _ = flow.authorization_url()
            
            # Show the authorization URL to the user
            st.write(f"[Click here to authorize]({authorization_url})")

            # Wait for the user to authorize and be redirected back to the app
            # Get the code parameter from the URL
            query_params = st.experimental_get_query_params()
            code = query_params.get("code")
            
            if code:
                code = code[0]  # Get the first value in the list, as it is stored in a list
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # Save the credentials to the token file
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
            else:
                st.error("Authorization code not found in the URL.")
                creds = None
    return creds


def load_questions_from_json(file_obj):
    data = json.load(file_obj)
    return data['questions']

def create_forms_service(creds):
    service = build('forms', 'v1', credentials=creds)
    return service

def create_new_form(service, title):
    form = {
        'info': {
            'title': title
        }
    }
    created_form = service.forms().create(body=form).execute()
    form_id = created_form['formId']
    form_url = created_form['responderUri']
    
    batch_update_body = {
        'requests': [{
            'updateSettings': {
                'updateMask': 'quizSettings.isQuiz',
                'settings': {
                    'quizSettings': {
                        'isQuiz': True
                    }
                }
            }
        }]
    }
    service.forms().batchUpdate(formId=form_id, body=batch_update_body).execute()
    return form_id, form_url

def edit_form(service, form_id, questions):
    batch_update_body = {
        'requests': []
    }

    # Add each question to the form
    for i, question in enumerate(questions):
        if 'title' not in question:
            st.write(f"Skipping question at index {i} due to missing 'title'")
            continue
        
        # Construct a request to create each question in the form
        item_request = {
            'createItem': {
                'item': {
                    'title': question['title'],
                    'questionItem': {
                        'question': {
                            'required': question.get('required', True)
                        }
                    }
                },
                'location': {
                    'index': i
                }
            }
        }
        
        # Add question type and options if needed
        question_type = question.get('type', '').upper()
        options = question.get('options')
        if question_type == 'RADIO':
            item_request['createItem']['item']['questionItem']['question']['choiceQuestion'] = {'type': 'RADIO', 'options': [{'value': option} for option in options]}
            # Assign points and correct answers if it is a quiz question
            correct_answer = question.get('correct')
            if correct_answer:
                for option in item_request['createItem']['item']['questionItem']['question']['choiceQuestion']['options']:
                    option['isCorrect'] = (option['value'] == correct_answer)
                item_request['createItem']['item']['questionItem']['question']['grading'] = {'correctAnswers': [{'value': correct_answer}], 'points': 1}
        elif question_type == 'CHECKBOX':
            item_request['createItem']['item']['questionItem']['question']['choiceQuestion'] = {'type': 'CHECKBOX', 'options': [{'value': option} for option in options]}
        elif question_type == 'DROPDOWN':
            item_request['createItem']['item']['questionItem']['question']['dropdownQuestion'] = {'options': [{'value': option} for option in options]}
        elif question_type == 'TEXT':
            item_request['createItem']['item']['questionItem']['question']['textQuestion'] = {}
        
        # Add the request to the batch
        batch_update_body['requests'].append(item_request)

    # Execute the batch update request
    service.forms().batchUpdate(formId=form_id, body=batch_update_body).execute()
    st.write("Questions added to the form.")

def display_instructions():
    st.header("Magic - Form Creator 🪄")
    st.write("How to Use This App")
    st.markdown("""
    1. **Create Form**:
        - Provide a title for your form.
        - A new form will be created in your Google account.

    2. **Upload Questions**:
        - Upload a JSON file containing the questions to add to the form.
        - The JSON file must follow this format:
    """)
    
    default_json_format = """{
  "questions": [
    {
      "title": "What is DevOps?",
      "type": "RADIO",
      "options": [
        "A programming language",
        "A set of practices that combines software development and IT operations",
        "A type of database"
      ],
      "required": true
    },
    {
      "title": "Which tool is commonly used for version control in DevOps?",
      "type": "RADIO",
      "options": ["Git", "Excel", "Java"],
      "required": true
    }
  ]
}
"""
    # Display the default JSON format and provide a copy button
    st.code(default_json_format, language="json")
    if st.button("Copy JSON Format"):
        pyperclip.copy(default_json_format)
        st.success("JSON format copied to clipboard!")

def inject_custom_css():
    # Define custom CSS styles
    custom_css = """
    <style>
    /* Customize the Streamlit app */
    body {
        background-image: url('./back.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    /* Customize headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1e73df;
    }
    /* Customize button */
    button, .stButton>button {
        background-color: #4e73df;
        color: #fff;
        border-radius: 5px;
    }
    </style>
    """

    # Inject the custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)

def main():
    # Inject custom CSS into the app
    inject_custom_css()
    
    # Display app instructions
    display_instructions()
    
    # Title of the application
    st.title("Create Google Form")
    
    # Authenticate and create Google Forms API service
    creds = authenticate()
    service = create_forms_service(creds)
    
    # Get the form title from user input
    form_title = st.text_input("Enter the form title")
    
    # Allow the user to upload a questions JSON file
    questions_file = st.file_uploader("Upload questions JSON file", type=["json"])
    
    # If the user clicks the button to create the form
    if st.button("Create Form & Wait For Magic 😉"):
        if form_title and questions_file:
            questions = load_questions_from_json(questions_file)
            form_id, form_url = create_new_form(service, form_title)
            edit_form(service, form_id, questions)
            st.success(f"Form created with ID: {form_id}")
            st.success(f"Form URL: {form_url}")
        else:
            st.error("Please enter the form title and upload the questions JSON file.")

if __name__ == '__main__':
    main()
#25311
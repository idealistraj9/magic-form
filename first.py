from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import os

# Define the required scopes for Google Forms API
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_file_paths():
    # Prompt the user for the path to the client_secret.json file
    credentials_path = "client_secret.json"
    # Define the token file path based on the credentials path
    token_path = os.path.join(os.path.dirname(credentials_path), 'token.json')
    return credentials_path, token_path

def authenticate():
    # Retrieve the port number from the user input (default is 8000)
    port = int(input("Enter the port number to use for authentication (default: 8000): ") or 8000)
    
    print("Authenticating...")
    creds = None
    credentials_path, token_path = get_file_paths()
    
    # Load existing credentials if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Authenticate if no valid credentials exist
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Create the flow and specify the port number
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=port)

        # Save the credentials for future use
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
    
    print("Authentication successful!")
    return creds

def load_questions_from_json():
    # Define the path to the question.json file
    json_file_path = 'questions.json'
    
    # Load the data from the JSON file
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    return data['questions']

def create_forms_service(creds):
    service = build('forms', 'v1', credentials=creds)
    return service

def create_new_form(service):
    # Ask the user for the title of the form
    title = input("Enter the title of the form: ")
    
    # Create the form with only the title
    form = {
        'info': {
            'title': title
        }
    }
    created_form = service.forms().create(body=form).execute()
    form_id = created_form['formId']
    form_url = created_form['responderUri']
    
    # Update the form settings to enable quiz mode
    # This is the correct format for the batch update request to set quiz settings
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
    
    # Execute the batch update request to set the form as a quiz
    service.forms().batchUpdate(formId=form_id, body=batch_update_body).execute()
    
    return form_id, form_url


def edit_form(service, form_id, questions):
    batch_update_body = {
        'requests': []
    }

    # Add each question to the form
    for i, question in enumerate(questions):
        if 'title' not in question:
            print(f"Skipping question at index {i} due to missing 'title'")
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

def main():
    # Authenticate the script and create the Google Forms API service
    creds = authenticate()
    service = create_forms_service(creds)
    
    # Create a new form and retrieve its ID and URL
    form_id, form_url = create_new_form(service)
    print(f'Form created with ID: {form_id}')
    print(f'Form URL: {form_url}')
    
    # Load questions from the specified JSON file (questions.json)
    questions = load_questions_from_json()
    
    # Edit the form with the loaded questions
    edit_form(service, form_id, questions)
    print('Questions added to the form.')

if __name__ == '__main__':
    main()
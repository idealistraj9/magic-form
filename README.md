Magic Form Creator 🪄
Magic Form Creator is a Streamlit web application that allows users to create Google Forms with ease. With this tool, you can define your form title and upload a JSON file containing the questions you want to add to the form. The application then handles the creation of the form in your Google account using the Google Forms API.

Features
Create a new Google Form with a custom title.
Upload questions from a JSON file to add to the form.
Supports various question types including Radio, Checkbox, Dropdown, and Text.
Automatically sets up quiz settings if the questions include correct answers.
Getting Started
To get started with Magic Form Creator, follow these steps:

Clone this repository to your local machine.
Install the required dependencies by running pip install -r requirements.txt.
Set up your Google Cloud project and obtain OAuth 2.0 client credentials.
Create a client_secret.json file with your OAuth 2.0 client credentials.
Create a secrets.toml file containing your Streamlit secrets, including web.client_id, web.client_secret, and web.streamlit_url.
Run the Streamlit application by executing streamlit run main.py.
Follow the instructions on the web application to authenticate with Google and create your form.
Dependencies
Streamlit
Google APIs Client Library
Google Auth OAuthlib
Pyperclip (for copying JSON format)
Contributing
Contributions to Magic Form Creator are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Magic Form Creator 🪄</title>
</head>
<body>

  <h1>Magic Form Creator 🪄</h1>

  <p>Magic Form Creator is a Streamlit web application that allows users to create Google Forms with ease. With this tool, you can define your form title and upload a JSON file containing the questions you want to add to the form. The application then handles the creation of the form in your Google account using the Google Forms API.</p>

  <h2>Features</h2>

  <ul>
    <li>Create a new Google Form with a custom title.</li>
    <li>Upload questions from a JSON file to add to the form.</li>
    <li>Supports various question types including Radio, Checkbox, Dropdown, and Text.</li>
    <li>Automatically sets up quiz settings if the questions include correct answers.</li>
  </ul>

  <h2>Getting Started</h2>

  <ol>
    <li>Clone this repository to your local machine.</li>
    <li>Install the required dependencies by running <code>pip install -r requirements.txt</code>.</li>
    <li>Set up your Google Cloud project and obtain OAuth 2.0 client credentials.</li>
    <li>Create a <code>client_secret.json</code> file with your OAuth 2.0 client credentials.</li>
    <li>Create a <code>secrets.toml</code> file containing your Streamlit secrets, including <code>web.client_id</code>, <code>web.client_secret</code>, and <code>web.streamlit_url</code>.</li>
    <li>Run the Streamlit application by executing <code>streamlit run main.py</code>.</li>
    <li>Follow the instructions on the web application to authenticate with Google and create your form.</li>
  </ol>

  <h2>Dependencies</h2>

  <ul>
    <li>Streamlit</li>
    <li>Google APIs Client Library</li>
    <li>Google Auth OAuthlib</li>
    <li>Pyperclip (for copying JSON format)</li>
  </ul>

  <h2>Contributing</h2>

  <p>Contributions to Magic Form Creator are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.</p>

  <h2>License</h2>

  <p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for details.</p>

</body>
</html>

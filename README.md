# Google Blogger AI

This project integrates with the Google Blogger API to manage blog posts.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/usmanmughalji/google-blogger-ai.git
    cd google-blogger-ai
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install Flask google-api-python-client google-auth-oauthlib google-auth-httplib2
    ```

4.  **Google Cloud Project Configuration:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   Enable the "Blogger API" and "Google People API" for your project.
    *   Go to "APIs & Services" > "OAuth consent screen".
        *   Configure your OAuth consent screen. For testing, you can set the "User type" to "External" and "Publishing status" to "Testing". Add your Google account as a "test user".
    *   Go to "APIs & Services" > "Credentials".
        *   Create "OAuth client ID" credentials. Choose "Web application" as the application type.
        *   Add `http://localhost:5000` and `http://localhost:5000/oauth2callback` to "Authorized redirect URIs".
        *   Download the client configuration JSON file and rename it to `client_secret.json`. Place this file in the root directory of your project (where `app.py` is located).

## Running the Application

1.  **Start the Flask backend server:**
    ```bash
    python app.py
    ```

2.  **Open your browser:**
    Navigate to `http://localhost:5000` to access the application.

## Usage

*   Click "Authorize with Google" to authenticate with your Google account and grant access to your Blogger data.
*   Once authorized, you can select a blog, load existing posts, and create new posts.

## Technologies Used

*   **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
*   **Backend:** Python (Flask)
*   **API:** Google Blogger API

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests.

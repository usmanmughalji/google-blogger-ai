import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Configuration for Google API
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "blogger_token.pickle" # Token file for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# This is for development only, allowing OAuth 2.0 to work over HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def generate_token():
    credentials = None

    # Load existing credentials if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing existing token...")
            credentials.refresh(Request())
        else:
            print("No valid token found. Initiating new authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            # Use a fixed port for the redirect URI to avoid mismatch issues
            credentials = flow.run_local_server(port=8080, open_browser=True)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)
        print(f"Token saved to {TOKEN_FILE}")
    else:
        print("Valid token already exists.")

    return credentials

if __name__ == '__main__':
    print("Running token generation script...")
    generate_token()
    print("Token generation process complete. You can now run app.py.")

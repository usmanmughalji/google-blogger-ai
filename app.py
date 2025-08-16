from flask import Flask, request, redirect, url_for, session, jsonify, send_from_directory
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24) # Replace with a strong, unique key in production

# This is for development only, allowing OAuth 2.0 to work over HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configuration for Google API
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "blogger_token.pickle" # Token file for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Ensure client_secrets.json exists
if not os.path.exists(CLIENT_SECRETS_FILE):
    print(f"Error: {CLIENT_SECRETS_FILE} not found. Please download it from Google Cloud Console.")
    exit()

# Function to get credentials from the pickle file
def get_credentials():
    credentials = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Save refreshed credentials
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(credentials, token)
        else:
            # If no valid credentials, or refresh failed, indicate unauthorized
            return None
    return credentials

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Remove /authorize and /oauth2callback routes as token generation is external

@app.route('/get_blogs')
def get_blogs():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authorized. Please run generate_blogger_token.py first."}), 401

    service = build('blogger', 'v3', credentials=creds)

    try:
        blogs = service.blogs().listByUser(userId='self').execute()
        return jsonify(blogs)
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({"error": str(e)}), 500

@app.route('/get_posts/<blog_id>')
def get_posts(blog_id):
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authorized. Please run generate_blogger_token.py first."}), 401

    service = build('blogger', 'v3', credentials=creds)

    try:
        posts = service.posts().list(blogId=blog_id).execute()
        return jsonify(posts)
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({"error": str(e)}), 500

@app.route('/create_post/<blog_id>', methods=['POST'])
def create_post(blog_id):
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authorized. Please run generate_blogger_token.py first."}), 401

    service = build('blogger', 'v3', credentials=creds)

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    post_body = {
        'kind': 'blogger#post',
        'blog': {'id': blog_id},
        'title': title,
        'content': content
    }

    try:
        new_post = service.posts().insert(blogId=blog_id, body=post_body).execute()
        return jsonify(new_post)
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

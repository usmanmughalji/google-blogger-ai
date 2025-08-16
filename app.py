from flask import Flask, request, redirect, url_for, session, jsonify, send_from_directory
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24) # Replace with a strong, unique key in production

# This is for development only, allowing OAuth 2.0 to work over HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configuration for Google API
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Ensure client_secrets.json exists
if not os.path.exists(CLIENT_SECRETS_FILE):
    print(f"Error: {CLIENT_SECRETS_FILE} not found. Please download it from Google Cloud Console.")
    exit()

# Initialize the OAuth 2.0 flow
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES,
    redirect_uri='http://localhost:5000/oauth2callback'
)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/authorize')
def authorize():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Ensure the state parameter is present in the request URL for security
    if 'state' not in request.args:
        return jsonify({"error": "State parameter missing in callback"}), 400

    # The flow.fetch_token method will automatically validate the state
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    # Clean up the state from the session after successful token fetch
    session.pop('state', None)
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    # Redirect back to the main page with a success indicator
    return redirect(url_for('index', auth_success='true'))

@app.route('/get_blogs')
def get_blogs():
    if 'credentials' not in session:
        return jsonify({"error": "Not authorized"}), 401

    credentials = Credentials(**session['credentials'])
    service = build('blogger', 'v3', credentials=credentials)

    try:
        blogs = service.blogs().listByUser(userId='self').execute()
        return jsonify(blogs)
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({"error": str(e)}), 500

@app.route('/get_posts/<blog_id>')
def get_posts(blog_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authorized"}), 401

    credentials = Credentials(**session['credentials'])
    service = build('blogger', 'v3', credentials=credentials)

    try:
        posts = service.posts().list(blogId=blog_id).execute()
        return jsonify(posts)
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({"error": str(e)}), 500

@app.route('/create_post/<blog_id>', methods=['POST'])
def create_post(blog_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authorized"}), 401

    credentials = Credentials(**session['credentials'])
    service = build('blogger', 'v3', credentials=credentials)

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

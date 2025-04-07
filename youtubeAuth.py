from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# Define the OAuth 2.0 scope for full YouTube access
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_channel_info(youtube):
    request = youtube.channels().list(
        part="snippet,statistics",
        mine=True  # Get the authenticated user's channel
    )
    response = request.execute()
    print(response)
def get_youtube_client():
    """Load stored credentials or re-authenticate."""
    try:
        with open("token.pickle", "rb") as token_file:
            credentials = pickle.load(token_file)
        return build("youtube", "v3", credentials=credentials)
    except Exception:
        return authenticate_youtube()
def authenticate_youtube():
    """Authenticate and return a YouTube API client."""
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )
    credentials = flow.run_local_server(port=0)

    # Save credentials for future use
    with open("token.pickle", "wb") as token_file:
        pickle.dump(credentials, token_file)

    return build("youtube", "v3", credentials=credentials)

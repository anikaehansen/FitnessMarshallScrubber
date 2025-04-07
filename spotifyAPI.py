import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import json
import requests
import os
import time
def spotify_artist_get(song_dict):
    with open('spotify_client.json', 'r') as file:
        data = json.load(file)
        CLIENT_ID = data['client_id']
        CLIENT_SECRET = data['client_secret']
    CACHE_PATH = '.cache_token.json'  # This file will store the token data
    # Function to load token from file or None if not found
    def load_token():
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, 'r') as file:
                token_info = json.load(file)
                if token_info['expires_at'] > time.time():
                    return token_info
                else:
                    return None
        return None

    # Function to save token to file
    def save_token(token_info):
        with open(CACHE_PATH, 'w') as file:
            json.dump(token_info, file)

    # Function to get a new access token (if no valid token is found or it needs to be refreshed)
    def get_token():
        token_info = load_token()
        if not token_info:
            sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri='https://example.com/callback',
                            scope="user-library-read user-top-read",  # Define necessary scope
                                    cache_path=CACHE_PATH)
            token_info = sp_oauth.get_cached_token()

            if not token_info:
                print("Please visit this URL to authorize the app:")
                auth_url = sp_oauth.get_authorize_url()
                print(auth_url)
                response = input("Paste the full redirect URL here: ")
                token_info = sp_oauth.get_access_token(response)

            save_token(token_info)
        return token_info

    # Get or refresh token
    token_info = get_token()
    access_token = token_info['access_token']

    access_token = token_info['access_token']

    # Now use the access token to authenticate the API
    sp = spotipy.Spotify(auth=access_token)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    for url, songs in song_dict.items():
        for i in range(1, len(songs)):  # Skip the first item (list title)
            song_title = songs[i]
            result = sp.search(song_title, limit=1)
            if result['tracks']['items']:
                track = result['tracks']['items'][0]
                artist_name = [artist['name'] for artist in track['artists']]  # Get all artist names

            else:
                artist_name = 'Unknown'  # Handle cases where no artist is found
            songs[i] = [song_title, artist_name]
    return song_dict
import requests
from bs4 import BeautifulSoup
import re
import asyncio
from youtubeAuth import get_channel_info, get_youtube_client
from musicScrubber import get_playlist_videos, process_playlist_and_filter_comments, isolate_songs_from_comments
from spotifyAPI import spotify_artist_get
from yTposts import YT_Posts

# Authenticate and create YouTube API client
youtube = get_youtube_client()
filtered_comments = process_playlist_and_filter_comments('PLgcveAkQOd-swcmlzntTcrLGsEQYtv2Vk', youtube)
filtered_song_dict = isolate_songs_from_comments(filtered_comments)
full_song_dict = spotify_artist_get(filtered_song_dict)

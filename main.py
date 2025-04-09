"""Processes YouTube playlist and outputs song, artist, video dictionary

Calls all other functions from other files.
Authenticates YouTube, then processes every video of the playlist by
searching comments for official comment that lists the song titles and timestamps.
Cleans the comments for just the song titles, removing extra comments and timestamps.
Uses Spotify API to pull artist from the song titles. Creates dictionary of
video title, video link, list of songs and artists.

"""
from youtubeAuth import get_channel_info, get_youtube_client
from musicScrubber import (
    get_playlist_videos,
    process_playlist_and_filter_comments,
    isolate_songs_from_comments,
)
from spotifyAPI import spotify_artist_get


def main():
    # Authenticate and create YouTube API client
    youtube = get_youtube_client()
    filtered_comments = process_playlist_and_filter_comments(
        "PLgcveAkQOd-swcmlzntTcrLGsEQYtv2Vk", youtube
    )
    filtered_song_dict = isolate_songs_from_comments(filtered_comments)
    full_song_dict = spotify_artist_get(filtered_song_dict)
    # TODO: Create json from dictionary and intergrate with ability to search front-end

if __name__ == "__main__":
    main()

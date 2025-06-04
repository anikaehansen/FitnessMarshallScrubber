"""Returns list of songs per video using Official comment

Using authenticated Youtube instance, gets video urls and titles in the requested playlist.
For each video in the playlist, finds comment from uploader and confirms it has a regex that matches the
 timestamp : song format.
Isolates only the songs from the comment, ensures no extra comments, or words are included, and adds those songs to
a dictionary, associated with the video url and title.

"""

import googleapiclient.discovery
import os
import re


def get_playlist_videos(playlist_id: str, youtube):
    # Request for playlist items
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50,  # You can adjust this number or handle pagination
    )

    response = request.execute()
    videos = []
    video_urls = []
    for item in response["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append(
            {
                "video_id": video_id,
                "video_url": video_url,
                "title": item["snippet"]["title"],
            }
        )
        video_urls.append(video_url)
    return videos, video_urls


# Main function to process videos in a playlist
def get_video_comments(video, youtube):
    comments = []
    next_page_token = None
    video_id = video["video_id"]
    video_title = video["title"]
    while True:
        # Fetch comment threads for the video
        request = youtube.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=100, pageToken=next_page_token
        )
        response = request.execute()

        # Process each comment
        for item in response["items"]:
            comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
            author = comment_snippet["authorDisplayName"]
            comment_text = comment_snippet["textDisplay"]
            user_name = "@TheFitnessMarshall"
            # Filter comments by specific user and text "0:"
            if author == user_name and "0:" in comment_text:
                comment_info = {
                    "author": author,
                    "comment": comment_text,
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": video_title,
                }
                comments.append(comment_info)

        # Check if there are more comments
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


# Main function to process the playlist and filter comments
def process_playlist_and_filter_comments(playlist_id: str, youtube) -> list:
    # Step 1: Get videos from the playlist
    videos_in_playlist, video_urls_in_playlist = get_playlist_videos(
        playlist_id, youtube
    )

    # Step 2: Get and filter comments for each video
    all_filtered_comments = []
    for video in videos_in_playlist:
        try:
            comments = get_video_comments(video, youtube)
            all_filtered_comments.extend(comments)
        except:
            pass

    return all_filtered_comments


# Get the filtered comments
def isolate_songs_from_comments(filtered_comments: list) -> dict:
    song_dict = {}
    pattern = r'">.*?<\/a>\s*([^<]+)'
    exclude_words = ["Stream", "WATERBREAK"]
    for comment in filtered_comments:
        song_list = re.findall(pattern, comment["comment"])
        for idx, song in enumerate(song_list):
            # If "Stretch" is found in the song name, update the song name
            if "Stretch" in song:
                stretch_pattern = r"Stretch \((.*)\)"  # Pattern to capture the text inside parentheses
                match = re.search(stretch_pattern, song)
                if match:
                    # Replace the song name with the match inside parentheses
                    song_list[idx] = match.group(
                        1
                    )  # Update the song name to only the content inside parentheses
            song_list[idx] = song_list[idx].replace("&#39;", "'").replace("&amp;", "&")
            song_list[idx] = song_list[idx].split(" - ")[0].strip()

        # Filter the song list: remove songs that are empty/only spaces or contain words in the exclude_words list
        filtered_song_list = [
            song
            for song in song_list
            if song.strip()
            and not any(
                exclude_word.lower() in song.lower() for exclude_word in exclude_words
            )
            and song != "Open "
            and song != "Open"
        ]
        filtered_song_list.insert(0, comment["title"])
        song_dict[comment["video_url"]] = filtered_song_list
    song_dictionary = song_dict
    return song_dictionary

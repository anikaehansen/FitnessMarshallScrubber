import re
import copy
import json
import pickle
import time
import hashlib
import os
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
class YT_Posts:
    def __init__(self) -> None:
        self.youtube = self.get_youtube_client()
        self.build_headers()

    def get_youtube_client(self):
        """Load stored credentials or re-authenticate."""
        try:
            with open("token.pickle", "rb") as token_file:
                credentials = pickle.load(token_file)

            # Ensure credentials are still valid, refreshing if needed
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            return build("youtube", "v3", credentials=credentials)
        except Exception:
            return self.authenticate_youtube()

    def authenticate_youtube(self):
        """Authenticate and return a YouTube API client."""
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", SCOPES
        )
        credentials = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pickle", "wb") as token_file:
            pickle.dump(credentials, token_file)

        return build("youtube", "v3", credentials=credentials)

    def build_headers(self):
        """Extract OAuth token from credentials and set headers."""
        if not self.youtube or not self.youtube._http.credentials:
            print("YouTube client or credentials missing!")
            return

        access_token = self.youtube._http.credentials.token

        if not access_token:
            print("Failed to retrieve access token!")
            return

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

    def refresh_token(self):
        """Refresh the OAuth token if expired."""
        if self.youtube._http.credentials.expired and self.youtube._http.credentials.refresh_token:
            self.youtube._http.credentials.refresh(Request())
            self.build_headers()
    @staticmethod
    def combineText(text_dict: dict) -> str:
        text = ""
        for each_text in text_dict:
            text += each_text["text"]
        return text

    def cleanUpPostResults(self, post_dict: dict) -> dict:
        result_dict = {
            "postParams": None,
            "postId": None,
            "text": None,
            "images": None,
            "videos": None,
            "polls": None
        }
        
        if "backstagePostThreadRenderer" not in post_dict.keys():
            return False

        post_dict = post_dict["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]

        result_dict["postId"] = post_dict["postId"]
        result_dict["postParams"] = post_dict["publishedTimeText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["params"]

        # Join all texts
        result_dict["text"] = self.combineText(post_dict["contentText"]["runs"])

        # Clean up attachments (polls, single images, image gallery, videos)
        if "backstageAttachment" in post_dict.keys():
            images = []
            
            # Single Image
            if "backstageImageRenderer" in post_dict["backstageAttachment"].keys():
                images.append(post_dict["backstageAttachment"]["backstageImageRenderer"]["image"]["thumbnails"][-1])

            # Multi Image
            if "postMultiImageRenderer" in post_dict["backstageAttachment"].keys():
                for each_image in post_dict["backstageAttachment"]["postMultiImageRenderer"]['images']:
                    images.append(each_image["backstageImageRenderer"]["image"]["thumbnails"][-1])

            result_dict["images"] = images

            # Videos
            videos = {}
            if "videoRenderer" in post_dict["backstageAttachment"].keys():
                videos["text"] = self.combineText(post_dict["backstageAttachment"]["videoRenderer"]["title"]["runs"])
                videos["videoId"] = post_dict["backstageAttachment"]["videoRenderer"]["videoId"]
            result_dict["videos"] = videos

            # Polls
            polls = {
                "choices": [],
                "totalVotes": 0
            }
            
            if "pollRenderer" in post_dict["backstageAttachment"].keys():
                choices = []
                for each_choice in post_dict["backstageAttachment"]["pollRenderer"]["choices"]:
                    choice_dict = {}
                    choice_dict["text"] = self.combineText(each_choice["text"]["runs"])
                    # Field doesn't exist if you haven't voted
                    if "numVotes" in each_choice:
                        choice_dict["numVotes"] = each_choice["numVotes"]
                        choice_dict["votePercentage"] = each_choice["votePercentage"]["simpleText"]
                    else:
                        choice_dict["numVotes"] = 0
                        choice_dict["votePercentage"] = each_choice["votePercentageIfNotSelected"]["simpleText"] #Assume false if haven't voted
                    choices.append(choice_dict)
                polls["choices"] = choices
                polls["totalVotes"] = post_dict["backstageAttachment"]["pollRenderer"]["totalVotes"]["simpleText"]
            result_dict["polls"] = polls

        return result_dict
        
    def cleanUpCommentResults(self, comment_dict: dict, reply: bool) -> dict:
        result_dict = {
            "commentId": None,
            "authorName": None,
            "commentText": None,
            "emojis": None,
            "replyToken": None,
            "replyCount": None,
        }   
        
        if not reply and "commentThreadRenderer" not in comment_dict.keys():
            return False

        if not reply and "replies" in comment_dict["commentThreadRenderer"].keys():
            result_dict['replyToken'] = comment_dict["commentThreadRenderer"]["replies"]["commentRepliesRenderer"]["contents"][0]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
            result_dict['replyCount'] = comment_dict["commentThreadRenderer"]["comment"]["commentRenderer"]["replyCount"]

        if not reply:
            comment_dict = comment_dict["commentThreadRenderer"]["comment"]["commentRenderer"]
        else:
            comment_dict = comment_dict["commentRenderer"]

        result_dict["commentId"] = comment_dict["commentId"]

        result_dict["authorName"] = comment_dict["authorText"]["simpleText"]
        result_dict["commentText"] = self.combineText(comment_dict["contentText"]["runs"])

        emojis = []
        for text in comment_dict["contentText"]["runs"]:
            if "emoji" in text.keys():
                emojis.append({
                    "emojiName": text["text"],
                    "emojiUrl": text["emoji"]["image"]["thumbnails"][-1]["url"]
                })

        result_dict["emojis"] = emojis
        return result_dict

    def get_channel_id_from_handle(self, handle: str) -> str:
        """Fetch the YouTube channel ID from a username (handle)."""
        try:
            # Make sure to remove '@' from the handle
            response = self.youtube.channels().list(
                part="id",
                forUsername=handle.lstrip('@')  # Strip the '@' symbol
            ).execute()

            # Check if we got the channel data
            if 'items' in response and response['items']:
                return response['items'][0]['id']  # Return the first result

            print(f"❌ No channel found for handle: {handle}")
            return None
        except Exception as e:
            print(f"❌ Error fetching channel ID: {str(e)}")
            return None

    def fetchPosts(self, channel_id: str, limit: int = 10):
        channel_id = self.get_channel_id_from_handle(channel_id)
        if not channel_id:
            print(f"❌ Could not fetch channel ID for {channel_id}")
            return []

        try:
            # Fetch posts from the Community tab via activities API
            json_data = {
                'context': {
                    'client': {
                        'clientName': 'WEB',
                        'clientVersion': '2.20240731.04.00',
                    },
                },
            }

            response = requests.post('https://www.youtube.com/youtubei/v1/browse', json=json_data)

            print(response)  # Check if the response format is what you expect

            # Extract Community posts (adjust based on response structure)
            if "contents" in response and "twoColumnBrowseResultsRenderer" in response["contents"]:
                community_posts = [
                    item for item in response["contents"]["twoColumnBrowseResultsRenderer"].get("tabs", [])
                    if item.get("tabRenderer", {}).get("title") == "Community"
                ]
                print(f"✅ Successfully fetched {len(community_posts)} posts")
                return community_posts
            else:
                print("❌ No community posts found.")
                return []

        except Exception as e:
            print(f"❌ Error fetching posts: {str(e)}")
            return []
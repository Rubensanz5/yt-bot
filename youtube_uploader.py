import os
import json
import pickle
import random
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import YOUTUBE_CLIENT_SECRET

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

TITLE_TEMPLATES = [
    "Is This Illegal? {topic}",
    "You Can Get in Trouble for This… ({topic})",
    "Don't Do This… It's Illegal ({topic})",
    "This Can Cost You Thousands ({topic})",
]

DESCRIPTION = """Learn your legal rights in simple terms. No confusing jargon, just straight facts.

⚖️ On this channel:
- Laws explained simply
- Legal tips you actually need
- Rights you should know before it's too late

🔔 Subscribe and hit the bell so you never miss an update.

⚠️ Disclaimer: This video is for educational purposes only and does not constitute legal advice. Always consult a licensed attorney for your specific situation."""

TAGS = [
    "legal rights explained",
    "is it illegal",
    "law explained",
    "legal tips",
    "know your rights",
    "legal advice",
    "rights unlocked",
    "law simplified",
    "legal education",
    "your rights",
]

def generate_title(topic):
    return random.choice(TITLE_TEMPLATES).format(topic=topic)

def authenticate_youtube():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)

def upload():
    with open("current_script.txt") as f:
        lines = f.readlines()

    topic = lines[0].replace("TOPIC: ", "").strip()
    if len(lines) > 1 and lines[1].startswith("TITLE:"):
        title = lines[1].replace("TITLE: ", "").strip()
    else:
        title = generate_title(topic)

    description = DESCRIPTION
    tags = TAGS
    if os.path.exists("current_metadata.json"):
        with open("current_metadata.json", encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", title)
        description = meta.get("description", description)
        tags = meta.get("tags", tags)

    youtube = authenticate_youtube()

    print(f"Uploading: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "27",
            },
            "status": {"privacyStatus": "public"},
        },
        media_body=MediaFileUpload("final_video.mp4", resumable=True),
    )

    response = request.execute()
    video_id = response["id"]
    print(f"Video uploaded: https://youtube.com/watch?v={video_id}")

    if os.path.exists("thumbnail.png"):
        print("Uploading thumbnail...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload("thumbnail.png"),
        ).execute()
        print("Thumbnail uploaded.")

    return video_id

if __name__ == "__main__":
    upload()

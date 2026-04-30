# shorts_creator.py + uploader
import requests
import os
import json
import pickle
import random
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, ColorClip
from PIL import Image, ImageDraw, ImageFont
import textwrap
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import PEXELS_API_KEY, YOUTUBE_CLIENT_SECRET

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

SHORTS_DESCRIPTION = """Know your legal rights in 60 seconds!

Follow for daily legal tips that could save you thousands.

Educational purposes only. Not legal advice."""

SHORTS_TAGS = [
    "shorts", "legal shorts", "law shorts", "know your rights",
    "is it illegal", "legal tips", "rights explained", "law facts"
]

def download_pexels_vertical_videos(num_videos=4):
    """Descarga videos verticales de Pexels para Shorts"""
    print("Downloading vertical videos from Pexels...")

    keywords = ["law", "court", "justice", "lawyer", "legal"]
    random.shuffle(keywords)

    os.makedirs("temp_shorts", exist_ok=True)
    video_files = []

    for keyword in keywords:
        if len(video_files) >= num_videos:
            break

        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=3&orientation=portrait"

        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            for video in data.get("videos", []):
                if len(video_files) >= num_videos:
                    break

                video_files_list = video["video_files"]
                best = next((v for v in video_files_list if v["quality"] == "hd"), video_files_list[0])

                video_path = f"temp_shorts/short_clip_{len(video_files)}.mp4"
                print(f"Downloading short clip {len(video_files)+1}/{num_videos}...")

                r = requests.get(best["link"], stream=True)
                with open(video_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                video_files.append(video_path)
        except Exception as e:
            print(f"Error: {e}")
            continue

    if len(video_files) < 2:
        print("Falling back to landscape videos...")
        for keyword in keywords[:3]:
            if len(video_files) >= num_videos:
                break
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=2&orientation=landscape"
            try:
                response = requests.get(url, headers=headers)
                data = response.json()
                for video in data.get("videos", []):
                    if len(video_files) >= num_videos:
                        break
                    video_files_list = video["video_files"]
                    best = next((v for v in video_files_list if v["quality"] == "hd"), video_files_list[0])
                    video_path = f"temp_shorts/short_clip_{len(video_files)}.mp4"
                    r = requests.get(best["link"], stream=True)
                    with open(video_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    video_files.append(video_path)
            except:
                continue

    print(f"Downloaded {len(video_files)} clips for Short")
    return video_files

THUMBNAIL_STYLES = [
    # Dark navy + red
    {"bg": (15, 15, 35), "accent": (220, 20, 20), "text": (255, 255, 255), "sub": (180, 180, 180)},
    # Black + gold
    {"bg": (10, 10, 10), "accent": (212, 160, 20), "text": (255, 255, 255), "sub": (200, 195, 170)},
    # Dark navy + cyan
    {"bg": (5, 20, 45), "accent": (0, 180, 216), "text": (255, 255, 255), "sub": (160, 200, 220)},
    # Charcoal + orange
    {"bg": (20, 15, 10), "accent": (230, 95, 15), "text": (255, 255, 255), "sub": (200, 185, 165)},
]

def create_shorts_thumbnail(topic, output="thumbnail_short.png"):
    """Crea miniatura vertical para Short"""
    print("Creating Short thumbnail...")

    style = random.choice(THUMBNAIL_STYLES)

    img = Image.new("RGB", (1080, 1920), color=style["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 1080, 20], fill=style["accent"])
    draw.rectangle([0, 1900, 1080, 1920], fill=style["accent"])

    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 90)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 55)
    except OSError:
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 90)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 50)
            font_tag = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 55)
        except OSError:
            font_big = ImageFont.load_default()
            font_small = font_big
            font_tag = font_big

    draw.text((60, 200), "RIGHTS UNLOCKED", font=font_tag, fill=style["accent"])

    wrapped = textwrap.fill(topic.upper(), width=18)
    draw.text((60, 400), wrapped, font=font_big, fill=style["text"])

    draw.text((60, 1750), "KNOW YOUR RIGHTS - LEGAL TIPS", font=font_small, fill=style["sub"])

    img.save(output)
    print(f"Short thumbnail saved to {output}")

def loop_clip_to_duration(clip, duration):
    """Repite el clip hasta alcanzar la duracion requerida"""
    if clip.duration >= duration:
        return clip.subclipped(0, duration)
    n = int(duration / clip.duration) + 2
    return concatenate_videoclips([clip] * n).subclipped(0, duration)

def create_short_video(voice_file="voice_short.mp3", output="final_short.mp4"):
    """Monta el Short vertical 1080x1920"""
    print("Creating Short video...")

    with open("current_short.txt", "r") as f:
        topic = f.readline().replace("TOPIC: ", "").strip()

    audio = AudioFileClip(voice_file)
    total_duration = audio.duration
    print(f"Short duration: {total_duration:.1f} seconds")

    num_clips = 4
    video_clips_paths = download_pexels_vertical_videos(num_videos=num_clips)

    clips = []
    clip_duration = total_duration / max(len(video_clips_paths), 1)

    for i, path in enumerate(video_clips_paths):
        print(f"Processing clip {i+1}/{len(video_clips_paths)}...")
        try:
            clip = VideoFileClip(path).without_audio()
            clip = loop_clip_to_duration(clip, clip_duration)

            clip_w, clip_h = clip.size
            target_w, target_h = 1080, 1920

            scale = max(target_w / clip_w, target_h / clip_h)
            new_w = int(clip_w * scale)
            new_h = int(clip_h * scale)

            clip = clip.resized((new_w, new_h))

            x_center = (new_w - target_w) // 2
            y_center = (new_h - target_h) // 2
            clip = clip.cropped(x1=x_center, y1=y_center, x2=x_center + target_w, y2=y_center + target_h)

            clips.append(clip)
        except Exception as e:
            print(f"Skipping clip {i+1}: {e}")
            continue

    if not clips:
        print("Creating fallback black clip...")
        clips = [ColorClip(size=(1080, 1920), color=(20, 20, 40), duration=total_duration)]

    print("Concatenating Short clips...")
    final_clip = concatenate_videoclips(clips, method="compose")

    if final_clip.duration > total_duration:
        final_clip = final_clip.subclipped(0, total_duration)

    final_clip = final_clip.with_audio(audio)

    print("Rendering Short...")
    final_clip.write_videofile(
        output,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_short_audio.m4a",
        remove_temp=True,
        logger=None,
    )

    for path in video_clips_paths:
        try:
            os.remove(path)
        except:
            pass

    print(f"Short created: {output}")
    return output

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

def upload_short():
    with open("current_short.txt") as f:
        lines = f.readlines()

    topic = lines[0].replace("TOPIC: ", "").strip()
    title = lines[1].replace("TITLE: ", "").strip() if len(lines) > 1 and lines[1].startswith("TITLE:") else topic

    description = SHORTS_DESCRIPTION
    tags = SHORTS_TAGS
    if os.path.exists("current_shorts_metadata.json"):
        with open("current_shorts_metadata.json", encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", title)
        description = meta.get("description", description)
        tags = meta.get("tags", tags)

    youtube = authenticate_youtube()

    print(f"Uploading Short: {title}")
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
        media_body=MediaFileUpload("final_short.mp4", resumable=True),
    )

    response = request.execute()
    video_id = response["id"]
    print(f"Short uploaded: https://youtube.com/shorts/{video_id}")
    print("Note: YouTube Shorts do not support custom thumbnails via API.")

    return video_id

if __name__ == "__main__":
    with open("current_short.txt", "r") as f:
        topic = f.readline().replace("TOPIC: ", "").strip()

    create_shorts_thumbnail(topic)
    create_short_video()
    upload_short()

    print("\nShorts complete:")
    print("  - final_short.mp4 created and uploaded")
    print("  - thumbnail_short.png uploaded")

# shorts_creator.py
import requests
import os
import json
import pickle
import random
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, ColorClip
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import textwrap
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import PEXELS_API_KEY, YOUTUBE_CLIENT_SECRET

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Mismo mapa de keywords que video_creator
THUMBNAIL_KEYWORD_MAP = {
    "landlord": ["eviction notice door", "apartment tenant dispute", "rental house keys"],
    "evict": ["eviction notice door", "apartment tenant dispute", "rental house keys"],
    "tenant": ["apartment rental door", "house keys tenant", "lease agreement signing"],
    "police": ["police officer street", "police stop car", "law enforcement badge"],
    "arrest": ["handcuffs arrest", "police officer arrest", "jail cell"],
    "traffic": ["police traffic stop car", "speeding ticket police", "car pulled over"],
    "parking": ["parking ticket car windshield", "parking violation", "meter expired"],
    "debt": ["debt collection bills", "credit card debt stress", "financial stress money"],
    "credit": ["credit card bills stress", "credit score document", "financial debt"],
    "fired": ["fired from job office", "unemployment stress worker", "job loss office"],
    "employee": ["office worker rights", "workplace employment", "business meeting fired"],
    "accident": ["car accident street", "vehicle crash road", "car collision damage"],
    "medical": ["hospital bill invoice", "medical debt insurance", "doctor bill stress"],
    "court": ["courthouse building", "judge gavel courtroom", "lawyer courtroom"],
    "lawsuit": ["courtroom judge gavel", "lawyer documents", "legal papers signing"],
    "scam": ["fraud scam alert", "identity theft computer", "online scam phone"],
    "identity": ["identity theft fraud", "stolen credit card", "hacker computer"],
    "contract": ["contract signing pen", "legal document agreement", "business contract"],
    "recording": ["phone recording conversation", "smartphone camera", "recording device"],
    "search": ["police search car", "warrant document police", "search and seizure"],
    "default": ["courthouse justice", "law books gavel", "legal documents lawyer"],
}

CLICKBAIT_SHORTS = [
    "Did You Know This?? 😱",
    "This Is Actually ILLEGAL",
    "KNOW THIS Before It's Too Late",
    "Most People Get This WRONG",
    "They Won't Tell You This 🚨",
    "SHOCKING Legal Fact",
]

THUMBNAIL_STYLES = [
    {"accent": (220, 20, 20), "text": (255, 255, 255)},
    {"accent": (212, 160, 20), "text": (255, 255, 255)},
    {"accent": (0, 180, 216), "text": (255, 255, 255)},
    {"accent": (230, 95, 15), "text": (255, 255, 255)},
]

def get_thumbnail_keywords(topic):
    topic_lower = topic.lower()
    for key, keywords in THUMBNAIL_KEYWORD_MAP.items():
        if key in topic_lower:
            return random.choice(keywords)
    return random.choice(THUMBNAIL_KEYWORD_MAP["default"])

def download_pexels_image(query, output_path="thumbnail_short_bg.jpg", vertical=True):
    """Descarga foto de Pexels para miniatura"""
    headers = {"Authorization": PEXELS_API_KEY}
    page = random.randint(1, 5)
    orientation = "portrait" if vertical else "landscape"
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&page={page}&orientation={orientation}"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            url = f"https://api.pexels.com/v1/search?query=courthouse justice&per_page=5&orientation={orientation}"
            response = requests.get(url, headers=headers)
            data = response.json()
            photos = data.get("photos", [])

        if photos:
            photo = random.choice(photos)
            img_url = photo["src"]["large2x"]
            r = requests.get(img_url)
            with open(output_path, "wb") as f:
                f.write(r.content)
            return output_path
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def draw_text_with_outline(draw, pos, text, font, text_color, outline_color, outline_width=3):
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def create_shorts_thumbnail(topic, output="thumbnail_short.png", title=None):
    """Crea miniatura vertical 1080x1920 con foto real de Pexels"""
    print("Creating Short thumbnail with real photo...")

    style = random.choice(THUMBNAIL_STYLES)
    keyword = get_thumbnail_keywords(topic)
    bg_path = download_pexels_image(keyword, "thumbnail_short_bg.jpg", vertical=True)

    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGB")
        img = img.resize((1080, 1920), Image.LANCZOS)

        overlay = Image.new("RGB", (1080, 1920), (0, 0, 0))
        img = Image.blend(img, overlay, alpha=0.45)

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
    else:
        img = Image.new("RGB", (1080, 1920), color=(15, 15, 35))

    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 95)
        font_mid = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 60)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    except OSError:
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 95)
            font_mid = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 60)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)
        except OSError:
            font_big = ImageFont.load_default()
            font_mid = font_big
            font_small = font_big

    # Barra superior
    draw.rectangle([0, 0, 1080, 80], fill=style["accent"])
    draw.text((30, 15), "⚖️ RIGHTS UNLOCKED", font=font_small, fill=(255, 255, 255))

    # Texto clickbait
    clickbait = random.choice(CLICKBAIT_SHORTS)
    draw_text_with_outline(draw, (30, 130), clickbait, font_mid,
                           style["accent"], (0, 0, 0), outline_width=3)

    # Título principal
    display = title if title else topic
    wrapped = textwrap.wrap(display.upper(), width=16)[:4]
    y_pos = 600
    for line in wrapped:
        draw_text_with_outline(draw, (30, y_pos), line, font_big,
                               (255, 255, 255), (0, 0, 0), outline_width=5)
        y_pos += 110

    # Barra inferior
    draw.rectangle([0, 1820, 1080, 1920], fill=style["accent"])
    draw.text((30, 1840), "FOLLOW FOR DAILY LEGAL TIPS", font=font_small, fill=(255, 255, 255))

    img.save(output)

    if bg_path and os.path.exists(bg_path):
        try:
            os.remove(bg_path)
        except:
            pass

    print(f"Short thumbnail saved to {output}")


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

    # Fallback a landscape si no hay verticales
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


def loop_clip_to_duration(clip, duration):
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

    video_clips_paths = download_pexels_vertical_videos(num_videos=4)

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
            clip = clip.cropped(x1=x_center, y1=y_center,
                                x2=x_center + target_w, y2=y_center + target_h)
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
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def upload_short():
    with open("current_short.txt") as f:
        lines = f.readlines()

    topic = lines[0].replace("TOPIC: ", "").strip()
    title = lines[1].replace("TITLE: ", "").strip() if len(lines) > 1 and lines[1].startswith("TITLE:") else topic

    description = "⚖️ Know your legal rights in 60 seconds!\n\nFollow for daily legal tips.\n\n⚠️ Educational purposes only. Not legal advice."
    tags = ["shorts", "legal shorts", "law shorts", "know your rights", "is it illegal", "legal tips"]

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
    return video_id


if __name__ == "__main__":
    topic = ""
    title = None

    with open("current_short.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("TOPIC:"):
                topic = line.replace("TOPIC: ", "").strip()
            elif line.startswith("TITLE:"):
                title = line.replace("TITLE: ", "").strip()

    if os.path.exists("current_shorts_metadata.json"):
        with open("current_shorts_metadata.json", encoding="utf-8") as f:
            meta = json.load(f)
            title = meta.get("title", title)

    create_shorts_thumbnail(topic, title=title)
    create_short_video()
    upload_short()

    print("\nShorts complete:")
    print("  - final_short.mp4 created and uploaded")
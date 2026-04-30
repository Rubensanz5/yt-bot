# video_creator.py
import requests
import os
import random
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap
from config import PEXELS_API_KEY

def download_pexels_videos(num_videos=10):
    """Descarga videos de Pexels con keywords legales"""
    print("Downloading videos from Pexels...")

    keywords = ["law", "court", "justice", "lawyer", "legal", "judge", "gavel", "courthouse", "contract", "rights"]
    random.shuffle(keywords)

    os.makedirs("temp_videos", exist_ok=True)
    video_files = []

    for keyword in keywords:
        if len(video_files) >= num_videos:
            break

        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=3&orientation=landscape"

        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            for video in data.get("videos", []):
                if len(video_files) >= num_videos:
                    break

                video_files_list = video["video_files"]
                hd_video = next((v for v in video_files_list if v["quality"] == "hd"), video_files_list[0])

                video_path = f"temp_videos/clip_{keyword}_{len(video_files)}.mp4"
                print(f"Downloading clip {len(video_files)+1}/{num_videos} ({keyword})...")

                r = requests.get(hd_video["link"], stream=True)
                with open(video_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                video_files.append(video_path)
        except Exception as e:
            print(f"Error downloading {keyword}: {e}")
            continue

    print(f"Downloaded {len(video_files)} clips")
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

def create_thumbnail(topic, output="thumbnail.png"):
    """Crea miniatura automatica profesional"""
    print("Creating thumbnail...")

    style = random.choice(THUMBNAIL_STYLES)

    img = Image.new("RGB", (1280, 720), color=style["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 15, 720], fill=style["accent"])

    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 72)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
    except OSError:
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 72)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
            font_tag = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 36)
        except OSError:
            font_big = ImageFont.load_default()
            font_small = font_big
            font_tag = font_big

    draw.text((50, 40), "KNOW YOUR RIGHTS", font=font_tag, fill=style["accent"])

    wrapped = textwrap.fill(topic.upper(), width=25)
    draw.text((50, 130), wrapped, font=font_big, fill=style["text"])

    draw.rectangle([50, 580, 1230, 585], fill=style["accent"])
    draw.text((50, 600), "FREE LEGAL GUIDE - EXPLAINED SIMPLY", font=font_small, fill=style["sub"])

    img.save(output)
    print(f"Thumbnail saved to {output}")

def loop_clip_to_duration(clip, duration):
    """Repite el clip hasta alcanzar la duracion requerida"""
    if clip.duration >= duration:
        return clip.subclipped(0, duration)
    n = int(duration / clip.duration) + 2
    return concatenate_videoclips([clip] * n).subclipped(0, duration)

def create_video(voice_file="voice.mp3", output="final_video.mp4"):
    """Monta el video final horizontal 1920x1080"""
    print("Creating final video...")

    with open("current_script.txt", "r") as f:
        topic = f.readline().replace("TOPIC: ", "").strip()

    audio = AudioFileClip(voice_file)
    total_duration = audio.duration
    print(f"Audio duration: {total_duration:.1f}s ({round(total_duration/60, 1)} min)")

    clip_length = 20
    num_clips = max(6, int(total_duration / clip_length) + 1)

    video_clips_paths = download_pexels_videos(num_videos=num_clips)

    clips = []
    clip_duration = total_duration / len(video_clips_paths)

    for i, path in enumerate(video_clips_paths):
        print(f"Processing clip {i+1}/{len(video_clips_paths)}...")
        try:
            clip = VideoFileClip(path).without_audio()
            clip = loop_clip_to_duration(clip, clip_duration)
            clip = clip.resized((1920, 1080))
            clips.append(clip)
        except Exception as e:
            print(f"Skipping clip {i+1}: {e}")
            continue

    if not clips:
        raise Exception("No valid clips processed")

    print("Concatenating clips...")
    final_clip = concatenate_videoclips(clips, method="compose")

    if final_clip.duration > total_duration:
        final_clip = final_clip.subclipped(0, total_duration)

    final_clip = final_clip.with_audio(audio)

    print("Rendering video... (may take 5-15 minutes)")
    final_clip.write_videofile(
        output,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        logger=None,
    )

    for path in video_clips_paths:
        try:
            os.remove(path)
        except:
            pass

    print(f"Video created: {output}")
    return output

if __name__ == "__main__":
    with open("current_script.txt", "r") as f:
        topic = f.readline().replace("TOPIC: ", "").strip()

    create_thumbnail(topic)
    create_video()

    print("\nStep 3 complete:")
    print("  - final_video.mp4")
    print("  - thumbnail.png")

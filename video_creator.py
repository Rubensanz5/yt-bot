# video_creator.py
import requests
import os
import random
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
from config import PEXELS_API_KEY

# Keywords de búsqueda de imágenes por tema legal
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

CLICKBAIT_TEMPLATES = [
    "They WON'T Tell You This",
    "ILLEGAL? Most People Don't Know",
    "This Could Cost You THOUSANDS",
    "Know This BEFORE It's Too Late",
    "WARNING: Your Rights Matter",
    "The Truth Nobody Tells You",
    "DON'T Make This Mistake",
    "SHOCKING Legal Facts",
]

THUMBNAIL_STYLES = [
    {"accent": (220, 20, 20), "text": (255, 255, 255), "shadow": (0, 0, 0)},
    {"accent": (212, 160, 20), "text": (255, 255, 255), "shadow": (0, 0, 0)},
    {"accent": (0, 180, 216), "text": (255, 255, 255), "shadow": (0, 0, 0)},
    {"accent": (230, 95, 15), "text": (255, 255, 255), "shadow": (0, 0, 0)},
]

def get_thumbnail_keywords(topic):
    """Elige keywords de imagen según el tema del video"""
    topic_lower = topic.lower()
    for key, keywords in THUMBNAIL_KEYWORD_MAP.items():
        if key in topic_lower:
            return random.choice(keywords)
    return random.choice(THUMBNAIL_KEYWORD_MAP["default"])

def download_pexels_image(query, output_path="thumbnail_bg.jpg"):
    """Descarga una foto de Pexels relacionada al tema"""
    headers = {"Authorization": PEXELS_API_KEY}
    # Offset aleatorio para que no siempre sea la misma foto
    page = random.randint(1, 5)
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&page={page}&orientation=landscape"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            # Fallback a query genérica
            url = f"https://api.pexels.com/v1/search?query=courthouse justice&per_page=5&orientation=landscape"
            response = requests.get(url, headers=headers)
            data = response.json()
            photos = data.get("photos", [])

        if photos:
            photo = random.choice(photos)
            img_url = photo["src"]["large2x"]  # 2560px ancho, alta calidad
            r = requests.get(img_url)
            with open(output_path, "wb") as f:
                f.write(r.content)
            print(f"Background image downloaded: {query}")
            return output_path
    except Exception as e:
        print(f"Error downloading image: {e}")

    return None

def draw_text_with_shadow(draw, pos, text, font, text_color, shadow_color, shadow_offset=4):
    """Dibuja texto con sombra para mejor legibilidad"""
    x, y = pos
    # Sombra
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Texto principal
    draw.text((x, y), text, font=font, fill=text_color)

def draw_text_with_outline(draw, pos, text, font, text_color, outline_color, outline_width=3):
    """Dibuja texto con contorno negro para máxima legibilidad sobre cualquier foto"""
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def create_thumbnail(topic, output="thumbnail.png", title=None):
    """Crea miniatura con foto real de Pexels + texto clickbait superpuesto"""
    print("Creating thumbnail with real photo...")

    style = random.choice(THUMBNAIL_STYLES)

    # 1. Descargar foto de fondo relacionada al tema
    keyword = get_thumbnail_keywords(topic)
    bg_path = download_pexels_image(keyword, "thumbnail_bg.jpg")

    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGB")
        img = img.resize((1280, 720), Image.LANCZOS)

        # Oscurecer la imagen para que el texto sea legible (overlay semitransparente)
        overlay = Image.new("RGB", (1280, 720), (0, 0, 0))
        img = Image.blend(img, overlay, alpha=0.45)

        # Añadir ligero blur en los bordes para efecto profesional
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
    else:
        # Fallback: fondo degradado oscuro
        img = Image.new("RGB", (1280, 720), color=(15, 15, 35))

    draw = ImageDraw.Draw(img)

    # Cargar fuentes
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 75)
        font_clickbait = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
    except OSError:
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 75)
            font_clickbait = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)
            font_tag = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 36)
        except OSError:
            font_title = ImageFont.load_default()
            font_clickbait = font_title
            font_tag = font_title

    # 2. Barra de color en la parte inferior (estilo noticia)
    draw.rectangle([0, 620, 1280, 720], fill=style["accent"])

    # 3. Tag superior izquierdo: "⚖️ RIGHTS UNLOCKED"
    draw.rectangle([0, 0, 380, 55], fill=style["accent"])
    draw.text((15, 10), "⚖️ RIGHTS UNLOCKED", font=font_tag, fill=(255, 255, 255))

    # 4. Texto clickbait en la parte superior (rotatorio)
    clickbait = random.choice(CLICKBAIT_TEMPLATES)
    draw_text_with_outline(draw, (20, 75), clickbait, font_clickbait,
                           style["accent"], (0, 0, 0), outline_width=3)

    # 5. Título principal del video (parte central-baja)
    if title:
        display_text = title
    else:
        display_text = topic

    # Truncar si es muy largo
    wrapped_lines = textwrap.wrap(display_text.upper(), width=22)
    if len(wrapped_lines) > 3:
        wrapped_lines = wrapped_lines[:3]
        wrapped_lines[-1] = wrapped_lines[-1] + "..."

    y_pos = 300
    for line in wrapped_lines:
        draw_text_with_outline(draw, (20, y_pos), line, font_title,
                               (255, 255, 255), (0, 0, 0), outline_width=4)
        y_pos += 88

    # 6. Texto en la barra inferior
    try:
        font_bottom = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 32)
    except OSError:
        font_bottom = font_tag
    draw.text((20, 633), "KNOW YOUR RIGHTS • FREE LEGAL GUIDE", font=font_bottom, fill=(255, 255, 255))

    img.save(output)

    # Limpiar imagen de fondo temporal
    if bg_path and os.path.exists(bg_path):
        try:
            os.remove(bg_path)
        except:
            pass

    print(f"Thumbnail saved to {output}")


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
    # Leer topic y title del metadata si existe
    topic = ""
    title = None

    with open("current_script.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("TOPIC:"):
                topic = line.replace("TOPIC: ", "").strip()
            elif line.startswith("TITLE:"):
                title = line.replace("TITLE: ", "").strip()

    import json
    if os.path.exists("current_metadata.json"):
        with open("current_metadata.json", encoding="utf-8") as f:
            meta = json.load(f)
            title = meta.get("title", title)

    create_thumbnail(topic, title=title)
    create_video()

    print("\nStep 3 complete:")
    print("  - final_video.mp4")
    print("  - thumbnail.png")
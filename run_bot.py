# run_bot.py
import subprocess
import sys

PYTHON = sys.executable

def run(script):
    print(f"\n{'='*40}")
    print(f"Running: {script}")
    print('='*40)
    subprocess.run([PYTHON, script], check=True)

if __name__ == "__main__":
    print("YouTube Bot Starting...")

    # --- Video largo ---
    print("\n--- LONG VIDEO PIPELINE ---")
    run("script_generator.py")   # Genera guion + voz
    run("video_creator.py")      # Crea video + miniatura
    run("youtube_uploader.py")   # Sube a YouTube

    # --- YouTube Short ---
    print("\n--- SHORTS PIPELINE ---")
    run("shorts_generator.py")   # Genera guion + voz corta
    run("shorts_uploader.py")    # Crea Short + sube a YouTube

    print("\nDone! Both video and Short uploaded to YouTube.")

# script_generator_shorts.py
import anthropic
import edge_tts
import asyncio
import os
import random
import json
from config import ANTHROPIC_API_KEY

SHORTS_TOPICS = [
    "Can police search your phone without a warrant",
    "What to do if your boss doesn't pay overtime",
    "Is it illegal to record someone in public",
    "Can a landlord enter without notice",
    "What happens if you don't show up to jury duty",
    "Can you legally refuse to show ID to police",
    "Is it illegal to drive barefoot",
    "Can your employer read your work emails",
    "What to do if a debt collector calls you",
    "Can a store detain you for shoplifting suspicion",
    "Is it legal to film police officers",
    "Can your landlord keep your security deposit",
    "What to do if you get a fake check",
    "Can you be fired for calling in sick",
    "Is it illegal to jaywalk in every state",
    "Can police lie to you during questioning",
    "What happens if you miss a court date",
    "Can your neighbor legally cut your tree branches",
    "Is it illegal to not have car insurance",
    "Can a cop pull you over for no reason",
]

SHORTS_VOICES = [
    "en-US-GuyNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-AndrewNeural",
]

SHORTS_TITLE_TEMPLATES = [
    "Is This Illegal? #shorts #law",
    "Know Your Rights! #shorts #legal",
    "Most People Don't Know This Is Illegal #shorts",
    "This Can Get You Arrested #shorts #rights",
    "The Law Nobody Told You About #shorts",
    "You're Probably Doing This Illegally #shorts",
]

def generate_shorts_title(topic):
    return random.choice(SHORTS_TITLE_TEMPLATES) + f" | {topic}"

def get_shorts_description():
    return """⚖️ Know your legal rights in 60 seconds!

Follow for daily legal tips that could save you thousands.

⚠️ Educational purposes only. Not legal advice."""

def get_shorts_tags():
    return [
        "shorts", "legal shorts", "law shorts", "know your rights",
        "is it illegal", "legal tips", "rights explained", "law facts"
    ]

def generate_shorts_metadata(topic):
    """Generates a unique description and topic-specific tags for the Short"""
    print("Generating unique Short metadata...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Write YouTube Shorts metadata for a 60-second legal education video about: "{topic}"

DESCRIPTION (60-80 words max, punchy):
- 1 sentence specific to this topic
- 2-3 quick bullet points of what they learn
- End with: "⚠️ Educational purposes only. Not legal advice."
- Include: "Follow for daily legal tips!"
Start with ⚖️ emoji.

TAGS:
Provide exactly 8 tags: 4 general Shorts/legal tags + 4 specific to "{topic}"

Respond in this exact format, nothing else:
DESCRIPTION:
[your description]
TAGS:
tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text
    desc_pos = text.find("DESCRIPTION:")
    tags_pos = text.find("TAGS:")

    if desc_pos == -1 or tags_pos == -1:
        return get_shorts_description(), get_shorts_tags()

    description = text[desc_pos + len("DESCRIPTION:"):tags_pos].strip()
    tags_raw = text[tags_pos + len("TAGS:"):].strip().strip("[]")
    tags = [t.strip().strip('"').strip("'") for t in tags_raw.split(",") if t.strip()][:8]

    if not tags:
        tags = get_shorts_tags()

    return description, tags


def generate_shorts_script(topic):
    """Genera guion viral para Short de 50-60 segundos"""
    print(f"Generating SHORT script for: {topic}")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a viral YouTube Shorts script writer for a legal education channel called RightsUnlocked.

Write a HIGH-RETENTION 60-second YouTube Short script about: {topic}

VIRAL RULES FOR SHORTS:
- First 2 seconds: hook so strong they cannot scroll past (question, shocking stat, or bold claim)
- Every 10 seconds: new surprising fact or twist
- Fast pace, punchy sentences, maximum 15 words per sentence
- End with a cliffhanger or call to follow for more
- Create urgency and fear of missing out

STRUCTURE:
- Second 0-5: HOOK (shocking question or fact)
- Second 5-20: The surprising truth
- Second 20-40: Real example or consequence
- Second 40-55: What you should do
- Second 55-60: Call to follow

STRICT RULES:
- Write ONLY the spoken words
- No brackets, no stage directions, no labels
- Short punchy sentences
- Target: 120-150 words MAXIMUM
- Sound like a friend warning you urgently

Topic: {topic}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    script = response.content[0].text
    word_count = len(script.split())
    print(f"Short script generated: {word_count} words (~{round(word_count/2.5)} seconds)")
    return script

async def generate_shorts_voice(script, output_file="voice_short.mp3", voice="en-US-GuyNeural"):
    """Convierte el guion a voz con Edge TTS (velocidad ligeramente mayor para Shorts)"""
    print(f"Generating voice for Short ({voice})...")
    communicate = edge_tts.Communicate(script, voice=voice, rate="+10%")
    await communicate.save(output_file)
    print(f"Voice saved to {output_file}")

def get_next_shorts_topic():
    """Rota los temas de Shorts automáticamente"""
    tracker_file = "shorts_tracker.txt"

    if not os.path.exists(tracker_file):
        with open(tracker_file, "w") as f:
            f.write("0")

    with open(tracker_file, "r") as f:
        index = int(f.read().strip())

    topic = SHORTS_TOPICS[index % len(SHORTS_TOPICS)]

    with open(tracker_file, "w") as f:
        f.write(str(index + 1))

    return topic

if __name__ == "__main__":
    topic = get_next_shorts_topic()
    print(f"Topic: {topic}")

    script = generate_shorts_script(topic)
    title = generate_shorts_title(topic)
    description, tags = generate_shorts_metadata(topic)
    voice = random.choice(SHORTS_VOICES)
    print(f"Voice: {voice}")

    print("\n--- SHORT SCRIPT ---")
    print(script)
    print("--- END ---\n")

    with open("current_short.txt", "w") as f:
        f.write(f"TOPIC: {topic}\nTITLE: {title}\n\n{script}")

    with open("current_shorts_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "topic": topic,
            "title": title,
            "voice": voice,
            "description": description,
            "tags": tags,
        }, f, indent=2, ensure_ascii=False)

    asyncio.run(generate_shorts_voice(script, "voice_short.mp3", voice))

    print("\nShorts Step 2 complete:")
    print("  - current_short.txt")
    print("  - current_shorts_metadata.json")
    print("  - voice_short.mp3")
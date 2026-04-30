# script_generator.py
import anthropic
import edge_tts
import asyncio
import os
import random
import json
from config import ANTHROPIC_API_KEY

LEGAL_TOPICS = [
    "What to do if a landlord illegally evicts you",
    "Your rights when police stop you on the street",
    "How to fight an unfair parking ticket",
    "What happens if you don't pay credit card debt",
    "How to file a small claims court case",
    "Your rights as an employee if you get fired",
    "What to do after a car accident",
    "How to deal with debt collectors legally",
    "What is a cease and desist letter",
    "Your rights if you are arrested",
    "How to dispute a medical bill",
    "What to do if your employer doesn't pay you",
    "How to handle identity theft legally",
    "Your rights as a tenant in an apartment",
    "What to do if you are wrongfully terminated",
    "How to protect yourself from scams legally",
    "Your rights during a traffic stop",
    "How to write a legal demand letter",
    "What to do if someone sues you",
    "Your rights if a store refuses a refund",
    "Can your boss legally spy on you at work",
    "What happens if you ignore a court summons",
    "Is it legal to record a conversation without consent",
    "What to do if police search your car illegally",
    "How to get out of a contract legally",
]

TITLE_TEMPLATES = [
    "Is This Illegal? {topic}",
    "You Can Get in Trouble for This… ({topic})",
    "Don't Do This… It's Illegal ({topic})",
    "This Can Cost You Thousands ({topic})",
    "Most People Don't Know This Is Illegal ({topic})",
    "Your Rights: {topic} Explained",
    "The Truth About {topic} Nobody Tells You",
    "Warning: {topic} Could Ruin You Financially",
]

VOICES = [
    "en-US-GuyNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-AndrewNeural",
]

# Duraciones variables para videos normales
DURATION_CONFIGS = [
    {"label": "6 minutes", "words": "900-1000"},
    {"label": "8 minutes", "words": "1000-1200"},
    {"label": "10 minutes", "words": "1200-1400"},
]

def generate_title(topic):
    return random.choice(TITLE_TEMPLATES).format(topic=topic)

def get_description():
    return """Learn your legal rights in simple terms. No confusing jargon, just straight facts.

⚖️ On this channel:
- Laws explained simply
- Legal tips you actually need
- Rights you should know before it's too late

🔔 Subscribe and hit the bell so you never miss an update.

⚠️ Disclaimer: This video is for educational purposes only and does not constitute legal advice. Always consult a licensed attorney for your specific situation."""

def get_tags():
    return [
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

def generate_metadata(topic):
    """Generates a unique description and topic-specific tags via Claude"""
    print("Generating unique metadata...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Write YouTube metadata for a legal education video about: "{topic}"

DESCRIPTION (150-200 words):
- Open with 1-2 sentences specific to this exact topic
- List 3 specific things viewers will learn
- Include: "🔔 Subscribe and hit the bell so you never miss an update."
- Close with: "⚠️ Disclaimer: This video is for educational purposes only and does not constitute legal advice. Always consult a licensed attorney for your specific situation."
Start with ⚖️ emoji.

TAGS:
Provide exactly 10 tags: 5 general legal education tags + 5 specific to "{topic}"

Respond in this exact format, nothing else:
DESCRIPTION:
[your description]
TAGS:
tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text
    desc_pos = text.find("DESCRIPTION:")
    tags_pos = text.find("TAGS:")

    if desc_pos == -1 or tags_pos == -1:
        return get_description(), get_tags()

    description = text[desc_pos + len("DESCRIPTION:"):tags_pos].strip()
    tags_raw = text[tags_pos + len("TAGS:"):].strip().strip("[]")
    tags = [t.strip().strip('"').strip("'") for t in tags_raw.split(",") if t.strip()][:10]

    if not tags:
        tags = get_tags()

    return description, tags


def generate_script(topic):
    """Genera guion viral de 6-10 minutos"""
    print(f"Generating script for: {topic}")

    config = random.choice(DURATION_CONFIGS)
    print(f"Target duration: {config['label']} (~{config['words']} words)")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a viral YouTube script writer for a legal education channel called RightsUnlocked.

Write a HIGH-RETENTION script about: {topic}

VIRAL RULES:
- Hook in first 5 seconds — use shock, a surprising stat, or a question that makes them scared to stop watching
- Every 20-30 seconds add a new curiosity loop or surprising fact to keep them watching
- Use simple conversational language, zero legal jargon
- Add emotional triggers: fear, surprise, relief, urgency
- Use real scenarios and relatable examples
- Phrases like: "here's what they don't tell you", "pay attention to this", "most people get this wrong", "this one mistake cost someone $10,000"

STRUCTURE (follow this flow, do NOT write section headers):
1. Hook — shocking open that makes them need to keep watching
2. Setup — explain the situation and why it matters
3. The truth — what the law actually says, surprising facts
4. Real example — a story or scenario that makes it real
5. Consequence — what happens if you get this wrong
6. Your rights — exactly what you can do
7. Step by step — what to do right now
8. Close — recap + call to subscribe

STRICT RULES:
- Write ONLY the spoken words
- No brackets, no stage directions, no section headers
- Flow naturally like someone talking to a friend
- Be specific with numbers, timelines, dollar amounts
- Target word count: {config['words']} words

Topic: {topic}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    script = response.content[0].text
    word_count = len(script.split())
    print(f"Script generated: {word_count} words (~{round(word_count/130)} minutes)")
    return script, config["label"]

async def generate_voice(script, output_file="voice.mp3", voice="en-US-GuyNeural"):
    """Convierte el guion a voz con Edge TTS"""
    print(f"Generating voice ({voice})...")
    communicate = edge_tts.Communicate(script, voice=voice)
    await communicate.save(output_file)
    print(f"Voice saved to {output_file}")

def get_next_topic():
    """Rota los temas automáticamente"""
    tracker_file = "topic_tracker.txt"

    if not os.path.exists(tracker_file):
        with open(tracker_file, "w") as f:
            f.write("0")

    with open(tracker_file, "r") as f:
        index = int(f.read().strip())

    topic = LEGAL_TOPICS[index % len(LEGAL_TOPICS)]

    with open(tracker_file, "w") as f:
        f.write(str(index + 1))

    return topic

if __name__ == "__main__":
    topic = get_next_topic()
    print(f"Topic: {topic}")

    script, duration = generate_script(topic)
    title = generate_title(topic)
    description, tags = generate_metadata(topic)
    voice = random.choice(VOICES)
    print(f"Voice: {voice}")

    print("\n--- SCRIPT PREVIEW ---")
    print(script[:400])
    print("--- END PREVIEW ---\n")

    with open("current_script.txt", "w") as f:
        f.write(f"TOPIC: {topic}\nTITLE: {title}\nDURATION: {duration}\n\n{script}")

    with open("current_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "topic": topic,
            "title": title,
            "duration": duration,
            "voice": voice,
            "description": description,
            "tags": tags,
        }, f, indent=2, ensure_ascii=False)

    asyncio.run(generate_voice(script, "voice.mp3", voice))

    print("\nStep 2 complete:")
    print("  - current_script.txt")
    print("  - current_metadata.json")
    print("  - voice.mp3")
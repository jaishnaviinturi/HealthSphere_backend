import requests
import random
from googleapiclient.discovery import build
import time
from flask import Flask, request, jsonify
from flask_cors import CORS 
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app) 

HF_API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
HF_API_KEY = os.getenv("HF_API_KEY")  # Load from .env
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Load from .env
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

mood_queries = {
    "joy": "uplifting funny videos",
    "sadness": "comforting music calm videos",
    "anger": "intense workout motivation",
    "fear": "relaxing meditation anxiety relief",
    "surprise": "amazing surprising moments",
    "disgust": "funny distraction videos",
    "neutral": "interesting trivia facts"
}

fallback_rules = {
    "overthinking": "fear", "suffocating": "fear", "scared": "fear", "anxious": "fear", "nervous": "fear",
    "terrified": "fear", "worried": "fear", "insecure": "fear", "uneasy": "fear", "panic": "fear",
    "paranoia": "fear", "frightened": "fear", "dread": "fear", "restless": "fear", "pressured": "fear",
    "stressed": "fear", "intimidated": "fear",

    "depressed": "sadness", "hopeless": "sadness", "miserable": "sadness", "lonely": "sadness",
    "heartbroken": "sadness", "drained": "sadness", "crying": "sadness", "grief": "sadness",

    "tired": "neutral", "bored": "neutral", "meh": "neutral", "alright": "neutral",
    "okay": "neutral", "fine": "neutral",

    "happy": "joy", "excited": "joy", "cheerful": "joy", "ec Ascertain": "joy","ecstatic": "joy", "thrilled": "joy",
    "grateful": "joy", "joyful": "joy", "content": "joy", "delighted": "joy", "proud": "joy",
    "enthusiastic": "joy", "blessed": "joy",

    "angry": "anger", "furious": "anger", "mad": "anger", "frustrated": "anger", "irritated": "anger",
    "pissed": "anger", "annoyed": "anger", "raging": "anger", "upset": "anger", "betrayed": "anger",
    "insulted": "anger", "provoked": "anger", "fuming": "anger", "aggravated": "anger",

    "surprised": "surprise", "amazed": "surprise", "shocked": "surprise", "wow": "surprise",
    "unexpected": "surprise", "unbelievable": "surprise", "stunning": "surprise",
    "mind-blowing": "surprise", "speechless": "surprise", "impressed": "surprise",
    "extraordinary": "surprise", "insane": "surprise", "overwhelmed": "surprise",

    "disgusted": "disgust", "gross": "disgust", "sick": "disgust", "repulsed": "disgust",
    "nauseous": "disgust", "awful": "disgust", "yuck": "disgust", "uncomfortable": "disgust",
    "unsettling": "disgust", "weird": "disgust", "revolting": "disgust", "terrible": "disgust",
    "creepy": "disgust", "off-putting": "disgust"
}

def detect_mood(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            payload = {"inputs": text}
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                top_mood = max(result[0], key=lambda x: x["score"])["label"]
                return top_mood
            else:
                print(f"HF API Error: {response.status_code}")
                if response.status_code != 503:
                    break
        except Exception as e:
            print(f"Request failed: {e}")
        time.sleep(2) 

    text = text.lower()
    for keyword, mood in fallback_rules.items():
        if keyword in text:
            print(f"Using fallback: Detected '{keyword}' → {mood}")
            return mood
    return "neutral" 

def fetch_youtube_video(mood):
    query = mood_queries.get(mood, "interesting videos")
    try:
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=5,
            type="video"
        ).execute()
        if "items" in search_response and search_response["items"]:
            video = random.choice(search_response["items"])
            video_id = video["id"]["videoId"]
            return f"https://youtube.com/watch?v={video_id}"
        else:
            return "https://youtube.com/watch?v=dQw4w9WgXcQ"  
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return "https://youtube.com/watch?v=dQw4w9WgXcQ"


@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    if user_input.lower() in ["exit", "quit", "bye"]:
        return jsonify({"response": "Bye for now!", "mood": None, "video_url": None})

    mood = detect_mood(user_input)
    
    response = f"It seems like you’re feeling {mood}. Want to tell me more?"

    video_url = fetch_youtube_video(mood)

    return jsonify({
        "response": response,
        "mood": mood,
        "video_url": video_url
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
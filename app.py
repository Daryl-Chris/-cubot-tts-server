from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY") or "YOUR_ELEVENLABS_API_KEY"
VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Rachel

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    if not data or "text" not in data:
        return {"error": "Missing 'text'"}, 400

    payload = {
        "text": data["text"],
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}
    }

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    r = requests.post(url, headers=headers, json=payload, stream=True)

    def stream():
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

    return Response(stream(), mimetype="audio/mpeg")

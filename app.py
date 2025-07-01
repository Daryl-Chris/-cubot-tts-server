from flask import Flask, request, send_file
import requests
import os
import tempfile

app = Flask(__name__)

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY2") or "YOUR_ELEVENLABS_API_KEY"
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

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    try:
        r = requests.post(tts_url, headers=headers, json=payload)
        if r.status_code != 200:
            return {"error": f"ElevenLabs error: {r.text}"}, r.status_code

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.write(r.content)
        temp_file.close()

        return send_file(temp_file.name, mimetype="audio/mpeg", as_attachment=False)

    except Exception as e:
        return {"error": str(e)}, 500

# 👇 Required by Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

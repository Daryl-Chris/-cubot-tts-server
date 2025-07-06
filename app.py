from flask import Flask, request, send_file
import requests, os, tempfile, subprocess

app = Flask(__name__)

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY2") or "your_elevenlabs_key"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"  # Laura

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    if not data or "text" not in data:
        return {"error": "Missing 'text'"}, 400

    payload = {
        "text": data["text"],
        "model_id": "eleven_monolingual_v1",
        "voice_settings": { "stability": 0.5, "similarity_boost": 0.7 }
    }

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    try:
        # Request TTS MP3
        r = requests.post(tts_url, headers=headers, json=payload)
        if r.status_code != 200:
            return {"error": f"ElevenLabs error: {r.text}"}, r.status_code

        # Save MP3 to temp file
        mp3_path = tempfile.mktemp(suffix=".mp3")
        with open(mp3_path, "wb") as f:
            f.write(r.content)

        # Convert MP3 to WAV using ffmpeg
        wav_path = tempfile.mktemp(suffix=".wav")
        cmd = ["ffmpeg", "-y", "-i", mp3_path, "-ac", "1", "-ar", "22050", wav_path]
        subprocess.run(cmd, check=True)

        os.remove(mp3_path)  # cleanup

        return send_file(wav_path, mimetype="audio/wav", as_attachment=False)

    except Exception as e:
        return {"error": str(e)}, 500

# Required by Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

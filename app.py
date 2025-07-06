from flask import Flask, request, send_file
import requests, tempfile, os
from pydub import AudioSegment

app = Flask(__name__)

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY2") or "your_key"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"  # Laura voice

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
        r = requests.post(tts_url, headers=headers, json=payload)
        if r.status_code != 200:
            return {"error": f"ElevenLabs: {r.text}"}, r.status_code

        # Save MP3 to temp
        tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_mp3.write(r.content)
        tmp_mp3.close()

        # Convert to WAV (Mono, 22050Hz)
        sound = AudioSegment.from_file(tmp_mp3.name, format="mp3")
        sound = sound.set_channels(1).set_frame_rate(22050)
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sound.export(tmp_wav.name, format="wav")
        tmp_wav.close()

        os.unlink(tmp_mp3.name)
        return send_file(tmp_wav.name, mimetype="audio/wav", as_attachment=False)

    except Exception as e:
        return {"error": str(e)}, 500

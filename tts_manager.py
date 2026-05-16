import requests
import edge_tts
import tempfile
import asyncio
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

ELEVENLABS_TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

async def generate_tts(text: str) -> str:
    """
    Try ElevenLabs first; if that fails, fall back to edge‑tts.
    Returns the path to the generated audio file (MP3).
    """
    # Attempt ElevenLabs
    try:
        audio_path = await _elevenlabs_tts(text)
        if audio_path:
            return audio_path
    except Exception as e:
        print(f"[WARN] ElevenLabs failed: {e}. Falling back to Edge‑TTS.")

    # Fallback to edge‑tts
    return await _edge_tts(text)

async def _elevenlabs_tts(text: str) -> str:
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = requests.post(ELEVENLABS_TTS_URL, json=payload, headers=headers, timeout=30)
    if response.status_code != 200:
        raise Exception(f"ElevenLabs HTTP {response.status_code}: {response.text}")
    
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    out_file.write(response.content)
    out_file.close()
    return out_file.name

async def _edge_tts(text: str) -> str:
    # Use a clear, neutral voice (en-US-JennyNeural)
    communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    await communicate.save(out_file.name)
    return out_file.name
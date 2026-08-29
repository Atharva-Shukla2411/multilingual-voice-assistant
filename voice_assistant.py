import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import requests


# -------------------------
# 1. Record voice
# -------------------------

sample_rate = 16000
duration = 20

print("Speak now...")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1
)

sd.wait()

write("recording.wav", sample_rate, audio)

print("Recording saved!")


# -------------------------
# 2. Convert speech to text
# -------------------------

print("\nTranscribing...")

whisper = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

segments, info = whisper.transcribe(
    "recording.wav")

text = ""

for segment in segments:
    text += segment.text

print("You said:")
print(text)


# -------------------------
# 3. Send text to Qwen
# -------------------------

print("\nUnderstanding information...")

prompt = f"""
You are a multilingual form-filling assistant.

The user may speak Hindi, Tamil, Telugu, English, or another
regional language.

Extract the requested information directly from the user's speech.

Return the values in English/Latin script where appropriate.

For names and place names, transliterate rather than translate.

Convert numbers such as ages into numeric values.

Do not invent information.
Use null when information is not provided.
User said:
{text}

Return ONLY valid JSON.

Use exactly this format:

{{
    "name": null,
    "age": null,
    "address": null,
    "phone": null
}}

Rules:
- Only extract information actually provided by the user.
- Do not invent information.
- Use null if information is missing.
"""

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3:1.7b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "format": "json"
    }
)

result = response.json()

print("\nAI extracted:")
print(result["message"]["content"])
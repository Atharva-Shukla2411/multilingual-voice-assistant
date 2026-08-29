import sounddevice as sd
import numpy as np
import wave
import time

SAMPLE_RATE = 16000
CHANNELS = 1

CHUNK_DURATION = 0.1
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Adjust this if necessary
THRESHOLD = 500

# How long silence must continue before stopping
SILENCE_DURATION = 1.5

silence_time = 0
recording_started = False

audio_data = []

print("🎤 Speak now...")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16",
    blocksize=CHUNK_SIZE
) as stream:

    while True:

        audio, overflow = stream.read(CHUNK_SIZE)

        audio = audio[:, 0]

        volume = np.sqrt(np.mean(audio.astype(np.float32) ** 2))

        if volume > THRESHOLD:

            recording_started = True
            silence_time = 0

            print("🎤", end="", flush=True)

        else:

            if recording_started:
                silence_time += CHUNK_DURATION

                print(".", end="", flush=True)

        audio_data.append(audio.copy())

        # Stop after enough silence
        if recording_started and silence_time >= SILENCE_DURATION:
            break

print("\n\n✅ Recording finished!")

# Save recording
audio_array = np.concatenate(audio_data)

with wave.open("vad_test.wav", "wb") as wf:

    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_array.astype(np.int16).tobytes())

print("💾 Saved as vad_test.wav")
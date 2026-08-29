import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
DURATION = 10


print("Loading Whisper...")

whisper = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def get_voice_input():
    print("\n🎤 Speak now...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1
    )

    sd.wait()

    write("recording.wav", SAMPLE_RATE, audio)

    print("Transcribing...")

    segments, info = whisper.transcribe(
    "recording.wav",
    beam_size=5,
    vad_filter=True,
    initial_prompt="The user may provide a 10 digit Indian phone number. Preserve all digits exactly."
)
    detected_language = info.language
    language_probability = info.language_probability

    print("Detected language:", detected_language)
    print("Language confidence:", language_probability)

    text = ""

    for segment in segments:
        text += segment.text

    print("You said:")
    print(text)

    return text, detected_language, language_probability

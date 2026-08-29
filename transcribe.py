from faster_whisper import WhisperModel

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)



def transcribe_with_language(audio_file):
    segments, info = model.transcribe(
        audio_file,
        beam_size=5
    )

    text = " ".join(segment.text for segment in segments)

    language = info.language
    probability = info.language_probability

    return text.strip(), language, probability
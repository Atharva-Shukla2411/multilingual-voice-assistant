import pyttsx3

ENGLISH_VOICE = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
HINDI_VOICE = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_hiIN_HemantM"


def speak(text, language="en"):
    engine = pyttsx3.init()

    if language == "hi":
        engine.setProperty("voice", HINDI_VOICE)
    else:
        engine.setProperty("voice", ENGLISH_VOICE)

    print(f"🤖 Assistant: {text}")

    engine.say(text)
    engine.runAndWait()
    engine.stop()
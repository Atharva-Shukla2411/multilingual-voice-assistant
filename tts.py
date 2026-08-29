import pyttsx3


def speak(text):
    print(f"\n🤖 Assistant: {text}")

    engine = pyttsx3.init()
    engine.setProperty("rate", 150)

    engine.say(text)
    engine.runAndWait()

    engine.stop()
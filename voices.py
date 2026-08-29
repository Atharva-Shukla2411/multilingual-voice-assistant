import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty("voices")

for i, voice in enumerate(voices):
    print("\nVOICE", i)
    print("Name:", voice.name)
    print("ID:", voice.id)
    print("Languages:", voice.languages)
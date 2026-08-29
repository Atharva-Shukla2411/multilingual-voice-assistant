from transcribe import transcribe_with_language

text, language, probability = transcribe_with_language("recording.wav")

print("\nText:")
print(text)

print("\nLanguage:")
print(language)

print("\nConfidence:")
print(probability)
from llm import extract_information

tests = [
    ("My name is Atharva", "name"),
    ("I am 18 years old", "age"),
    ("I live in Vellore", "address"),
    ("My phone number is 9876543210", "phone"),

    ("मेरा नाम अथर्व है", "name"),
    ("मेरी उम्र 18 साल है", "age"),
    ("मैं वेल्लोर में रहता हूँ", "address"),
    ("मेरा फोन नंबर 9876543210 है", "phone")
]

for text, field in tests:

    print("\n==============================")
    print("Input:", text)
    print("Field:", field)

    result = extract_information(text, field)

    print("LLM output:")
    print(result)
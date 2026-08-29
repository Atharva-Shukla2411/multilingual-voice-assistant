import requests

text = "My name is Aryav and I am 17 years old."

prompt = f"""
Extract the information from the following sentence.

Sentence:
{text}

Return ONLY JSON in this format:

{{
    "name": "...",
    "age": 0
}}
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

print(result["message"]["content"])
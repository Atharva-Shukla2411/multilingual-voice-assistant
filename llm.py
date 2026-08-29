import requests
import re


def extract_information(text, current_field):

    prompt = f"""
You are a multilingual form-filling assistant.

The user may speak Hindi, English, Tamil, Telugu,
or another regional language.

We are currently asking the user for:

{current_field}

The user said:
{text}

Your job is to extract information relevant to the current field.

IMPORTANT RULES:

1. The current field is: {current_field}

2. Only put information into the correct field.

3. If the user is answering the address question and says:
   "I live in Vellore"
   then the result MUST be:
   "address": "Vellore"

4. NEVER put an address or city into the "name" field.

5. NEVER change an already known name because the user mentions
   a city.

6. Do not invent information.

7. Use null for information that was not provided.

8. Convert ages to numbers.

9. Convert phone numbers to digits.

10. For names and places, use English/Latin script when appropriate.

11. Phone numbers must contain exactly 10 digits.

12. If the user gives a phone number with spaces, commas,
    hyphens, or other separators, remove the separators.

13. Never add commas to phone numbers.

14. Never change, round, shorten, or calculate a phone number.

15. Preserve every digit in the phone number exactly as provided.

16. If you are not confident about the phone number, return null
    rather than guessing.

Return ONLY valid JSON.

Use exactly this format:

{{
    "name": null,
    "age": null,
    "address": null,
    "phone": null
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

    return result["message"]["content"]



def clean_phone_number(phone):
    if phone is None:
        return None

    digits = re.sub(r"\D", "", str(phone))

    if len(digits) == 10:
        return digits

    return None

def extract_correction(text):

    prompt = f"""
You are a multilingual form correction assistant.

The current form contains these fields:

- name
- age
- address
- phone

The user wants to correct something.

User said:
{text}

Determine which field the user wants to correct
and what the new value should be.

Return ONLY valid JSON in this format:

{{
    "field": null,
    "value": null
}}

Possible fields are ONLY:

"name"
"age"
"address"
"phone"

Rules:

1. Return the field being corrected.
2. Return the new value.
3. If the user says something like:
   "My age is actually 19"
   return:
   {{
       "field": "age",
       "value": 19
   }}

4. If the user says:
   "My address is Chennai"
   return:
   {{
       "field": "address",
       "value": "Chennai"
   }}

5. Do not invent information.
6. Return null if you cannot determine the field.
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

    return result["message"]["content"]
import requests
import re


# ============================================================
# PHONE NUMBER CLEANING
# ============================================================

def clean_phone_number(phone):

    if phone is None:
        return None

    # Convert anything into text
    phone = str(phone)

    # Keep digits only
    digits = re.sub(r"\D", "", phone)

    # Must contain exactly 10 digits
    if len(digits) == 10:
        return digits

    return None


# ============================================================
# PHONE NUMBER FROM SPOKEN TEXT
# ============================================================

def extract_phone_from_text(text):

    if not text:
        return None

    text = text.lower().strip()

    # --------------------------------------------------------
    # Convert common spoken English number words to digits
    # --------------------------------------------------------

    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9"
    }

    # Replace number words with digits
    for word, digit in number_words.items():

        text = re.sub(
            rf"\b{word}\b",
            digit,
            text
        )

    # --------------------------------------------------------
    # Hindi number words
    # --------------------------------------------------------

    hindi_numbers = {
        "शून्य": "0",
        "एक": "1",
        "दो": "2",
        "तीन": "3",
        "चार": "4",
        "पाँच": "5",
        "पांच": "5",
        "छह": "6",
        "छः": "6",
        "सात": "7",
        "आठ": "8",
        "नौ": "9"
    }

    for word, digit in hindi_numbers.items():

        text = text.replace(
            word,
            digit
        )

    # --------------------------------------------------------
    # Extract digits
    # --------------------------------------------------------

    digits = re.sub(
        r"\D",
        "",
        text
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if len(digits) == 10:

        return digits

    return None


# ============================================================
# INFORMATION EXTRACTION
# ============================================================

def extract_information(text, current_field):

    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if current_field == "phone":

        phone = extract_phone_from_text(text)

        if phone is not None:

            return (
                '{'
                '"name": null, '
                '"age": null, '
                '"address": null, '
                f'"phone": "{phone}"'
                '}'
            )

        # If Python cannot confidently extract
        # exactly 10 digits, return null.

        return (
            '{'
            '"name": null, '
            '"age": null, '
            '"address": null, '
            '"phone": null'
            '}'
        )


    # --------------------------------------------------------
    # OTHER FIELDS
    # --------------------------------------------------------

    prompt = f"""
You are a multilingual form-filling assistant.

The user may speak Hindi, English, Tamil, Telugu,
or another regional language.

We are currently asking the user for:

{current_field}

The user said:

{text}

Your job is to extract information relevant
ONLY to the current field.

IMPORTANT RULES:

1. The current field is: {current_field}

2. Only put information into the correct field.

3. If the current field is address and the user says:
   "I live in Vellore"
   return:
   {{
       "name": null,
       "age": null,
       "address": "Vellore",
       "phone": null
   }}

4. NEVER put an address or city into the name field.

5. NEVER change an already known name because
   the user mentions a city.

6. Do not invent information.

7. Use null for information that was not provided.

8. Convert ages to numbers.

9. Do NOT extract phone numbers here.

10. For names and places, use English/Latin script
    when appropriate.

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


# ============================================================
# CORRECTION EXTRACTION
# ============================================================

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

3. If the user says:
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

5. If the field is phone, return ONLY the
   10 digit phone number.

6. Never add commas to phone numbers.

7. Never invent information.

8. Return null if you cannot determine
   the field or value.
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

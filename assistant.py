from voice_input import get_voice_input
from llm import extract_information, extract_correction
from form_manager import update_form, show_form, get_missing_fields, correct_field

import json
import re

from tts_manager import speak


# Default language
user_language = "en"


def ask_question(field):
    questions = {
        "en": {
            "name": "What is your name?",
            "age": "What is your age?",
            "address": "What is your address?",
            "phone": "Please say your 10 digit phone number, one digit at a time."
        },

        "hi": {
            "name": "आपका नाम क्या है?",
            "age": "आपकी उम्र क्या है?",
            "address": "आप कहाँ रहते हैं?",
            "phone": "कृपया अपना 10 अंकों का फोन नंबर एक-एक अंक करके बताइए।"
        }
    }

    # Use English if detected language isn't supported
    language_questions = questions.get(user_language, questions["en"])

    question = language_questions[field]

    print(f"🤖 Assistant: {question}")

    speak(question, user_language)


def handle_correction():
    # Ask the correction question in the user's language
    if user_language == "hi":
        correction_question = (
            "ठीक है। कृपया बताइए कि कौन सी जानकारी सही करनी है।"
        )
    else:
        correction_question = (
            "Okay. Please tell me what information needs to be corrected."
        )

    print(f"🤖 Assistant: {correction_question}")
    speak(correction_question, user_language)

    # Get user's correction
    correction_text, detected_language, confidence = get_voice_input()

    print("\nYou said:")
    print(correction_text)

    # Ask LLM to identify field and new value
    result = extract_correction(correction_text)

    print("\nCorrection detected:")
    print(result)

    try:
        correction = json.loads(result)

    except json.JSONDecodeError:
        if user_language == "hi":
            speak(
                "मुझे सुधार समझ नहीं आया। कृपया दोबारा बताइए।",
                "hi"
            )
        else:
            speak(
                "I could not understand the correction. Please try again.",
                "en"
            )

        return False

    field = correction.get("field")
    value = correction.get("value")

    # Check whether correction was successfully detected
    if field is None or value is None:

        if user_language == "hi":
            speak(
                "मैं यह समझ नहीं पाया कि कौन सी जानकारी बदलनी है।",
                "hi"
            )
        else:
            speak(
                "I could not determine what needs to be corrected.",
                "en"
            )

        return False

    # Update the corrected field
    correct_field(field, value)

    print(f"\nUpdated {field}: {value}")

    # Confirm correction in user's language
    if user_language == "hi":
        speak(
            f"आपकी {field} की जानकारी अपडेट कर दी गई है।",
            "hi"
        )
    else:
        speak(
            f"I have updated your {field}.",
            "en"
        )

    return True


# ==========================================
# MAIN PROGRAM
# ==========================================

print("================================")
print("   VOICE FORM ASSISTANT")
print("================================")


while True:

    # Check which fields are still missing
    missing = get_missing_fields()

    # ==========================================
    # FORM COMPLETE
    # ==========================================

    if not missing:

        while True:

            show_form()

            # Ask confirmation in the user's language
            if user_language == "hi":

                confirmation_question = (
                    "आपका फॉर्म पूरा हो गया है। "
                    "क्या दी गई सारी जानकारी सही है? "
                    "कृपया हाँ या नहीं कहें।"
                )

            else:

                confirmation_question = (
                    "Your form is complete. "
                    "Is all the information correct? "
                    "Please say yes or no."
                )

            print(f"🤖 Assistant: {confirmation_question}")

            speak(
                confirmation_question,
                user_language
            )

            # Get confirmation
            response, detected_language, confidence = get_voice_input()

            print("\nYou said:")
            print(response)

            response_lower = response.lower()

            # ==========================================
            # USER SAYS YES
            # ==========================================

            if "yes" in response_lower or "हाँ" in response_lower or "हां" in response_lower:

                if user_language == "hi":

                    speak(
                        "धन्यवाद। आपका फॉर्म पूरा हो गया है।",
                        "hi"
                    )

                else:

                    speak(
                        "Thank you. Your form has been completed.",
                        "en"
                    )

                print("\n🎉 FORM COMPLETED!")

                show_form()

                exit()

            # ==========================================
            # USER SAYS NO
            # ==========================================

            elif "no" in response_lower or "नहीं" in response_lower:

                success = handle_correction()

                if success:
                    continue

            # ==========================================
            # UNKNOWN RESPONSE
            # ==========================================

            else:

                if user_language == "hi":

                    speak(
                        "मुझे समझ नहीं आया। कृपया हाँ या नहीं कहें।",
                        "hi"
                    )

                else:

                    speak(
                        "I didn't understand. Please say yes or no.",
                        "en"
                    )

        # This prevents the program from continuing
        # into the missing-field section
        continue


    # ==========================================
    # ASK NEXT MISSING FIELD
    # ==========================================

    next_field = missing[0]

    ask_question(next_field)


    # ==========================================
    # GET USER'S ANSWER
    # ==========================================

    text, detected_language, confidence = get_voice_input()


    # ==========================================
    # REMEMBER USER'S LANGUAGE
    # ==========================================

    if confidence >= 0.70:

        if detected_language in ["hi", "en"]:

            user_language = detected_language

    print("User language:", user_language)


    # ==========================================
    # NOTHING DETECTED
    # ==========================================

    if not text.strip():

        if user_language == "hi":

            speak(
                "मुझे समझ नहीं आया। कृपया दोबारा बोलें।",
                "hi"
            )

        else:

            speak(
                "I couldn't understand that. Please try again.",
                "en"
            )

        continue


    # ==========================================
    # SEND TEXT TO LOCAL LLM
    # ==========================================

    print("\n🧠 Understanding...")

    result = extract_information(
        text,
        next_field
    )


    print("\nAI extracted:")
    print(result)


    # ==========================================
    # CONVERT JSON TO PYTHON DICTIONARY
    # ==========================================

    try:

        data = json.loads(result)

    except json.JSONDecodeError:

        if user_language == "hi":

            speak(
                "जानकारी को समझने में समस्या हुई। कृपया दोबारा बोलें।",
                "hi"
            )

        else:

            speak(
                "I had trouble understanding that. Please try again.",
                "en"
            )

        continue


    # ==========================================
    # PHONE NUMBER VALIDATION
    # ==========================================

    if next_field == "phone":

        digits = re.sub(r"\D", "", text)

        if len(digits) == 10:

            data["phone"] = digits

        else:

            data["phone"] = None

            if user_language == "hi":

                speak(
                    "कृपया अपना 10 अंकों का फोन नंबर दोबारा बताइए।",
                    "hi"
                )

            else:

                speak(
                    "Please say your 10 digit phone number again.",
                    "en"
                )

            continue


    # ==========================================
    # UPDATE FORM
    # ==========================================

    update_form(data)


    # ==========================================
    # SHOW CURRENT FORM
    # ==========================================

    show_form()
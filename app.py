import streamlit as st
import json

from form_manager import (
    form_data,
    get_missing_fields,
    update_form,
    correct_field
)

from voice_input import get_voice_input

from llm import (
    extract_information,
    extract_correction
)

from tts_manager import speak


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Multilingual Voice Form Assistant",
    page_icon="🎙️",
    layout="wide"
)


# ============================================================
# QUESTIONS
# ============================================================

QUESTIONS = {

    "en": {
        "name": "What is your name?",
        "age": "What is your age?",
        "address": "What is your address?",
        "phone": (
            "Please say your 10 digit phone number, "
            "one digit at a time."
        )
    },

    "hi": {
        "name": "आपका नाम क्या है?",
        "age": "आपकी उम्र क्या है?",
        "address": "आप कहाँ रहते हैं?",
        "phone": (
            "कृपया अपना 10 अंकों का फोन नंबर "
            "एक-एक अंक करके बताइए।"
        )
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "en"

if "last_spoken_question" not in st.session_state:
    st.session_state.last_spoken_question = None

if "status" not in st.session_state:
    st.session_state.status = "🟢 Ready"

if "correction_mode" not in st.session_state:
    st.session_state.correction_mode = False


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .main {
        padding-top: 1rem;
    }


    /* Header */

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 25px;
    }


    /* Form card */

    .form-card {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-top: 10px;
    }


    /* Individual field */

    .field {
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.20);
    }

    .field-name {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .field-value {
        font-size: 18px;
        font-weight: 500;
    }


    /* Completed */

    .completed {
        font-size: 13px;
    }


    /* Assistant card */

    .assistant-card {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-top: 10px;
    }


    /* Current question */

    .question-box {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin: 15px 0;
        font-size: 20px;
        font-weight: 500;
    }


    /* Footer */

    .footer {
        text-align: center;
        margin-top: 40px;
        font-size: 13px;
        opacity: 0.65;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎙️ Multilingual Voice Form Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Fill forms naturally using your voice — no typing required.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CURRENT LANGUAGE
# ============================================================

if st.session_state.language == "hi":
    language_text = "🇮🇳 Hindi"
else:
    language_text = "🇬🇧 English"


st.info(
    f"{st.session_state.status}  |  Current language: {language_text}"
)


# ============================================================
# FIND NEXT MISSING FIELD
# ============================================================

missing = get_missing_fields()

if missing:
    next_field = missing[0]
else:
    next_field = None


# ============================================================
# MAIN COLUMNS
# ============================================================

left_column, right_column = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# LEFT COLUMN — ASSISTANT
# ============================================================

with left_column:

    st.markdown(
        "## 🤖 Assistant"
    )

    st.markdown(
        '<div class="assistant-card">',
        unsafe_allow_html=True
    )


    # ========================================================
    # NORMAL QUESTION MODE
    # ========================================================

    if next_field:

        question = QUESTIONS[
            st.session_state.language
        ][next_field]


        # -----------------------------------------------
        # Current question
        # -----------------------------------------------

        st.markdown(
            f'<div class="question-box">{question}</div>',
            unsafe_allow_html=True
        )


        # -----------------------------------------------
        # Speak question only once
        # -----------------------------------------------

        if (
            st.session_state.last_spoken_question
            != question
        ):

            speak(
                question,
                st.session_state.language
            )

            st.session_state.last_spoken_question = (
                question
            )


        # -----------------------------------------------
        # Listening button
        # -----------------------------------------------

        if st.button(
            "🎤  Start Listening",
            use_container_width=True
        ):

            st.session_state.status = (
                "🎤 Listening..."
            )

            st.info(
                st.session_state.status
            )


            # -------------------------------------------
            # GET VOICE INPUT
            # -------------------------------------------

            text, detected_language, confidence = (
                get_voice_input()
            )


            # -------------------------------------------
            # LANGUAGE DETECTION
            # -------------------------------------------

            if confidence >= 0.70:

                if detected_language in ["hi", "en"]:

                    st.session_state.language = (
                        detected_language
                    )


            # -------------------------------------------
            # SHOW TRANSCRIPTION
            # -------------------------------------------

            st.markdown(
                "### 🗣️ You said:"
            )

            st.write(text)


            # -------------------------------------------
            # EMPTY INPUT
            # -------------------------------------------

            if not text.strip():

                st.session_state.status = (
                    "⚠️ No speech detected"
                )


                if (
                    st.session_state.language
                    == "hi"
                ):

                    speak(
                        "मुझे समझ नहीं आया। कृपया दोबारा बोलें।",
                        "hi"
                    )

                else:

                    speak(
                        "I couldn't understand that. Please try again.",
                        "en"
                    )


            else:

                # ---------------------------------------
                # FIND CURRENT FIELD
                # ---------------------------------------

                missing = get_missing_fields()


                if missing:

                    current_field = missing[0]


                    # -----------------------------------
                    # LLM PROCESSING
                    # -----------------------------------

                    st.session_state.status = (
                        "🧠 Understanding..."
                    )


                    st.info(
                        st.session_state.status
                    )


                    result = extract_information(
                        text,
                        current_field
                    )


                    # -----------------------------------
                    # AI RESULT
                    # -----------------------------------

                    st.markdown(
                        "### 🧠 AI extracted:"
                    )

                    st.code(result)


                    # -----------------------------------
                    # JSON
                    # -----------------------------------

                    try:

                        data = json.loads(result)


                        # --------------------------------
                        # UPDATE FORM
                        # --------------------------------

                        update_form(data)


                        st.session_state.status = (
                            "✅ Information saved"
                        )


                        st.success(
                            "Information added successfully!"
                        )


                    except json.JSONDecodeError:

                        st.session_state.status = (
                            "⚠️ Understanding failed"
                        )


                        if (
                            st.session_state.language
                            == "hi"
                        ):

                            speak(
                                "जानकारी को समझने में समस्या हुई। कृपया दोबारा बोलें।",
                                "hi"
                            )

                        else:

                            speak(
                                "I had trouble understanding that. Please try again.",
                                "en"
                            )


                    # -----------------------------------
                    # REFRESH
                    # -----------------------------------

                    st.rerun()


    # ========================================================
    # FORM COMPLETE
    # ========================================================

    else:

        # ----------------------------------------------------
        # IMPORTANT:
        # Don't show confirmation again while correcting
        # ----------------------------------------------------

        if not st.session_state.correction_mode:

            st.success(
                "🎉 All fields are completed!"
            )


            # -----------------------------------------------
            # Confirmation question
            # -----------------------------------------------

            if (
                st.session_state.language
                == "hi"
            ):

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


            st.markdown(
                f'<div class="question-box">'
                f'{confirmation_question}'
                f'</div>',
                unsafe_allow_html=True
            )


            # -----------------------------------------------
            # Speak confirmation once
            # -----------------------------------------------

            if (
                st.session_state.last_spoken_question
                != confirmation_question
            ):

                speak(
                    confirmation_question,
                    st.session_state.language
                )

                st.session_state.last_spoken_question = (
                    confirmation_question
                )


            # =============================================
            # YES / NO
            # =============================================

            col_yes, col_no = st.columns(2)


            # ---------------------------------------------
            # YES
            # ---------------------------------------------

            with col_yes:

                if st.button(
                    "✅ Yes, it's correct",
                    use_container_width=True
                ):

                    st.session_state.status = (
                        "🎉 Form completed!"
                    )


                    if (
                        st.session_state.language
                        == "hi"
                    ):

                        speak(
                            "धन्यवाद। आपका फॉर्म पूरा हो गया है।",
                            "hi"
                        )

                    else:

                        speak(
                            "Thank you. Your form has been completed.",
                            "en"
                        )


                    st.success(
                        "🎉 Form completed successfully!"
                    )


            # ---------------------------------------------
            # NO
            # ---------------------------------------------

            with col_no:

                if st.button(
                    "✏️ No, correct something",
                    use_container_width=True
                ):

                    st.session_state.correction_mode = True

                    st.rerun()


    # ========================================================
    # CORRECTION MODE
    # ========================================================

    if st.session_state.correction_mode:

        st.divider()

        st.subheader(
            "✏️ Correct Information"
        )


        # -----------------------------------------------
        # Correction question
        # -----------------------------------------------

        if (
            st.session_state.language
            == "hi"
        ):

            correction_question = (
                "ठीक है। कृपया बताइए कि कौन सी जानकारी सही करनी है।"
            )

        else:

            correction_question = (
                "Okay. Please tell me what information "
                "you would like to correct."
            )


        st.markdown(
            f'<div class="question-box">'
            f'{correction_question}'
            f'</div>',
            unsafe_allow_html=True
        )


        # -----------------------------------------------
        # Speak correction question once
        # -----------------------------------------------

        if (
            st.session_state.last_spoken_question
            != correction_question
        ):

            speak(
                correction_question,
                st.session_state.language
            )

            st.session_state.last_spoken_question = (
                correction_question
            )


        # -----------------------------------------------
        # Correction button
        # -----------------------------------------------

        if st.button(
            "🎤  Speak Correction",
            use_container_width=True
        ):

            st.session_state.status = (
                "🎤 Listening..."
            )


            st.info(
                st.session_state.status
            )


            # -------------------------------------------
            # GET CORRECTION
            # -------------------------------------------

            correction_text, detected_language, confidence = (
                get_voice_input()
            )


            st.markdown(
                "### 🗣️ You said:"
            )

            st.write(
                correction_text
            )


            if correction_text.strip():

                # ---------------------------------------
                # PROCESS CORRECTION
                # ---------------------------------------

                st.session_state.status = (
                    "🧠 Understanding correction..."
                )


                st.info(
                    st.session_state.status
                )


                result = extract_correction(
                    correction_text
                )


                st.markdown(
                    "### 🧠 Correction detected:"
                )

                st.code(result)


                # ---------------------------------------
                # PARSE JSON
                # ---------------------------------------

                try:

                    correction = json.loads(
                        result
                    )


                    field = correction.get(
                        "field"
                    )

                    value = correction.get(
                        "value"
                    )


                    # -----------------------------------
                    # VALIDATION
                    # -----------------------------------

                    if (
                        field is not None
                        and value is not None
                    ):

                        # -------------------------------
                        # UPDATE FIELD
                        # -------------------------------

                        correct_field(
                            field,
                            value
                        )


                        st.session_state.status = (
                            "✅ Correction saved"
                        )


                        # -------------------------------
                        # SPEAK SUCCESS
                        # -------------------------------

                        if (
                            st.session_state.language
                            == "hi"
                        ):

                            speak(
                                "आपकी जानकारी अपडेट कर दी गई है।",
                                "hi"
                            )

                        else:

                            speak(
                                "Your information has been updated.",
                                "en"
                            )


                        st.success(
                            f"✅ Updated {field}: {value}"
                        )


                        # -------------------------------
                        # EXIT CORRECTION MODE
                        # -------------------------------

                        st.session_state.correction_mode = (
                            False
                        )


                        st.session_state.last_spoken_question = (
                            None
                        )


                        st.rerun()


                    else:

                        st.session_state.status = (
                            "⚠️ Correction not understood"
                        )


                        if (
                            st.session_state.language
                            == "hi"
                        ):

                            speak(
                                "मैं यह समझ नहीं पाया कि कौन सी जानकारी बदलनी है।",
                                "hi"
                            )

                        else:

                            speak(
                                "I could not determine what needs to be corrected.",
                                "en"
                            )


                except json.JSONDecodeError:

                    st.session_state.status = (
                        "⚠️ Correction failed"
                    )


                    if (
                        st.session_state.language
                        == "hi"
                    ):

                        speak(
                            "मुझे सुधार समझ नहीं आया। कृपया दोबारा बताइए।",
                            "hi"
                        )

                    else:

                        speak(
                            "I could not understand the correction. Please try again.",
                            "en"
                        )


            else:

                st.warning(
                    "No speech detected. Please try again."
                )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# RIGHT COLUMN — FORM
# ============================================================

with right_column:

    st.markdown(
        "## 📝 Your Form"
    )


    st.markdown(
        '<div class="form-card">',
        unsafe_allow_html=True
    )


    # ========================================================
    # NAME
    # ========================================================

    name_value = form_data["name"]

    if name_value:

        st.markdown(
            f"""
            <div class="field">
                <div class="field-name">👤 NAME</div>
                <div class="field-value">{name_value}</div>
                <div class="completed">✅ Completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="field">
                <div class="field-name">👤 NAME</div>
                <div class="field-value">—</div>
                <div class="completed">⏳ Waiting for input</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # AGE
    # ========================================================

    age_value = form_data["age"]

    if age_value:

        st.markdown(
            f"""
            <div class="field">
                <div class="field-name">🎂 AGE</div>
                <div class="field-value">{age_value}</div>
                <div class="completed">✅ Completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="field">
                <div class="field-name">🎂 AGE</div>
                <div class="field-value">—</div>
                <div class="completed">⏳ Waiting for input</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # ADDRESS
    # ========================================================

    address_value = form_data["address"]

    if address_value:

        st.markdown(
            f"""
            <div class="field">
                <div class="field-name">📍 ADDRESS</div>
                <div class="field-value">{address_value}</div>
                <div class="completed">✅ Completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="field">
                <div class="field-name">📍 ADDRESS</div>
                <div class="field-value">—</div>
                <div class="completed">⏳ Waiting for input</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # PHONE
    # ========================================================

    phone_value = form_data["phone"]

    if phone_value:

        st.markdown(
            f"""
            <div class="field">
                <div class="field-name">📞 PHONE</div>
                <div class="field-value">{phone_value}</div>
                <div class="completed">✅ Completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="field">
                <div class="field-name">📞 PHONE</div>
                <div class="field-value">—</div>
                <div class="completed">⏳ Waiting for input</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # PROGRESS
    # ========================================================

    total_fields = len(
        form_data
    )


    completed_fields = (
        total_fields
        - len(get_missing_fields())
    )


    progress = (
        completed_fields / total_fields
    )


    st.markdown(
        "### 📊 Progress"
    )


    st.progress(
        progress
    )


    st.caption(
        f"{completed_fields} of {total_fields} "
        f"fields completed — "
        f"{int(progress * 100)}%"
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🎙️ Multilingual Edge Voice Assistant |
        Offline-first • Voice-powered • Privacy-focused
    </div>
    """,
    unsafe_allow_html=True
)

import streamlit as st
import json
import io
from datetime import datetime

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
    },

    "ta": {
        "name": "உங்கள் பெயர் என்ன?",
        "age": "உங்கள் வயது என்ன?",
        "address": "நீங்கள் எங்கு வசிக்கிறீர்கள்?",
        "phone": (
            "தயவுசெய்து உங்கள் 10 இலக்க தொலைபேசி "
            "எண்ணை ஒவ்வொரு இலக்கமாக சொல்லுங்கள்."
        )
    },

    "te": {
        "name": "మీ పేరు ఏమిటి?",
        "age": "మీ వయస్సు ఎంత?",
        "address": "మీరు ఎక్కడ నివసిస్తున్నారు?",
        "phone": (
            "దయచేసి మీ 10 అంకెల ఫోన్ నంబర్‌ను "
            "ఒక్కొక్క అంకెగా చెప్పండి."
        )
    }
}


# ============================================================
# LANGUAGE NAMES
# ============================================================

LANGUAGE_NAMES = {
    "en": "🇬🇧 English",
    "hi": "🇮🇳 Hindi",
    "ta": "🇮🇳 Tamil",
    "te": "🇮🇳 Telugu"
}


# ============================================================
# FIELD INFORMATION
# ============================================================

FIELD_INFO = {
    "name": ("👤", "Name"),
    "age": ("🎂", "Age"),
    "address": ("📍", "Address"),
    "phone": ("📞", "Phone")
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

if "form_completed" not in st.session_state:
    st.session_state.form_completed = False

if "completion_time" not in st.session_state:
    st.session_state.completion_time = None


# ============================================================
# RESET FUNCTION
# ============================================================

def reset_form():

    for field in form_data:
        form_data[field] = None

    st.session_state.language = "en"
    st.session_state.last_spoken_question = None
    st.session_state.status = "🟢 Ready"
    st.session_state.correction_mode = False
    st.session_state.form_completed = False
    st.session_state.completion_time = None


# ============================================================
# JSON EXPORT
# ============================================================

def get_form_json():

    return json.dumps(
        form_data,
        ensure_ascii=False,
        indent=4
    )


# ============================================================
# PDF EXPORT
# ============================================================

def create_pdf():

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable
    )

    buffer = io.BytesIO()

    # --------------------------------------------------------
    # PAGE SETUP
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=14
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#666666")
    )

    verified_style = ParagraphStyle(
        "VerifiedStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        alignment=TA_CENTER
    )

    # --------------------------------------------------------
    # DOCUMENT CONTENT
    # --------------------------------------------------------

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "MULTILINGUAL EDGE VOICE ASSISTANT",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Completed Form",
            subtitle_style
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#CCCCCC"),
            spaceBefore=2,
            spaceAfter=15
        )
    )

    # --------------------------------------------------------
    # FORM INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "FORM INFORMATION",
            section_style
        )
    )

    table_data = [
        [
            Paragraph(
                "<b>FIELD</b>",
                normal_style
            ),
            Paragraph(
                "<b>VALUE</b>",
                normal_style
            )
        ]
    ]

    field_labels = {
        "name": "Name",
        "age": "Age",
        "address": "Address",
        "phone": "Phone"
    }

    for field in [
        "name",
        "age",
        "address",
        "phone"
    ]:

        value = form_data.get(field)

        if value is None or str(value).strip() == "":
            value = "Not provided"

        table_data.append(
            [
                Paragraph(
                    field_labels[field],
                    normal_style
                ),
                Paragraph(
                    str(value),
                    normal_style
                )
            ]
        )

    # --------------------------------------------------------
    # FORM TABLE
    # --------------------------------------------------------

    form_table = Table(
        table_data,
        colWidths=[
            45 * mm,
            115 * mm
        ],
        repeatRows=1
    )

    form_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#E8EEF7")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F2937")
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D0D5DD")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BACKGROUND",
                (0, 1),
                (0, -1),
                colors.HexColor("#F8F9FA")
            )
        ])
    )

    story.append(form_table)

    story.append(
        Spacer(1, 15)
    )

    # --------------------------------------------------------
    # VERIFIED SECTION
    # --------------------------------------------------------

    verified_box = Table(
        [
            [
                Paragraph(
                    "✓ FORM VERIFIED",
                    verified_style
                )
            ],

            [
                Paragraph(
                    "The information above was reviewed "
                    "and confirmed by the user.",
                    small_style
                )
            ]
        ],
        colWidths=[160 * mm]
    )

    verified_box.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#F1F8F3")
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                1,
                colors.HexColor("#B7D8C0")
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            )
        ])
    )

    story.append(verified_box)

    story.append(
        Spacer(1, 18)
    )

    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    completion_time = st.session_state.completion_time

    if completion_time is None:
        completion_time = datetime.now()

    formatted_time = completion_time.strftime(
        "%d %B %Y, %I:%M %p"
    )

    details_data = [

        [
            Paragraph(
                "<b>Language</b>",
                normal_style
            ),

            Paragraph(
                LANGUAGE_NAMES.get(
                    st.session_state.language,
                    "English"
                ),
                normal_style
            )
        ],

        [
            Paragraph(
                "<b>Completed</b>",
                normal_style
            ),

            Paragraph(
                formatted_time,
                normal_style
            )
        ],

        [
            Paragraph(
                "<b>Processing</b>",
                normal_style
            ),

            Paragraph(
                "Local / Offline-first",
                normal_style
            )
        ]
    ]

    details_table = Table(
        details_data,
        colWidths=[
            45 * mm,
            115 * mm
        ]
    )

    details_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#DDDDDD")
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#F8F9FA")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(details_table)

    story.append(
        Spacer(1, 25)
    )

    # --------------------------------------------------------
    # PRIVACY NOTE
    # --------------------------------------------------------

    privacy_box = Table(
        [
            [
                Paragraph(
                    "<b>Privacy Notice</b><br/>"
                    "This form was completed using a "
                    "voice-powered, offline-first system. "
                    "User information is processed locally "
                    "wherever possible.",
                    small_style
                )
            ]
        ],
        colWidths=[160 * mm]
    )

    privacy_box.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#F8F9FA")
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D5D9DE")
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(privacy_box)

    story.append(
        Spacer(1, 25)
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#CCCCCC"),
            spaceBefore=5,
            spaceAfter=8
        )
    )

    story.append(
        Paragraph(
            "Multilingual Edge Voice Assistant  •  "
            "Voice-powered  •  Privacy-focused",
            small_style
        )
    )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎙️ Voice Assistant")

    st.write(
        "An offline-first assistant that helps users "
        "complete forms using natural speech."
    )

    st.divider()

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    st.subheader("🌐 Current Language")

    st.info(
        LANGUAGE_NAMES.get(
            st.session_state.language,
            "🇬🇧 English"
        )
    )

    st.divider()

    # --------------------------------------------------------
    # FORM CONTROLS
    # --------------------------------------------------------

    st.subheader("⚙️ Form Controls")

    if st.button(
        "🔄 Start New Form",
        use_container_width=True
    ):

        reset_form()
        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # PRIVACY
    # --------------------------------------------------------

    st.subheader("🔐 Privacy")

    st.success(
        "Local processing enabled"
    )

    st.caption(
        "Your voice and form information are processed "
        "locally wherever possible."
    )

    st.divider()

    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------

    st.subheader("💡 How it works")

    st.write("1. 🎤 Speak naturally")
    st.write("2. 📝 Speech is transcribed")
    st.write("3. 🧠 AI extracts information")
    st.write("4. 📋 Form is updated")
    st.write("5. ✅ Review and confirm")


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <style>

    .main-logo-container {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 5px;
        margin-bottom: 10px;
    }

    .tagline {
        text-align: center;
        font-size: 25px;
        font-weight: 700;
        line-height: 1.4;
        margin-top: 12px;
        margin-bottom: 28px;

        background: linear-gradient(
            90deg,
            #20c997,
            #4caf50,
            #4aa3df
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# CENTERED LOGO
# ------------------------------------------------------------

logo_left, logo_center, logo_right = st.columns(
    [1, 2, 1]
)

with logo_center:

    st.image(
        "logo.png",
        width=500
    )


# ------------------------------------------------------------
# TAGLINE
# ------------------------------------------------------------

st.markdown(
    """
    <div class="tagline">
        Fill forms naturally using your voice — no typing required.
    </div>
    """,
    unsafe_allow_html=True
)


st.divider()


# ============================================================
# STATUS BAR
# ============================================================

st.info(
    f"{st.session_state.status}   |   "
    f"Language: "
    f"{LANGUAGE_NAMES.get(st.session_state.language, 'English')}"
)


# ============================================================
# FIND MISSING FIELD
# ============================================================

missing = get_missing_fields()

if missing:
    next_field = missing[0]
else:
    next_field = None


# ============================================================
# PROGRESS
# ============================================================

total_fields = len(form_data)

completed_fields = (
    total_fields - len(get_missing_fields())
)

progress = completed_fields / total_fields

st.progress(progress)

st.caption(
    f"📊 Form Progress: {completed_fields}/{total_fields} "
    f"fields completed — {int(progress * 100)}%"
)

st.divider()


# ============================================================
# MAIN LAYOUT
# ============================================================

left_column, right_column = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# LEFT COLUMN — ASSISTANT
# ============================================================

with left_column:

    st.header("🤖 Assistant")

    # ========================================================
    # CORRECTION MODE
    # ========================================================

    if st.session_state.correction_mode:

        st.warning(
            "✏️ Correction Mode"
        )

        if st.session_state.language == "hi":

            correction_question = (
                "ठीक है। कृपया बताइए कि कौन सी "
                "जानकारी सही करनी है।"
            )

        else:

            correction_question = (
                "Okay. Please tell me what information "
                "you would like to correct."
            )

        st.subheader(
            correction_question
        )

        # ----------------------------------------------------
        # SPEAK CORRECTION QUESTION
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # CORRECTION BUTTON
        # ----------------------------------------------------

        if st.button(
            "🎤 Speak Correction",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.status = (
                "🎤 Listening..."
            )

            st.info(
                "🎤 Listening... Please speak your correction."
            )

            correction_text, detected_language, confidence = (
                get_voice_input()
            )

            if correction_text.strip():

                st.write(
                    "### 🗣️ You said:"
                )

                st.success(
                    correction_text
                )

                st.session_state.status = (
                    "🧠 Understanding correction..."
                )

                result = extract_correction(
                    correction_text
                )

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

                    if (
                        field is not None
                        and value is not None
                    ):

                        correct_field(
                            field,
                            value
                        )

                        st.session_state.status = (
                            "✅ Correction saved"
                        )

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
                            f"✅ {field.capitalize()} "
                            f"updated successfully!"
                        )

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
                                "मैं यह समझ नहीं पाया कि कौन सी "
                                "जानकारी बदलनी है। कृपया दोबारा बताइए।",
                                "hi"
                            )

                        else:

                            speak(
                                "I couldn't determine what "
                                "needs to be corrected. Please try again.",
                                "en"
                            )

                        st.error(
                            "I couldn't determine what "
                            "needs to be corrected."
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
                            "मुझे सुधार समझ नहीं आया। "
                            "कृपया दोबारा बताइए।",
                            "hi"
                        )

                    else:

                        speak(
                            "I couldn't understand the correction. "
                            "Please try again.",
                            "en"
                        )

                    st.error(
                        "I couldn't understand the correction."
                    )

            else:

                st.session_state.status = (
                    "⚠️ No speech detected"
                )

                if (
                    st.session_state.language
                    == "hi"
                ):

                    speak(
                        "मुझे कुछ सुनाई नहीं दिया। "
                        "कृपया दोबारा बोलें।",
                        "hi"
                    )

                else:

                    speak(
                        "I couldn't hear anything. "
                        "Please try again.",
                        "en"
                    )

                st.warning(
                    "⚠️ No speech detected. Please try again."
                )

    # ========================================================
    # NORMAL QUESTION MODE
    # ========================================================

    elif next_field:

        question = QUESTIONS[
            st.session_state.language
        ][next_field]

        st.caption(
            "CURRENT QUESTION"
        )

        st.subheader(
            question
        )

        # ----------------------------------------------------
        # SPEAK QUESTION ONLY ONCE
        # ----------------------------------------------------

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

        st.write("")

        # ----------------------------------------------------
        # LISTENING BUTTON
        # ----------------------------------------------------

        if st.button(
            "🎤 Start Listening",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.status = (
                "🎤 Listening..."
            )

            st.info(
                "🎤 Listening... Please speak your answer."
            )

            text, detected_language, confidence = (
                get_voice_input()
            )

            # ------------------------------------------------
            # LANGUAGE DETECTION
            # ------------------------------------------------

            if confidence >= 0.70:

                if detected_language in [
                    "en",
                    "hi",
                    "ta",
                    "te"
                ]:

                    st.session_state.language = (
                        detected_language
                    )

            # ------------------------------------------------
            # EMPTY INPUT
            # ------------------------------------------------

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
                        "I couldn't understand that. "
                        "Please try again.",
                        "en"
                    )

                st.warning(
                    "⚠️ No speech detected. Please try again."
                )

            else:

                # --------------------------------------------
                # TRANSCRIPTION
                # --------------------------------------------

                st.write(
                    "### 🗣️ You said:"
                )

                st.success(
                    text
                )

                # --------------------------------------------
                # FIND CURRENT FIELD
                # --------------------------------------------

                missing = get_missing_fields()

                if missing:

                    current_field = missing[0]

                    st.session_state.status = (
                        "🧠 Understanding..."
                    )

                    st.info(
                        "🧠 Understanding your answer..."
                    )

                    try:

                        # ------------------------------------
                        # EXTRACTION
                        # ------------------------------------

                        result = extract_information(
                            text,
                            current_field
                        )

                        # ------------------------------------
                        # PARSE JSON
                        # ------------------------------------

                        data = json.loads(
                            result
                        )

                        # ====================================
                        # PHONE VALIDATION
                        # ====================================

                        if current_field == "phone":

                            phone = data.get(
                                "phone"
                            )

                            if phone is None:

                                st.session_state.status = (
                                    "⚠️ Invalid phone number"
                                )

                                st.error(
                                    "⚠️ Please provide exactly "
                                    "10 digits."
                                )

                                if (
                                    st.session_state.language
                                    == "hi"
                                ):

                                    speak(
                                        "मुझे 10 अंकों का सही "
                                        "फोन नंबर चाहिए। "
                                        "कृपया दोबारा बताइए।",
                                        "hi"
                                    )

                                else:

                                    speak(
                                        "I need a valid 10 digit "
                                        "phone number. "
                                        "Please say it again.",
                                        "en"
                                    )

                            else:

                                update_form(
                                    data
                                )

                                st.session_state.status = (
                                    "✅ Information saved"
                                )

                                st.success(
                                    "✅ Phone number saved successfully!"
                                )

                                st.rerun()

                        # ====================================
                        # OTHER FIELDS
                        # ====================================

                        else:

                            update_form(
                                data
                            )

                            st.session_state.status = (
                                "✅ Information saved"
                            )

                            st.success(
                                "✅ Information added successfully!"
                            )

                            st.rerun()

                    except json.JSONDecodeError:

                        st.session_state.status = (
                            "⚠️ Understanding failed"
                        )

                        if (
                            st.session_state.language
                            == "hi"
                        ):

                            speak(
                                "जानकारी को समझने में समस्या हुई। "
                                "कृपया दोबारा बोलें।",
                                "hi"
                            )

                        else:

                            speak(
                                "I had trouble understanding that. "
                                "Please try again.",
                                "en"
                            )

                        st.error(
                            "⚠️ I couldn't understand your answer. "
                            "Please try again."
                        )

                    except Exception as e:

                        st.session_state.status = (
                            "⚠️ Something went wrong"
                        )

                        st.error(
                            "Something went wrong while "
                            "processing your answer."
                        )

                        st.caption(
                            f"Technical detail: {e}"
                        )

    # ========================================================
    # FORM COMPLETE / CONFIRMATION
    # ========================================================

    else:

        st.success(
            "🎉 All fields have been completed!"
        )

        # ----------------------------------------------------
        # CONFIRMATION QUESTION
        # ----------------------------------------------------

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

        st.subheader(
            confirmation_question
        )

        # ----------------------------------------------------
        # SPEAK CONFIRMATION ONLY ONCE
        # ----------------------------------------------------

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

        col_yes, col_no = st.columns(2)

        # ----------------------------------------------------
        # YES
        # ----------------------------------------------------

        with col_yes:

            if st.button(
                "✅ Yes, it's correct",
                use_container_width=True,
                type="primary"
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

                st.session_state.form_completed = (
                    True
                )

                st.session_state.completion_time = (
                    datetime.now()
                )

                st.rerun()

        # ----------------------------------------------------
        # NO
        # ----------------------------------------------------

        with col_no:

            if st.button(
                "✏️ No, correct something",
                use_container_width=True
            ):

                st.session_state.correction_mode = (
                    True
                )

                st.session_state.last_spoken_question = (
                    None
                )

                st.rerun()


# ============================================================
# RIGHT COLUMN — FORM
# ============================================================

with right_column:

    st.header("📝 Your Form")

    # ========================================================
    # NAME
    # ========================================================

    icon, label = FIELD_INFO["name"]

    if form_data["name"]:

        st.success(
            f"{icon} **{label}**\n\n"
            f"{form_data['name']}\n\n"
            f"✅ Completed"
        )

    else:

        st.info(
            f"{icon} **{label}**\n\n"
            "⏳ Waiting for input"
        )

    # ========================================================
    # AGE
    # ========================================================

    icon, label = FIELD_INFO["age"]

    if form_data["age"]:

        st.success(
            f"{icon} **{label}**\n\n"
            f"{form_data['age']}\n\n"
            f"✅ Completed"
        )

    else:

        st.info(
            f"{icon} **{label}**\n\n"
            "⏳ Waiting for input"
        )

    # ========================================================
    # ADDRESS
    # ========================================================

    icon, label = FIELD_INFO["address"]

    if form_data["address"]:

        st.success(
            f"{icon} **{label}**\n\n"
            f"{form_data['address']}\n\n"
            f"✅ Completed"
        )

    else:

        st.info(
            f"{icon} **{label}**\n\n"
            "⏳ Waiting for input"
        )

    # ========================================================
    # PHONE
    # ========================================================

    icon, label = FIELD_INFO["phone"]

    if form_data["phone"]:

        st.success(
            f"{icon} **{label}**\n\n"
            f"{form_data['phone']}\n\n"
            f"✅ Completed"
        )

    else:

        st.info(
            f"{icon} **{label}**\n\n"
            "⏳ Waiting for input"
        )

    # ========================================================
    # NEXT FIELD
    # ========================================================

    if next_field:

        icon, label = FIELD_INFO[next_field]

        st.warning(
            f"🎯 Next field: {icon} {label}"
        )

    # ========================================================
    # EXPORT COMPLETED FORM
    # ========================================================

    if st.session_state.form_completed:

        st.divider()

        st.subheader(
            "📄 Form Ready"
        )

        st.success(
            "Your form has been completed and verified."
        )

        # ----------------------------------------------------
        # PREVIEW JSON
        # ----------------------------------------------------

        form_json = get_form_json()

        with st.expander(
            "👁️ Preview saved information"
        ):

            st.code(
                form_json,
                language="json"
            )

        # ----------------------------------------------------
        # JSON DOWNLOAD
        # ----------------------------------------------------

        st.download_button(
            label="⬇️ Download JSON",
            data=form_json,
            file_name="completed_form.json",
            mime="application/json",
            use_container_width=True
        )

        # ----------------------------------------------------
        # PDF DOWNLOAD
        # ----------------------------------------------------

        try:

            pdf_data = create_pdf()

            st.download_button(
                label="📄 Download Professional PDF",
                data=pdf_data,
                file_name="completed_form.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        except ImportError:

            st.error(
                "PDF export requires ReportLab."
            )

            st.code(
                "pip install reportlab"
            )

        except Exception as e:

            st.error(
                "Could not generate the PDF."
            )

            st.caption(
                f"Technical detail: {e}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎙️ Multilingual Edge Voice Assistant  •  "
    "Offline-first  •  Voice-powered  •  Privacy-focused"
)

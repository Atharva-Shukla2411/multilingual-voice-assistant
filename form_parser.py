import re


# ============================================================
# COMMON FORM FIELD NAMES
# ============================================================

COMMON_FIELDS = {
    "name": [
        "name",
        "full name",
        "patient name",
        "applicant name",
        "first name",
        "last name"
    ],

    "age": [
        "age"
    ],

    "date_of_birth": [
        "date of birth",
        "dob",
        "birth date",
        "birthdate"
    ],

    "address": [
        "address",
        "residential address",
        "permanent address",
        "home address"
    ],

    "city": [
        "city",
        "town"
    ],

    "state": [
        "state"
    ],

    "pincode": [
        "pin code",
        "pincode",
        "postal code",
        "zip code"
    ],

    "phone": [
        "phone",
        "phone number",
        "mobile",
        "mobile number",
        "contact number"
    ],

    "email": [
        "email",
        "email address"
    ],

    "blood_group": [
        "blood group",
        "blood type"
    ],

    "gender": [
        "gender",
        "sex"
    ],

    "emergency_contact": [
        "emergency contact",
        "emergency phone",
        "emergency number"
    ]
}


# ============================================================
# DETECT FIELDS
# ============================================================

def detect_fields(form_text):

    """
    Detect possible form fields from text.

    Example:

        Name: __________
        Age: __________
        Address: __________

    Returns:

        ["name", "age", "address"]
    """

    detected_fields = []

    text = form_text.lower()

    for field, possible_names in COMMON_FIELDS.items():

        for name in possible_names:

            # Look for the field name in the form
            if re.search(r"\b" + re.escape(name) + r"\b", text):

                if field not in detected_fields:

                    detected_fields.append(field)

                break

    return detected_fields


# ============================================================
# TEST FUNCTION
# ============================================================

if __name__ == "__main__":

    sample_form = """
    Hospital Registration Form

    Full Name: __________________

    Age: __________________

    Date of Birth: ______________

    Blood Group: ________________

    Address: ____________________

    City: _______________________

    State: ______________________

    PIN Code: ___________________

    Phone Number: _______________

    Emergency Contact: __________
    """

    fields = detect_fields(sample_form)

    print("\nDetected fields:")

    for field in fields:

        print("-", field)

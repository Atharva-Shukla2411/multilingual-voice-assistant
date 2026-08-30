from pdf_parser import extract_text_from_pdf
from form_parser import detect_fields


def load_form(pdf_path):
    """
    Load a PDF form and detect its fields.

    PDF
      ↓
    Extract text
      ↓
    Detect fields
      ↓
    Return fields
    """

    print("\n📄 Reading form...")

    # Extract text from PDF
    form_text = extract_text_from_pdf(pdf_path)

    if not form_text.strip():
        print("❌ No readable text found in the PDF.")
        return []

    print("✅ PDF text extracted.")

    # Detect fields
    fields = detect_fields(form_text)

    print("✅ Fields detected.")

    return fields


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    pdf_path = input(
        "Enter the path of your PDF: "
    ).strip().strip('"')

    fields = load_form(pdf_path)

    print("\n========== DETECTED FORM FIELDS ==========\n")

    if fields:

        for field in fields:
            print("•", field)

    else:

        print("No fields were detected.")

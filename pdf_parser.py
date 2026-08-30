from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):

    """
    Extract all readable text from a PDF file.
    """

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    pdf_path = input(
    "Enter the path of your PDF: "
).strip().strip('"')

    text = extract_text_from_pdf(pdf_path)

    print("\n========== EXTRACTED TEXT ==========\n")

    print(text)

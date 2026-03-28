import platform
import pdfplumber

# Try importing OCR libs safely
try:
    import pytesseract
    from pdf2image import convert_from_path

    OCR_AVAILABLE = True

    # Only set Tesseract path on Windows — Linux/Mac find it automatically
    if platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

except Exception as e:
    OCR_AVAILABLE = False
    print("⚠ OCR libraries not available:", e)


def extract_text_from_pdf(pdf_path):
    text = ""

    # Step 1: Normal PDF text extraction
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("❌ PDF reading failed:", e)
        return ""

    # Step 2: OCR fallback — only kicks in if text is too short (scanned PDF)
    if len(text.strip()) < 100 and OCR_AVAILABLE:
        print("⚠ Using OCR fallback...")
        try:
            images = convert_from_path(pdf_path)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            text = ocr_text
        except Exception as e:
            print("❌ OCR failed:", e)

    return text
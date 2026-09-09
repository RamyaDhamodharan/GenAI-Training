import pymupdf
import pytesseract
from PIL import Image
import io

PDF_PATH = "clinic_patient_handbook_scanned.pdf"
OUTPUT_PATH = "clinic_patient_handbook_ocr.txt"

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

doc = pymupdf.open(PDF_PATH)

all_text = []

for page_number, page in enumerate(doc, start=1):
    pix = page.get_pixmap(dpi=200)

    image = Image.open(io.BytesIO(pix.tobytes("png")))

    text = pytesseract.image_to_string(image)

    all_text.append(f"\n--- PAGE {page_number} ---\n")
    all_text.append(text)

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    file.write("".join(all_text))

print(f"OCR completed.")
print(f"Pages processed: {len(doc)}")
print(f"Saved to: {OUTPUT_PATH}")
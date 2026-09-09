from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

PDF_PATH = "clinic_patient_handbook_scanned.pdf"

pages = [
    [
        "CLINIC PATIENT HANDBOOK",
        "",
        "1. Appointment Cancellation",
        "",
        "Patients should cancel unwanted appointments as early as possible.",
        "The clinic recommends cancelling at least 24 hours before the appointment.",
        "Patients who cannot attend should contact the clinic before the scheduled time.",
        "",
        "2. Missed Appointments",
        "",
        "A missed appointment means the patient did not attend as expected.",
        "Patients should contact the clinic if they cannot attend their booking.",
    ],
    [
        "CLINIC PATIENT HANDBOOK",
        "",
        "3. Rescheduling",
        "",
        "Patients may request a different appointment date when available.",
        "Staff should verify the current appointment status before rescheduling.",
        "",
        "4. Privacy",
        "",
        "Only authorized staff should access confidential patient information.",
        "Authentication is required for protected clinic records.",
        "Patient records should be handled according to clinic privacy procedures.",
    ],
]

images = []

for page_number, lines in enumerate(pages):
    image = Image.new("RGB", (1240, 1754), "white")
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("arial.ttf", 42)
        body_font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    y = 120

    for i, line in enumerate(lines):
        font = title_font if i == 0 else body_font
        draw.text((100, y), line, fill="black", font=font)
        y += 65 if line else 35

    image_path = f"scanned_page_{page_number + 1}.png"
    image.save(image_path)
    images.append(image_path)

pdf = canvas.Canvas(PDF_PATH, pagesize=A4)

for image_path in images:
    pdf.drawImage(image_path, 0, 0, width=A4[0], height=A4[1])
    pdf.showPage()

pdf.save()

print(f"Created: {PDF_PATH}")
print(f"Pages: {len(images)}")
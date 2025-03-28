import os
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pdf2image import convert_from_path
from zipfile import ZipFile
import pytesseract
import cv2
import numpy as np

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Use getlength for newer PIL versions
        line_width = font.getlength(' '.join(current_line))
        if line_width > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def draw_centered_text(draw, text, font, x, y, max_width):
    if not text:
        return
    
    lines = wrap_text(text, font, max_width)
    line_spacing = int(font.size * 1.2)  # Adjust line spacing based on font size
    
    for i, line in enumerate(lines):
        line_width = font.getlength(line)
        new_x = x + (max_width - line_width) // 2
        line_y = y + (i * line_spacing)
        draw.text((new_x, line_y), line, font=font, fill="black")

def analyze_template(template_path):
    # Convert PDF to image
    image = cv2.imread(template_path)
    if image is None:
        raise ValueError("Could not read the image")
    
    # Convert to grayscale properly
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Extract text and positions using OCR
    text_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    # Analyze layout and create position dictionary
    positions = {}
    for i, text in enumerate(text_data['text']):
        if text.strip():
            x = text_data['left'][i]
            y = text_data['top'][i]
            width = text_data['width'][i]
            positions[text.strip()] = (x, y, width)
    
    return positions

def generate_certificate_pdf(student_data, template_image, text_positions, font_size):
    image = Image.open(template_image)
    draw = ImageDraw.Draw(image)
    
    try:
        font_path = "DejaVuSans.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        # Fallback to Arial if DejaVuSans is not available
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
    
    # Process fields in specific order to prevent overlapping
    field_order = [
        "SR. No.", "GR.No.", "Student  ID:", "UID No.",
        "Name", "Fathers Name", "Surname", "Mothers Name",
        "Nationality", "Mother Tongue", "Religion", "Caste", "Sub Caste",
        "Birth Place", "Tal", "Dist", "State", "Country",
        "Birth Date", "In Words", "Previous School Attended",
        "Date of Admission", "Progress", "Conduct",
        "Date of Leaving School", "Last Class Attended", "From",
        "Reason of Leaving the School", "Remark", "Std", "Div"
    ]
    
    for field in field_order:
        if field in text_positions:
            x, y, max_width = text_positions[field]
            text = str(student_data.get(field, ''))
            draw_centered_text(draw, text, font, x, y, max_width)
    
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

st.title("School Certificate Generator")

uploaded_pdf = st.file_uploader("Upload Certificate Template (PDF)", type=["pdf"])
uploaded_data = st.file_uploader("Upload Student Data (.csv or .xlsx)", type=["csv", "xlsx"])

font_size = st.slider("Select Font Size", min_value=20, max_value=100, value=60, step=2)

if uploaded_pdf and uploaded_data:
    pdf_path = "uploaded_certificate.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())
    
    # Convert PDF and analyze template
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    template_image_path = "certificate_template.png"
    images[0].save(template_image_path, "PNG")
    
    # Use predefined positions instead of neural network predictions
    text_positions = {
        "SR. No.": (200, 500, 200),
        "Std": (1000, 1455, 100),
        "Div": (1030, 1455, 110),
        "GR.No.": (1450, 500, 100),
        "Student  ID:": (350, 590, 200),
        "UID No.": (450, 675, 250),
        "Name": (460, 755, 400),
        "Fathers Name": (1030, 745, 400),
        "Surname": (700, 825, 0),
        "Mothers Name": (1030, 825, 500),
        "Nationality": (320, 900, 200),
        "Mother Tongue": (970, 900, 600),
        "Religion": (320, 980, 200),
        "Caste": (700, 985, 200),
        "Sub Caste": (1300, 980, 200),
        "Birth Place": (600, 1060, 200),
        "Tal": (950, 1060, 200),
        "Dist": (1320, 1060, 200),
        "State": (500, 1140, 200),
        "Country": (1100, 1140, 200),
        "Birth Date": (700, 1215, 250),
        "In Words": (300, 1295, 1000),  # Increased max_width and adjusted position
        "Previous School Attended": (470, 1375, 600),
        "Date of Admission": (510, 1450, 200),
        "Progress": (330, 1530, 200),
        "Conduct": (1100,1530, 200),
        "Date of Leaving School": (470, 1610, 300),
        "Last Class Attended": (950, 1610, 300),
        "From": (1300, 1610, 200),
        "Reason of Leaving the School": (550, 1685, 500),
        "Remark": (310, 1765, 800),  # Increased max_width from 300 to 800
    }

    if uploaded_data.name.endswith('.csv'):
        df = pd.read_csv(uploaded_data, encoding='cp1252', skipinitialspace=False)
        df.columns = df.columns.str.strip()
    else:
        df = pd.read_excel(uploaded_data)

    for idx, row in df.iterrows():
        student_data = row.to_dict()
        cert_image = generate_certificate_pdf(student_data, template_image_path, text_positions, font_size)
        st.image(cert_image, caption=f"Preview: {student_data.get('Name', '')}", use_column_width=True)

    if st.button("Generate All and Download"):
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zf:
            for idx, row in df.iterrows():
                student_data = row.to_dict()
                cert_buffer = generate_certificate_pdf(student_data, template_image_path, text_positions, font_size)
                zf.writestr(f"{student_data.get('Name', 'certificate')}_{idx}.png", cert_buffer.getvalue())
        zip_buffer.seek(0)
        st.download_button("Download All Certificates as ZIP", zip_buffer.getvalue(), "certificates.zip")
else:
    st.warning("Please upload both a certificate template and student data file.")

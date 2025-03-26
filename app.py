import os
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pdf2image import convert_from_path
from zipfile import ZipFile

def draw_centered_text(draw, text, font, x, y, max_width):
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    new_x = x + (max_width - text_width) // 2  # Centering logic
    draw.text((new_x, y), text, font=font, fill="black")

def generate_certificate_pdf(student_data, template_image, text_positions, font_size=24):
    image = Image.open(template_image)
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    for field, (x, y, max_width) in text_positions.items():
        text = str(student_data.get(field, ''))
        draw_centered_text(draw, text, font, x, y, max_width)
    
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

st.title("School Certificate Generator")

uploaded_pdf = st.file_uploader("Upload Certificate Template (PDF)", type=["pdf"])
uploaded_data = st.file_uploader("Upload Student Data (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_pdf and uploaded_data:
    pdf_path = "uploaded_certificate.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    template_image_path = "certificate_template.png"
    images[0].save(template_image_path, "PNG")
    
    if uploaded_data.name.endswith('.csv'):
        df = pd.read_csv(uploaded_data, encoding='cp1252')
    else:
        df = pd.read_excel(uploaded_data)
    
    text_positions = {
        "SR. No.": (100, 250, 100),
        "Std": (250, 250, 50),
        "Div": (300, 250, 50),
        "GR.No.": (400, 250, 100),
        "Student ID": (150, 300, 200),
        "UID No.": (450, 300, 250),
        "Name": (200, 350, 400),
        "Father’s Name": (650, 350, 400),
        "Surname": (200, 400, 400),
        "Mother’s Name": (650, 400, 400),
        "Nationality": (200, 450, 200),
        "Mother Tongue": (650, 450, 200),
        "Religion": (200, 500, 200),
        "Caste": (650, 500, 200),
        "Birth Place": (200, 550, 300),
        "Tal": (500, 550, 200),
        "Dist": (200, 600, 200),
        "State": (500, 600, 200),
        "Country": (200, 650, 200),
        "Birth Date": (500, 650, 250),
        "In Words": (250, 700, 500),
        "Previous School Attended": (250, 750, 600),
        "Date of Admission": (500, 750, 200),
        "Progress": (250, 800, 200),
        "Conduct": (500, 800, 200),
        "Date of Leaving School": (250, 850, 300),
        "Last Class Attended": (500, 850, 300),
        "Reason of Leaving the School": (250, 900, 500),
        "Remark": (500, 900, 300),
    }
    
    for idx, row in df.iterrows():
        student_data = row.to_dict()
        st.write(f"Preview for: {student_data.get('Name', '')}")
        cert_image = generate_certificate_pdf(student_data, template_image_path, text_positions)
        st.image(cert_image, caption=f"Preview: {student_data.get('Name', '')}", use_column_width=True)
    
    if st.button("Generate All and Download"):
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zf:
            for idx, row in df.iterrows():
                student_data = row.to_dict()
                cert_buffer = generate_certificate_pdf(student_data, template_image_path, text_positions)
                zf.writestr(f"{student_data.get('Name', 'certificate')}_{idx}.png", cert_buffer.getvalue())
        zip_buffer.seek(0)
        st.download_button("Download All Certificates as ZIP", zip_buffer.getvalue(), "certificates.zip")
else:
    st.warning("Please upload both a certificate template and student data file.")

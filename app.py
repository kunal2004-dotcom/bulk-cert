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

def generate_certificate_pdf(student_data, template_image, text_positions, font_size):
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

font_size = st.slider("Select Font Size", min_value=30, max_value=100, value=60)

if uploaded_pdf and uploaded_data:
    pdf_path = "uploaded_certificate.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())
    images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path="/usr/bin/")
    template_image_path = "certificate_template.png"
    images[0].save(template_image_path, "PNG")

    if uploaded_data.name.endswith('.csv'):
        df = pd.read_csv(uploaded_data, encoding='cp1252', skipinitialspace=False)
        df.columns = df.columns.str.strip()
    else:
        df = pd.read_excel(uploaded_data)
    
    text_positions = {
        "SR. No.": (200, 500, 200),
        "Std": (1000, 1455, 100),
        "Div": (1030, 1455, 110),
        "GR.No.": (1450, 500, 100),
        "Student ID": (350, 590, 200),
        "UID No.": (450, 675, 250),
        "Name": (460, 755, 400),
        "Fathers Name": (1030, 745, 400),
        "Surname": (470, 825, 400),
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
        "In Words": (300, 1295, 500),
        "Previous School Attended": (470, 1375, 600),
        "Date of Admission": (510, 1450, 200),
        "Progress": (330, 1530, 200),
        "Conduct": (1100,1530, 200),
        "Date of Leaving School": (470, 1610, 300),
        "Last Class Attended": (950, 1610, 300),
        "From": (1300, 1610, 200),
        "Reason of Leaving the School": (550, 1685, 500),
        "Remark": (310, 1765, 300),
    }

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

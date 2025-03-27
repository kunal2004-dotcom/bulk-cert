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

def generate_certificate_pdf(student_data, template_image, text_positions, font_size=60):
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
    # Add font size slider
    font_size = st.slider("Select Font Size", 10, 100, 60, help="Adjust the font size for certificate text")
    
    pdf_path = "uploaded_certificate.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())
    images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path="/usr/bin/")
    template_image_path = "certificate_template.png"
    images[0].save(template_image_path, "PNG")

    if uploaded_data.name.endswith('.csv'):
        df = pd.read_csv(uploaded_data, encoding='cp1252', skipinitialspace=False)
        st.write("Original column names:", [f"'{col}'" for col in df.columns])
        df.columns = df.columns.str.strip()
    else:
        df = pd.read_excel(uploaded_data)
    
    text_positions = {
        # ... (keep your existing text_positions dictionary)
    }

    for idx, row in df.iterrows():
        student_data = row.to_dict()
        # ... (keep your existing debug writes)
        cert_image = generate_certificate_pdf(student_data, template_image_path, text_positions, font_size=font_size)
        st.image(cert_image, caption=f"Preview: {student_data.get('Name', '')}", use_column_width=True)

    if st.button("Generate All and Download"):
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zf:
            for idx, row in df.iterrows():
                student_data = row.to_dict()
                cert_buffer = generate_certificate_pdf(student_data, template_image_path, text_positions, font_size=font_size)
                zf.writestr(f"{student_data.get('Name', 'certificate')}_{idx}.png", cert_buffer.getvalue())
        zip_buffer.seek(0)
        st.download_button("Download All Certificates as ZIP", zip_buffer.getvalue(), "certificates.zip")
    
    if not df.empty:
        st.write("First row data:", df.iloc[0].to_dict())
else:
    st.warning("Please upload both a certificate template and student data file.")

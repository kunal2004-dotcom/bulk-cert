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
        df = pd.read_csv(uploaded_data, encoding='cp1252', skipinitialspace=False)
        # Print exact column names for debugging
        st.write("Original column names:", [f"'{col}'" for col in df.columns])
        # Clean up column names by stripping whitespace
        df.columns = df.columns.str.strip()
    else:
        df = pd.read_excel(uploaded_data)
    
    text_positions = {
        "SR. No.": (200, 500, 200),
        "Std": (100, 100, 100),
        "Div": (120, 100, 110),
        "GR.No.": (1450, 500, 100),
        "Student  ID:": (350, 590, 200),  # Keep only one version with exact CSV column name
        "UID No.": (450, 675, 250),
        "Name": (450, 750, 400),
        "Fathers Name": (1000, 750, 400),
        "Surname": (450, 830, 400),
        "Mothers Name": (990, 830, 500),
        "Nationality": (300, 910, 200),
        "Mother Tongue": (950, 910, 600),
        "Religion": (300, 990, 200),
        "Caste": (700, 990, 200),
        "Sub Caste": (950, 990, 200),
        "Birth Place ": (200, 550, 300),
        "Tal": (500, 550, 200),
        "Dist": (200, 600, 200),
        "State": (500, 600, 200),
        "Country": (200, 650, 200),
        "Birth Date ": (500, 650, 250),
        "In Words": (250, 700, 500),
        "Previous School Attended ": (250, 750, 600),
        "Date of Admission ": (500, 750, 200),
        "Progress": (250, 800, 200),
        "Conduct": (500, 800, 200),
        "Date of Leaving School ": (250, 850, 300),
        "Last Class Attended ": (500, 850, 300),
        "Reason of Leaving the School ": (250, 900, 500),
        "Remark": (500, 900, 300),
    }

    for idx, row in df.iterrows():
        student_data = row.to_dict()
        st.write("All data for debugging:", student_data)
        st.write("SR. No.:", student_data.get("SR. No.", "Not found"))
        st.write("Student ID:", student_data.get("Student ID", "Not found"))
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
    # Add debug print for the first row
    if not df.empty:
        st.write("First row data:", df.iloc[0].to_dict())
else:
    st.warning("Please upload both a certificate template and student data file.")

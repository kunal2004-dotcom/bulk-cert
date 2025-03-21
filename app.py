import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from zipfile import ZipFile

# Function to generate a certificate with a name in bold
def generate_certificate_image(name, template_image, font_size, text_x, text_y):
    # Open the image template
    image = Image.open(template_image)
    draw = ImageDraw.Draw(image)

    # Load font (using a default system font, or you can specify a TTF file)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size and position using textbbox
    bbox = draw.textbbox((text_x, text_y), name, font=font)
    text_width = bbox[2] - bbox[0]  # bbox[2] is the rightmost x-coordinate
    text_height = bbox[3] - bbox[1]  # bbox[3] is the bottom y-coordinate
    position = (text_x - text_width // 2, text_y - text_height // 2)

    # Draw the name in bold
    draw.text(position, name, font=font, fill="black", stroke_width=1, stroke_fill="black")

    # Save to a buffer
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return output

# Streamlit app
st.title("Bulk Certificate Generator with Image Template and Live Preview")

# Upload certificate image template
uploaded_template = st.file_uploader("Upload Certificate Template (Image)", type=["png", "jpg", "jpeg"])

# Input names via text box (separated by new lines or commas)
names_input = st.text_area("Enter Names (separated by commas or new lines):", placeholder="John Doe, Jane Doe\nMike Ross")

# Optional: Upload names list (CSV or Excel)
uploaded_names = st.file_uploader("Or upload Names List (.csv or .xlsx)", type=["csv", "xlsx"])

# Slider for font size
font_size = st.slider("Select Font Size", 10, 100, 50)

# Enhanced control for text position on the image
text_x_slider = st.slider("Horizontal Position (pixels)", -500, 1500, 500)
text_y = st.slider("Vertical Position (pixels)", 0, 1000, 300)

# Text input for precise horizontal position
text_x_input = st.number_input("Custom Horizontal Position (pixels)", value=text_x_slider, step=1)

# If a template is uploaded
if uploaded_template:
    # Parse names from text area input
    if names_input:
        names = [name.strip() for name in names_input.replace(',', '\n').split('\n') if name.strip()]
    else:
        # Load names from CSV or Excel if uploaded
        if uploaded_names:
            if uploaded_names.name.endswith('.csv'):
                names_df = pd.read_csv(uploaded_names)
            else:
                names_df = pd.read_excel(uploaded_names)
            if 'Name' in names_df.columns:
                names = names_df['Name'].tolist()
            else:
                st.error("The uploaded file does not contain a 'Name' column.")
                names = []
        else:
            names = []

    if names:
        # Show live previews of all generated certificates
        st.subheader("Live Preview of Generated Certificates:")
        for name in names:
            st.write(f"Preview for: {name}")
            preview_certificate = generate_certificate_image(name, uploaded_template, font_size, text_x_input, text_y)

            # Display the preview as an image
            st.image(preview_certificate, caption=f"Preview: {name}'s Certificate", use_column_width=True)

        # Option to download all certificates in bulk as a ZIP file
        if st.button("Generate All and Download"):
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, 'w') as zf:
                for name in names:
                    cert_buffer = generate_certificate_image(name, uploaded_template, font_size, text_x_input, text_y)
                    zf.writestr(f"{name}_certificate.png", cert_buffer.getvalue())
            zip_buffer.seek(0)
            st.download_button("Download All Certificates as ZIP", zip_buffer.getvalue(), "certificates.zip")
    else:
        st.warning("Please provide names to generate certificates.")

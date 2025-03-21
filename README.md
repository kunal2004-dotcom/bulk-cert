# Bulk Certificate Generator

A simple web application built with Streamlit that allows users to generate bulk certificates by uploading a certificate image template and providing a list of names. Users can preview the certificates in real-time and download them as a ZIP file.

## Features

- Upload a certificate image template (PNG, JPG, JPEG).
- Input names manually (separated by commas or new lines) or upload a CSV/Excel file.
- Live preview of generated certificates with customizable text positioning and font size.
- Download all generated certificates as a ZIP file.
- Supports custom fonts through secure secrets management.

## Prerequisites

Make sure you have Python 3.7 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).

## Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Create a virtual environment (optional but recommended):

Run the Streamlit app:  streamlit run app.py



![image](https://github.com/user-attachments/assets/98156a37-d76a-44f7-bb89-32797bc86975)


![image](https://github.com/user-attachments/assets/dfbbad05-5c8c-46cc-829f-a93807b020e4)


![image](https://github.com/user-attachments/assets/816eaae0-800f-42c2-a871-d3ca60fa249e)


![image](https://github.com/user-attachments/assets/91828b88-5354-46eb-b3ca-c3f4df2af03b)


Open your web browser and navigate to http://localhost:8501 to access the application.

Upload your certificate image template and enter the names you want to include in the certificates. You can either type them in or upload a CSV/Excel file containing the names.

Adjust the font size and text positioning using the provided sliders and inputs.

Preview the certificates in real-time. When you're satisfied, click the "Generate All and Download" button to download all certificates as a ZIP file. 



Acknowledgements
Streamlit - For building interactive web apps easily.
Pillow - For image processing in Python.
pandas - For data manipulation and analysis.

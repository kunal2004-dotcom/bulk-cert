import os
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pdf2image import convert_from_path
from zipfile import ZipFile
import pytesseract
try:
    import cv2
except ImportError:
    st.error("Error loading OpenCV. Please check system dependencies.")
    st.stop()
import numpy as np
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten
except ImportError:
    st.error("Error loading TensorFlow. Please check installation.")
    st.stop()

# ...existing code...

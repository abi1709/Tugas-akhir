import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from scipy import ndimage
import datetime
import pandas as pd
import base64
import random

# Load CSS untuk styling
def load_css():
    st.markdown(
        """
        <style>
        body {
            font-family: Arial, sans-serif;
        }
        .title {
            text-align: center;
            color: #00008B;
            margin-top: 20px;
        }
        .subtitle {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .stButton>button {
            background-color: #00008B;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 0 auto; /* Center the button horizontally */
            display: block; /* Make the button a block element */
        }
        .center-logo {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .center-logo img {
            width: 500px;
            max-width: 100%;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 20px;
        }
        .upload-section {
            text-align: center;
            margin-bottom: 20px;
        }
        .history-section {
            margin-top: 20px;
        }
        @media (max-width: 600px) {
            .title {
                font-size: 44px;
            }
            .subtitle {
                font-size: 18px;
            }
            .stButton>button {
                font-size: 14px;
                padding: 8px 16px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
# Halaman sambutan
def welcome_page():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="title">Selamat Datang di Aplikasi Penghitung Berat Buah</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Klik tombol di bawah ini untuk memulai.</p>', unsafe_allow_html=True)
    
    # Menambahkan logo aplikasi
    logo_path = 'logo_abi.png'
    if os.path.exists(logo_path):
        st.markdown(
            f"""
            <div class="center-logo">
                <img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" alt="Logo Aplikasi">
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Memusatkan tombol menggunakan CSS
    if st.button("Get Started"):
        st.session_state.page = 'main_app'
    
    st.markdown('</div>', unsafe_allow_html=True)

# Fungsi untuk menggambar bounding box (manual untuk kesederhanaan)
def draw_bounding_box(image):
    # Definisikan bounding box (x, y, width, height)
    x, y, w, h = 560, 1275, 1550, 1768  # Sesuaikan nilai-nilai ini berdasarkan gambar Anda
    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return x, y, w, h

def process_image(image):
    # Konversi gambar ke RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Gambar bounding box 
    x, y, w, h = draw_bounding_box(image_rgb)

    # Crop gambar sesuai bounding box
    cropped_image = image_rgb[y:y+h, x:x+w]

    # Konversi gambar ke grayscale
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    # Terapkan threshold untuk segmentasi
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Temukan kontur
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Pilih kontur terbesar (diasumsikan sebagai buah)
    contour = max(contours, key=cv2.contourArea)

    # Gambar kontur pada gambar asli
    cv2.drawContours(cropped_image, [contour], -1, (0, 255, 0), 2)

    # Hitung bounding box dari kontur
    x, y, w, h = cv2.boundingRect(contour)

    # Hitung diameter (diasumsikan sebagai diameter buah)
    diameter = max(w, h)

    # Hitung radius
    radius = diameter / 2.0

    # Hitung luas permukaan bola (BSA) dalam satuan pixel persegi
    bsa = 1 * np.pi * (radius ** 2)

    # Gunakan konstanta proporsionalitas yang bervariasi
    bsa_weight_ratio = random.uniform(0.0005, 0.0012)  

    # Estimasi berat buah
    estimated_weight = bsa * bsa_weight_ratio

    return cropped_image, estimated_weight


# Main app function
def main_app():
    st.markdown('<h1 class="title">Penghitung Berat Buah</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Unggah gambar buah atau ambil gambar menggunakan kamera di bawah ini:", type=['jpg', 'jpeg', 'png'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = np.array(image)
        result_image, estimated_weight = process_image(image)
        st.image(result_image, caption=f'Estimasi Berat Buah: {estimated_weight:.2f} grams', use_column_width=True)

# Kontrol alur halaman dengan state page
if 'page' not in st.session_state:
    st.session_state['page'] = 'welcome'

# Load CSS untuk styling
load_css()

# Pilihan halaman
if st.session_state.page == 'welcome':
    welcome_page()
elif st.session_state.page == 'main_app':
    main_app()
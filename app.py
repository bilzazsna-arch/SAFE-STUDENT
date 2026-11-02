import os, sqlite3, smtplib, ssl, secrets, base64
from datetime import datetime, date, time
from email.message import EmailMessage
from pathlib import Path
import streamlit as st
import pandas as pd

BASE = Path(__file__).resolve().parent
DB = BASE / "safe_student.db"
BK_EMAIL = "bkm2kmendunia@gmail.com"
SENDER = "safestudentm2k@gmail.com"

st.set_page_config(page_title="SAFE-STUDENT | MAN 2 Kudus", page_icon="🐟", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_img_path = BASE / "bg_laut.jpg"
if bg_img_path.exists():
    bg_base64 = get_base64_of_bin_file(bg_img_path)
    bg_css = f"""
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    @media (max-width: 768px) {{
        .stApp {{
            background-size: cover !important;
            background-position: center top !important;
            background-attachment: scroll !important;
        }}
    }}
    """
else:
    bg_css = """
    .stApp {
        background: linear-gradient(180deg, #0284c7 0%, #38bdf8 65%, #e0f2fe 100%);
    }
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bubblegum+Sans&family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');

{bg_css}

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

.block-container {{
    max-width: 1380px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}}

/* Posisi Logo Benar-benar di Tengah */
.logo-center-wrapper {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-bottom: 10px;
}}
.logo-center-wrapper img {{
    max-width: 210px !important;
    height: auto !important;
    object-fit: contain;
}}

/* Posisi Maskot Ganda di Tengah */
.mascot-double-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    width: 100%;
    margin-bottom: 5px;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(7,59,102,0.95) 0%, rgba(7,89,133,0.95) 58%, rgba(14,116,144,0.95) 100%);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.2);
}}
[data-testid="stSidebar"] * {{
    color: white !important;
}}

/* Header Judul Eye-Catching Font Cantik */
.hero-clean {{
    text-align: center;
    padding: 10px 5px;
    margin-bottom: 12px;
}}
.hero-clean .eyebrow {{
    font-family: 'Bubblegum Sans', cursive;
    font-size: clamp(1rem, 2.8vw, 1.3rem);
    letter-spacing: 2px;
    color: #e0f2fe;
    text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    margin-bottom: 2px;
}}
.hero-clean h1 {{
    font-family: 'Pacifico', cursive, sans-serif;
    font-size: clamp(2rem, 5vw, 3.8rem);
    line-height: 1.2;
    margin: 6px 0;
    color: #ffd45c;
    text-shadow: 0 4px 12px rgba(0,

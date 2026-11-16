import os, sqlite3, smtplib, ssl, secrets, base64, random
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bubblegum+Sans&family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1380px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Posisi Logo Benar-benar di Tengah */
.logo-center-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-bottom: 10px;
}
.logo-center-wrapper img {
    max-width: 210px !important;
    height: auto !important;
    object-fit: contain;
}

/* Posisi Maskot Tunggal di Tengah */
.mascot-center-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    text-align: center;
    margin-bottom: 12px;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(7,59,102,0.95) 0%, rgba(7,89,133,0.95) 58%, rgba(14,116,144,0.95) 100%);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.2);
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Header Judul Beling-Beling & Terlihat Jelas (Glow & Sparkle Effect) */
.hero-clean {
    text-align: center;
    padding: 12px 5px;
    margin-bottom: 8px;
}
.hero-clean .eyebrow {
    font-family: 'Bubblegum Sans', cursive;
    font-size: clamp(1.1rem, 3vw, 1.4rem);
    letter-spacing: 2.5px;
    color: #ffffff;
    text-shadow: 0 0 10px #38bdf8, 0 0 20px #0284c7, 0 2px 4px rgba(0,0,0,0.8);
    margin-bottom: 4px;
    font-weight: 700;
}
.hero-clean h1 {
    font-family: 'Pacifico', cursive, sans-serif;
    font-size: clamp(2.2rem, 5.5vw, 4rem);
    line-height: 1.2;
    margin: 6px 0;
    color: #fffbeb;
    text-shadow: 0 0 12px #fde047, 0 0 25px #eab308, 0 4px 10px rgba(0, 0, 0, 0.8);
}
.hero-clean p {
    font-family: 'Bubblegum Sans', cursive;
    color: #ffffff;
    font-size: clamp(1.2rem, 3.2vw, 1.6rem);
    text-shadow: 0 0 8px #7dd3fc, 0 2px 6px rgba(0,0,0,0.8);
    margin-bottom: 0;
}

/* STYLING TAB MENU AGAR EYE-CATCHING & JELAS */
[data-testid="stTabs"] button {
    font-family: 'Fredoka', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    color: #073b66 !important;
    background-color: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 14px 14px 0 0 !important;
    padding: 12px 22px !important;
    margin-right: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.2s ease;
}
[data-testid="stTabs"] button:hover {
    background-color: #e0f2fe !important;
    color: #0284c7 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(90deg, #0284c7, #0891b2) !important;
    color: #ffffff !important;
    border-color: #0284c7 !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45) !important;
    transform: translateY(-2px);
}

/* Panel & Card Styling */
.panel {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(10px);
    border: 2px solid #38bdf8;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 10px 28px rgba(8, 59, 102, 0.22);
}

.metric {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #bae6fd;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(8, 59, 102, 0.1);
}
.metric .num {
    font-family: 'Fredoka', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #0284c7;
}

.muted {
    color: #1e293b;
    font-size: 1.05rem;
    font-weight: 500;
}

/* Button & Form */
div.stButton > button, div.stFormSubmitButton > button {
    border: 0;
    border-radius: 14px;
    background: linear-gradient(90deg, #0284c7, #0891b2);
    color: white;
    font-weight: 700;
    min-height: 2.8rem;
    box-shadow: 0 6px 16px rgba(2, 132, 199, 0.35);
    transition: transform 0.15s ease;
    width: 100%;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    color: white;
    transform: translateY(-2px);
}

div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.96);
    border: 1.5px solid #bae6fd;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(8, 59, 102, 0.15);
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

[data-testid="stImage"] {
    display: flex;
    justify-content: center;
    align-items: center;
}

[data-testid="stImage"] img {
    object-fit: contain;
    margin: 0 auto;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    .panel {
        padding: 16px !important;
        border-radius: 18px !important;
    }
}
</style>
""" + f"""
<style>
{bg_css}
</style>
""", unsafe_allow_html=True)

def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def now(): 
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, created TEXT, category TEXT,
        content TEXT, urgency TEXT, score INTEGER, status TEXT DEFAULT 'Baru',
        student_email TEXT, requested TEXT, final_schedule TEXT,
        schedule_status TEXT DEFAULT 'Belum diajukan', bk_note TEXT, updated TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS email_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, recipient TEXT, subject TEXT,
        event TEXT, code TEXT, status TEXT, detail TEXT)""")
        c.commit()
init_db()

def cfg():
    try:
        e = st.secrets.get("email", {})
        return {"sender": e.get("sender", SENDER), "password": e.get("app_password", ""),
                "recipient": e.get("recipient", BK_EMAIL), "host": e.get("smtp_host", "smtp.gmail.com"),
                "port": int(e.get("smtp_port", 465))}
    except Exception:
        return {"sender": os.getenv("SAFE_EMAIL_SENDER", SENDER),
                "password": os.getenv("SAFE_EMAIL_APP_PASSWORD", ""),
                "recipient": os.getenv("SAFE_EMAIL_RECIPIENT", BK_EMAIL),
                "host": "smtp.gmail.com", "port": 465}

def log_mail(to, subject, event, code, status, detail=""):
    with connect() as c:
        c.execute("INSERT INTO email_log(created,recipient,subject,event,code,status,detail) VALUES(?,?,?,?,?,?,?)",
                  (now(), to, subject, event, code, status, detail[:300]))
        c.commit()

def email(to, subject, body, event, code=""):
    conf = cfg()
    if not to or "@" not in str(to):
        log_mail(str(to or "(kosong)"), subject, event, code, "Gagal", "Alamat penerima tidak valid")
        return False, "Alamat email penerima tidak valid."
    if not conf["password"]:
        log_mail(to, subject, event, code, "Belum dikonfigurasi", "App Password belum diisi")
        return False, "Email belum dikonfigurasi. Isi app_password di .streamlit/secrets.toml."
    try:
        msg = EmailMessage()
        msg["From"] = conf["sender"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        host, port = conf["host

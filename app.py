import os, sqlite3, smtplib, ssl, secrets
from datetime import datetime, date, time
from email.message import EmailMessage
from pathlib import Path
import streamlit as st
import pandas as pd

BASE = Path(__file__).resolve().parent
DB = BASE / "safe_student.db"
BK_EMAIL = "bkm2kmendunia@gmail.com"
SENDER = "safestudentm2k@gmail.com"

st.set_page_config(page_title="SAFE-STUDENT | MAN 2 Kudus", page_icon="🦀", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap');

:root{
    --navy:#073b66;
    --blue:#087fa8;
    --cyan:#16b8c8;
    --gold:#ffd45c;
    --ink:#12344a;
}

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Background Nuansa Bawah Laut Cerah & Segar */
.stApp {
    background: linear-gradient(180deg, #0284c7 0%, #0284c7 25%, #38bdf8 65%, #e0f2fe 100%);
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1400px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #073b66 0%, #075985 58%, #0e7490 100%);
    border-right: 1px solid rgba(255,255,255,0.1);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px 12px;
    border-radius: 12px;
    transition: background 0.2s;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* Hero Banner Utama */
.hero {
    background: linear-gradient(120deg, #073b66 0%, #087fa8 60%, #0891b2 100%);
    color: white;
    border-radius: 28px;
    padding: 26px 36px;
    margin: 8px 0 22px 0;
    box-shadow: 0 16px 36px rgba(6, 75, 108, 0.25);
    border: 2px solid rgba(255, 255, 255, 0.25);
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero h1 {
    font-family: 'Fredoka', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.8rem);
    line-height: 1.1;
    margin: 6px 0;
    color: #ffd45c;
    text-shadow: 0 3px 6px rgba(0,0,0,0.2);
}
.hero p {
    color: #e7f9ff;
    font-size: 1.05rem;
    margin-bottom: 0;
}

/* Panel & Card Styling */
.panel {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(8, 59, 102, 0.12);
}

.metric {
    background: linear-gradient(145deg, #ffffff, #f0f9ff);
    border: 1px solid #bae6fd;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(8, 59, 102, 0.08);
}
.metric .num {
    font-family: 'Fredoka', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #0284c7;
}

.muted {
    color: #475569;
    font-size: 0.95rem;
}

/* Buttons & Forms */
div.stButton > button, div.stFormSubmitButton > button {
    border: 0;
    border-radius: 14px;
    background: linear-gradient(90deg, #0284c7, #0891b2);
    color: white;
    font-weight: 700;
    min-height: 2.8rem;
    box-shadow: 0 6px 16px rgba(2, 132, 199, 0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    width: 100%;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(2, 132, 199, 0.4);
}

div[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 24px rgba(8, 59, 102, 0.08);
}

[data-testid="stTabs"] button {
    font-weight: 700;
    font-size: 1rem;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

[data-testid="stImage"] img {
    object-fit: contain;
}

@media(max-width: 700px) {
    .block-container { padding: 1rem 0.6rem; }
    .hero { padding: 20px 16px; border-radius: 20px; }
    .hero h1 { font-size: 2.2rem; }
}
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
        host, port = conf["host"], int(conf["port"])
        context = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=context, timeout=25) as server:
                server.ehlo()
                server.login(conf["sender"], conf["password"].replace(" ", ""))
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=25) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(conf["sender"], conf["password"].replace(" ", ""))
                server.send_message(msg)
        log_mail(to, subject, event, code, "Terkirim", "SMTP menerima pesan untuk dikirim")
        return True, f"Email berhasil diserahkan ke server email untuk {to}."
    except Exception as ex:
        detail = f"{type(ex).__name__}: {str(ex)[:220]}"
        log_mail(to, subject, event, code, "Gagal", detail)
        return False, f"Email gagal dikirim ({type(ex).__name__})."

def mail_bk(code, category, urgency):
    to = cfg()["recipient"]
    body = f"""Halo Guru BK MAN 2 Kudus,

Ada laporan baru di SAFE-STUDENT.
Kode laporan: {code}

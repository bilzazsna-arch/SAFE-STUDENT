import os
import sqlite3
import smtplib
import ssl
import secrets
import base64
import html
from datetime import datetime, date, time
from email.message import EmailMessage
from pathlib import Path

import streamlit as st
import pandas as pd


# =========================================================
# 1. KONFIGURASI UTAMA
# =========================================================

BASE = Path(__file__).resolve().parent
DB = BASE / "safe_student.db"

BK_EMAIL = "bkm2kmendunia@gmail.com"
SENDER = "safestudentm2k@gmail.com"

st.set_page_config(
    page_title="SAFE-STUDENT | MAN 2 Kudus",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mencari gambar berdasarkan beberapa kemungkinan nama file.
def cari_file(*nama_file):
    for nama in nama_file:
        path = BASE / nama
        if path.exists():
            return path
    return None


LOGO = cari_file(
    "Logo_MAN2.png",
    "logo_man2.png",
    "logo_gabungan.png"
)

BACKGROUND = cari_file(
    "bg_laut.jpg",
    "bg_laut.png",
    "background_laut.jpg"
)

KEMA = cari_file(
    "ubur_cewe.png",
    "kepiting_cewe.png",
    "kema.png"
)

TEMO = cari_file(
    "kepiting_cowo.png",
    "kepiting_cowok.png",
    "temo.png"
)


def gambar_base64(path):
    if not path or not path.exists():
        return ""

    ekstensi = path.suffix.lower()
    tipe = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }.get(ekstensi, "image/png")

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{tipe};base64,{data}"


LOGO_URI = gambar_base64(LOGO)
BG_URI = gambar_base64(BACKGROUND)
KEMA_URI = gambar_base64(KEMA)
TEMO_URI = gambar_base64(TEMO)


# =========================================================
# 2. CSS DESAIN WEBSITE
# =========================================================

css_background = (
    f'url("{BG_URI}")'
    if BG_URI
    else "linear-gradient(145deg, #06365d, #087da6, #c9f3ff)"
)

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap'
    );

    :root {{
        --navy: #06365d;
        --blue: #087ca8;
        --cyan: #26c6da;
        --yellow: #ffdc42;
        --white: #ffffff;
        --text: #173c55;
    }}

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    .stApp {{
        background-image:
            linear-gradient(
                180deg,
                rgba(2, 35, 66, .58),
                rgba(2, 64, 99, .42),
                rgba(3, 54, 85, .68)
            ),
            {css_background};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: var(--text);
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stToolbar"] {{
        right: 1rem;
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }}

    /* SIDEBAR */

    [data-testid="stSidebar"] {{
        background: linear-gradient(
            180deg,
            #052e50 0%,
            #075985 52%,
            #087e9c 100%
        );
        border-right: 1px solid rgba(255,255,255,.18);
    }}

    [data-testid="stSidebar"] * {{
        color: #ffffff;
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        line-height: 1.65;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,.23);
    }}

    [data-testid="stSidebar"] [role="radiogroup"] {{
        gap: 8px;
    }}

    [data-testid="stSidebar"] [role="radio"] {{
        background: rgba(255,255,255,.07);
        border-radius: 12px;
        padding: 10px;
    }}

    [data-testid="stSidebar"] [role="radio"]:has(
        input:checked
    ) {{
        background: rgba(255,255,255,.2);
        border: 1px solid rgba(255,255,255,.45);
    }}

    /* LOGO SEKOLAH */

    .logo-area {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 4px auto 15px auto;
        padding: 5px 0;
    }}

    .school-logo {{
        display: block;
        width: min(420px, 90%);
        max-height: 150px;
        object-fit: contain;
        filter: drop-shadow(0 5px 12px rgba(0,0,0,.25));
    }}

    /* JUDUL UTAMA */

    .brand-top {{
        text-align: center;
        color: #e9fbff;
        font-size: clamp(.72rem, 1.5vw, 1rem);
        font-weight: 700;
        letter-spacing: 4px;
        text-shadow: 0 2px 8px rgba(0,0,0,.4);
        margin: 4px 0;
    }}

    .brand-title {{
        text-align: center;
        line-height: 1.05;
        margin: 5px auto 8px auto;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(2.8rem, 7vw, 6rem);
        font-weight: 700;
        color: #ffdf43;
        text-shadow:
            0 3px 0 #e99a16,
            0 6px 0 #064b77,
            0 10px 18px rgba(0,0,0,.38);
        overflow-wrap: anywhere;
    }}

    .brand-subtitle {{
        text-align: center;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(1.35rem, 3.5vw, 2.5rem);
        font-weight: 600;
        color: #ffffff;
        text-shadow:
            0 3px 0 #075985,
            0 5px 12px rgba(0,0,0,.35);
        margin-bottom: 12px;
    }}

    .brand-caption {{
        text-align: center;
        max-width: 700px;
        margin: 0 auto 20px auto;
        color: #effcff;
        font-size: .92rem;
        line-height: 1.8;
        text-shadow: 0 2px 5px rgba(0,0,0,.35);
    }}

    /* BAGIAN KEMA, SAMBUTAN, TEMO */

    .character-name {{
        text-align: center;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(1.15rem, 2vw, 1.55rem);
        font-weight: 700;
        color: #ffdf43;
        text-shadow: 0 3px 8px rgba(0,0,0,.45);
        margin-top: 2px;
    }}

    .character-caption {{
        text-align: center;
        color: #ffffff;
        font-size: .78rem;
        font-weight: 500;
        margin-bottom: 8px;
        text-shadow: 0 2px 5px rgba(0,0,0,.4);
    }}

    .mascot {{
        width: 100%;
        max-width: 250px;
        max-height: 300px;
        object-fit: contain;
        display: block;
        margin: 0 auto;
        filter: drop-shadow(0 9px 12px rgba(0,0,0,.25));
    }}

    .greeting-card {{
        background: rgba(255,255,255,.96);
        border: 2px solid rgba(255,255,255,.8);
        border-radius: 26px;
        padding: 24px 22px;
        margin: 14px auto;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,25,55,.2);
    }}

    .greeting-card h2 {{
        color: #075985;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(1.25rem, 2.5vw, 1.85rem);
        line-height: 1.3;
        margin: 0 0 12px 0;
    }}

    .greeting-card p {{
        color: #426277;
        font-size: .9rem;
        line-height: 1.8;
        margin-bottom: 8px;
    }}

    .welcome-pill {{
        display: inline-block;
        background: #e0f7ff;
        color: #075985;
        border-radius: 30px;
        padding: 7px 13px;
        font-size: .78rem;
        font-weight: 700;
        margin-bottom: 12px;
    }}

    /* KARTU FORMULIR */

    .section-banner {{
        background: linear-gradient(110deg, #ffffff, #e9faff);
        border: 1px solid #d1eff8;
        border-left: 6px solid #0c91bb;
        border-radius: 17px;
        padding: 18px 20px;
        margin: 12px 0 18px 0;
        box-shadow: 0 8px 25px rgba(0,30,65,.12);
    }}

    .section-banner h2,
    .section-banner h3 {{
        color: #075985;
        font-family: 'Fredoka', sans-serif;
        margin: 0 0 7px 0;
    }}

    .section-banner p {{
        color: #587789;
        margin: 0;
        font-size: .88rem;
        line-height: 1.7;
    }}

    .panel {{
        background: rgba(255,255,255,.97);
        border: 1px solid #d7edf7;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 9px 26px rgba(0,35,70,.12);
    }}

    .metric {{
        background: rgba(255,255,255,.97);
        border: 1px solid #d7edf7;
        border-radius: 18px;
        padding: 17px;
        min-height: 110px;
        box-shadow: 0 7px 20px rgba(0,35,70,.09);
    }}

    .metric-label {{
        font-size: .85rem;
        color: #587789;
    }}

    .metric-number {{
        font-size: 2rem;
        font-weight: 800;
        color: #075985;
    }}

    .muted {{
        color: #587789;
        font-size: .88rem;
        line-height: 1.7;
    }}

    /* FORM STREAMLIT */

    div[data-testid="stForm"] {{
        background: rgba(255,255,255,.98);
        border: 1px solid #d7edf7;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(0,35,70,.1);
    }}

    [data-testid="stTabs"] [role="tablist"] {{
        gap: 8px;
    }}

    [data-testid="stTabs"] button[role="tab"] {{
        border-radius: 12px 12px 5px 5px;
        padding: 10px 14px;
        font-weight: 600;
    }}

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input {{
        border-radius: 11px;
    }}

    div.stButton > button,
    div.stFormSubmitButton > button {{
        background: linear-gradient(100deg, #0879b9, #08a1b7);
        color: white;
        border: none;
        border-radius: 12px;
        min-height: 44px;
        font-weight: 700;
        transition: .2s ease;
    }}

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {{
        background: linear-gradient(100deg, #065985, #087c9c);
        color: white;
        border: none;
        transform: translateY(-1px);
    }}

    [data-testid="stDataFrame"] {{
        background: white;
        border-radius: 12px;
        overflow: hidden;
    }}

    .footer {{
        text-align: center;
        color: #f0fcff;
        font-size: .78rem;
        padding: 28px 8px 10px 8px;
        text-shadow: 0 2px 5px rgba(0,0,0,.4);
    }}

    /* RESPONSIF HP */

    @media (max-width: 768px) {{
        .block-container {{
            padding: 1rem .8rem 1rem .8rem;
        }}

        .school-logo {{
            width: min(300px, 90%);
            max-height: 110px;
        }}

        .brand-top {{
            letter-spacing: 2px;
        }}

        .greeting-card {{
            padding: 18px 15px;
            margin: 8px 0 18px 0;
        }}

        .mascot {{
            max-width: 185px;
            max-height: 230px;
        }}

        .panel,
        div[data-testid="stForm"] {{
            padding: 15px;
        }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        * {{
            transition: none !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 3. DATABASE
# =========================================================

def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                created TEXT,
                category TEXT,
                content TEXT,
                urgency TEXT,
                score INTEGER,
                status TEXT DEFAULT 'Baru',
                student_email TEXT,
                requested TEXT,
                final_schedule TEXT,
                schedule_status TEXT DEFAULT 'Belum diajukan',
                bk_note TEXT,
                updated TEXT
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT,
                recipient TEXT,
                subject TEXT,
                event TEXT,
                code TEXT,
                status TEXT,
                detail TEXT
            )
        """)

        con.commit()


init_db()


# =========================================================
# 4. KONFIGURASI EMAIL
# =========================================================

def cfg():
    try:
        email_secrets = st.secrets.get("email", {})

        return {
            "sender": email_secrets.get("sender", SENDER),
            "password": email_secrets.get("app_password", ""),
            "recipient": email_secrets.get("recipient", BK_EMAIL),
            "host": email_secrets.get("smtp_host", "smtp.gmail.com"),
            "port": int(email_secrets.get("smtp_port", 465))
        }

    except Exception:
        return {
            "sender": os.getenv("SAFE_EMAIL_SENDER", SENDER),
            "password": os.getenv("SAFE_EMAIL_APP_PASSWORD", ""),
            "recipient": os.getenv("SAFE_EMAIL_RECIPIENT", BK_EMAIL),
            "host": "smtp.gmail.com",
            "port": 465
        }


def log_mail(to, subject, event, code, status, detail=""):
    with connect() as con:
        con.execute("""
            INSERT INTO email_log
            (created, recipient, subject, event, code, status, detail)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            now(), to, subject, event, code, status, detail[:300]
        ))
        con.commit()


def email(to, subject, body, event, code=""):
    conf = cfg()

    if not conf["password"]:
        log_mail(
            to, subject, event, code,
            "Belum dikonfigurasi",
            "App Password belum diatur"
        )
        return False, "Email belum dikonfigurasi di Secrets."

    try:
        msg = EmailMessage()
        msg["From"] = conf["sender"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL(
            conf["host"],
            conf["port"],
            context=ssl.create_default_context(),
            timeout=20
        ) as server:
            server.login(conf["sender"], conf["password"])
            server.send_message(msg)

        log_mail(to, subject, event, code, "Terkirim")
        return True, "Email berhasil dikirim."

    except Exception as ex:
        log_mail(to, subject, event, code, "Gagal", str(ex))
        return False, "Email gagal dikirim. Periksa pengaturan Gmail."


def mail_bk(code, category, urgency):
    recipient = cfg()["recipient"]

    body = f"""
Halo Guru BK MAN 2 Kudus,

Ada laporan baru di SAFE-STUDENT.

Kode laporan: {code}
Kategori: {category}
Penanda urgensi otomatis: {urgency}

Isi curhat tidak disertakan dalam email demi menjaga privasi.
Silakan buka dashboard Guru BK untuk meninjau laporan.

SAFE-STUDENT MAN 2 Kudus
"""

    return email(
        recipient,
        f"[SAFE-STUDENT] Laporan baru {code}",
        body,
        "Laporan baru",
        code
    )


def mail_student(to, code, schedule, note=""):
    body = f"""
Halo,

Pengajuan jadwal konseling kamu telah disetujui Guru BK MAN 2 Kudus.

Kode pengajuan: {code}
Jadwal: {schedule}
Lokasi: Ruang BK MAN 2 Kudus.

Catatan: jika tidak dapat hadir, hubungi Guru BK untuk mengatur ulang jadwal.
Email ini tidak memuat isi curhat.

SAFE-STUDENT MAN 2 Kudus
"""

    if note.strip():
        body += "\nCatatan untuk kamu: " + note.strip()

    return email(
        to,
        f"[SAFE-STUDENT] Jadwal disetujui - {code}",
        body,
        "Persetujuan jadwal",
        code
    )


# =========================================================
# 5. FUNGSI LAPORAN
# =========================================================

def score_text(text):
    text = text.lower()

    high = [
        "diancam", "dipukul", "kekerasan",
        "takut pulang", "tidak aman"
    ]

    medium = [
        "bullying", "dibully", "cemas",
        "panik", "stres", "tertekan",
        "sedih", "konflik"
    ]

    score = (
        3 * sum(word in text for word in high)
        + sum(word in text for word in medium)
    )

    if score >= 3:
        return "MERAH", score

    if score > 0:
        return "KUNING", score

    return "HIJAU", score


def get_reports():
    with connect() as con:
        return pd.read_sql_query(
            "SELECT * FROM reports ORDER BY created DESC",
            con
        )


def update_report(code, **kwargs):
    allowed = {
        "status",
        "final_schedule",
        "schedule_status",
        "bk_note"
    }

    values = {
        key: value
        for key, value in kwargs.items()
        if key in allowed
    }

    values["updated"] = now()

    with connect() as con:
        con.execute(
            "UPDATE reports SET "
            + ", ".join(key + " = ?" for key in values)
            + " WHERE code = ?",
            list(values.values()) + [code]
        )
        con.commit()


# =========================================================
# 6. KOMPONEN TAMPILAN
# =========================================================

def show_hero(title, subtitle):
    if LOGO_URI:
        st.markdown(
            f"""
            <div class="logo-area">
                <img class="school-logo" src="{LOGO_URI}">
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="brand-top">
            SAFE-STUDENT · MAN 2 KUDUS
        </div>

        <div class="brand-title">
            {html.escape(title)}
        </div>

        <div class="brand-subtitle">
            Digital MAN
        </div>

        <div class="brand-caption">
            {html.escape(subtitle)}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_section(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-banner">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_character(uri, name, caption):
    if uri:
        st.markdown(
            f"""
            <img class="mascot" src="{uri}">
            <div class="character-name">{html.escape(name)}</div>
            <div class="character-caption">{html.escape(caption)}</div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="character-name">{html.escape(name)}</div>
            <div class="character-caption">
                Gambar belum ditemukan di folder aplikasi.
            </div>
            """,
            unsafe_allow_html=True
        )


def show_metric(label, value):
    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-number">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def check_password(secret_name, state_name, label):
    if st.session_state.get(state_name, False):
        return True

    with st.expander(
        f"🔐 Masuk {label}",
        expanded=True
    ):
        password = st.text_input(
            f"Kata sandi {label}",
            type="password",
            key=f"pw_{state_name}"
        )

        if st.button(f"Masuk {label}", key=f"login_{state_name}"):
            try:
                expected = st.secrets.get("auth", {}).get(
                    secret_name, ""
                )
            except Exception:
                expected = ""

            if expected and secrets.compare_digest(password, expected):
                st.session_state[state_name] = True
                st.rerun()
            else:
                st.error(
                    "Kata sandi salah atau belum diatur di Secrets."
                )

    return False


# ===========================================

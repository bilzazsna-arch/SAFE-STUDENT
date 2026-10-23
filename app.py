import os
import ssl
import smtplib
import secrets
import base64
import html
from pathlib import Path
from datetime import datetime, date, time
from email.message import EmailMessage

import pandas as pd
import streamlit as st


# =========================================================
# 1. KONFIGURASI
# =========================================================

st.set_page_config(
    page_title="SAFE-STUDENT | MAN 2 Kudus",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).resolve().parent

REPORT_FILE = BASE / "db_laporan.csv"
APPOINTMENT_FILE = BASE / "db_jadwal.csv"
EMAIL_LOG_FILE = BASE / "db_email.csv"

BK_EMAIL = "bkm2kmendunia@gmail.com"
SENDER_EMAIL = "safestudentm2k@gmail.com"

LOGO_FILE = "Logo_MAN2.png"
BG_FILE = "bg_laut.jpg"
KEMA_FILE = "ubur_cewe.png"
TEMO_FILE = "kepiting_cowo.png"


# =========================================================
# 2. STRUKTUR DATA
# =========================================================

REPORT_COLUMNS = [
    "ID_Kasus",
    "Waktu",
    "Kategori",
    "Isi_Laporan",
    "Status_Urgensi",
    "Skor_Urgensi",
    "Status_Kasus",
    "Catatan_Guru_BK",
    "Catatan_Rekam_Medis_BK",
    "Kontak_Opsional",
    "Notifikasi_Email",
]

APPOINTMENT_COLUMNS = [
    "ID_Jadwal",
    "Waktu_Dibuat",
    "ID_Kasus",
    "Tanggal",
    "Jam",
    "Nama_Panggilan",
    "Kontak_Opsional",
    "Email_Siswa",
    "Catatan",
    "Status_Jadwal",
    "Jadwal_Final",
    "Catatan_Guru_BK",
    "Notifikasi_Email",
]

EMAIL_COLUMNS = [
    "Waktu",
    "Penerima",
    "Subjek",
    "Jenis",
    "ID_Referensi",
    "Status",
    "Detail",
]


def waktu_sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def baca_csv(path, columns):
    """Membaca CSV lama dan menambahkan kolom baru tanpa menghapus kolom lama."""
    if path.exists():
        try:
            df = pd.read_csv(path, dtype=str).fillna("")

            for col in columns:
                if col not in df.columns:
                    df[col] = ""

            # Pertahankan kolom lama serta kolom baru.
            urutan = list(columns) + [
                col for col in df.columns if col not in columns
            ]
            return df[urutan]

        except Exception:
            st.error(
                f"File {path.name} tidak dapat dibaca. "
                "Periksa file sebelum melanjutkan."
            )

    return pd.DataFrame(columns=columns)


def simpan_csv(path, df):
    df.to_csv(path, index=False, encoding="utf-8-sig")


def load_reports():
    return baca_csv(REPORT_FILE, REPORT_COLUMNS)


def load_appointments():
    return baca_csv(APPOINTMENT_FILE, APPOINTMENT_COLUMNS)


def load_email_logs():
    return baca_csv(EMAIL_LOG_FILE, EMAIL_COLUMNS)


def save_reports(df):
    simpan_csv(REPORT_FILE, df)


def save_appointments(df):
    simpan_csv(APPOINTMENT_FILE, df)


def save_email_logs(df):
    simpan_csv(EMAIL_LOG_FILE, df)


# =========================================================
# 3. GAMBAR LOKAL
# =========================================================

def image_uri(filename):
    path = BASE / filename

    if not path.exists():
        return ""

    ext = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "image/png")

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


LOGO_URI = image_uri(LOGO_FILE)
BG_URI = image_uri(BG_FILE)
KEMA_URI = image_uri(KEMA_FILE)
TEMO_URI = image_uri(TEMO_FILE)


# =========================================================
# 4. CSS — DESAIN UTAMA
# =========================================================

background_css = (
    f'url("{BG_URI}")'
    if BG_URI
    else "linear-gradient(135deg,#073b66,#0785aa,#bcefff)"
)

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap'
    );

    :root {{
        --navy: #073b66;
        --blue: #087ca8;
        --cyan: #25c6da;
        --yellow: #ffdc42;
        --ink: #173c55;
    }}

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(
                rgba(2,36,65,.48),
                rgba(2,54,83,.42)
            ),
            {background_css};
        background-position: center;
        background-size: cover;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
    }}

    /* SIDEBAR */

    [data-testid="stSidebar"] {{
        background: linear-gradient(
            180deg,
            #052e50,
            #075985,
            #087f9d
        );
        border-right: 1px solid rgba(255,255,255,.2);
    }}

    [data-testid="stSidebar"] * {{
        color: white;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,.25);
    }}

    [data-testid="stSidebar"] [role="radio"] {{
        padding: 9px;
        border-radius: 12px;
    }}

    [data-testid="stSidebar"] [role="radio"]:has(input:checked) {{
        background: rgba(255,255,255,.18);
    }}

    /* LOGO */

    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 3px auto 18px;
    }}

    .logo-school {{
        display: block;
        width: min(430px, 92%);
        max-height: 150px;
        object-fit: contain;
        filter: drop-shadow(0 5px 10px rgba(0,0,0,.25));
    }}

    /* JUDUL */

    .eyebrow {{
        color: #f0fcff;
        text-align: center;
        letter-spacing: 3px;
        font-size: .82rem;
        font-weight: 700;
        text-shadow: 0 2px 6px #002c49;
    }}

    .title-curhatin {{
        text-align: center;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(3rem, 7vw, 6.1rem);
        font-weight: 700;
        line-height: 1.05;
        margin: 5px 0;
        color: #ffdf43;
        text-shadow:
            0 3px 0 #e99a16,
            0 6px 0 #075985,
            0 10px 18px rgba(0,0,0,.35);
    }}

    .title-digital {{
        text-align: center;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(1.8rem, 4vw, 3.2rem);
        font-weight: 700;
        color: #fff;
        margin: 0;
        text-shadow:
            0 3px 0 #0784bb,
            0 6px 12px rgba(0,0,0,.4);
    }}

    .title-safe {{
        display: table;
        margin: 12px auto 25px;
        padding: 8px 18px;
        border-radius: 30px;
        background: rgba(4,54,91,.92);
        border: 1px solid rgba(255,255,255,.85);
        color: white;
        font-size: .88rem;
        font-weight: 600;
        text-align: center;
    }}

    /* MASKOT */

    .mascot {{
        width: 100%;
        text-align: center;
    }}

    .mascot img {{
        display: block;
        width: 100%;
        max-width: 245px;
        max-height: 310px;
        object-fit: contain;
        margin: 0 auto;
        filter: drop-shadow(0 8px 11px rgba(0,0,0,.27));
    }}

    .mascot-name {{
        display: inline-block;
        margin-top: 7px;
        padding: 5px 24px;
        background: #fff;
        color: #075985;
        border: 2px solid #d8f3ff;
        border-radius: 20px;
        font-family: 'Fredoka', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(0,0,0,.16);
    }}

    /* KARTU SAMBUTAN */

    .welcome-card {{
        background: rgba(255,255,255,.97);
        border: 3px solid #d7f0ff;
        border-radius: 26px;
        padding: 25px 22px;
        margin: 12px auto;
        text-align: center;
        box-shadow: 0 12px 28px rgba(0,24,50,.2);
    }}

    .welcome-tag {{
        display: inline-block;
        background: #e2f8ff;
        color: #087ca8;
        border-radius: 30px;
        padding: 6px 12px;
        font-size: .75rem;
        font-weight: 700;
        margin-bottom: 10px;
    }}

    .welcome-title {{
        color: #075985;
        font-family: 'Fredoka', sans-serif;
        font-size: clamp(1.3rem, 2.4vw, 1.9rem);
        line-height: 1.3;
        font-weight: 700;
        margin-bottom: 12px;
    }}

    .welcome-copy {{
        color: #426277;
        font-size: .88rem;
        line-height: 1.9;
    }}

    /* KARTU DAN FORM */

    .section-card {{
        background: linear-gradient(120deg,#fff,#eafaff);
        border: 1px solid #ccecf8;
        border-left: 6px solid #0b91ba;
        border-radius: 17px;
        padding: 18px 20px;
        margin: 10px 0 18px;
        box-shadow: 0 8px 20px rgba(0,35,70,.1);
    }}

    .section-card h3 {{
        font-family: 'Fredoka', sans-serif;
        color: #075985;
        margin: 0 0 7px;
    }}

    .section-card p {{
        color: #587789;
        font-size: .86rem;
        line-height: 1.7;
        margin: 0;
    }}

    .panel-card {{
        background: rgba(255,255,255,.97);
        color: #173c55;
        border: 1px solid #d7edf7;
        border-radius: 19px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 24px rgba(0,35,70,.11);
    }}

    .panel-card h3 {{
        color: #075985;
        font-family: 'Fredoka', sans-serif;
    }}

    .metric-card {{
        background: rgba(255,255,255,.97);
        border: 1px solid #d7edf7;
        border-radius: 17px;
        padding: 17px;
        min-height: 95px;
        box-shadow: 0 7px 18px rgba(0,35,70,.1);
    }}

    .metric-label {{
        color: #587789;
        font-size: .82rem;
    }}

    .metric-value {{
        color: #075985;
        font-size: 1.9rem;
        font-weight: 800;
    }}

    div[data-testid="stForm"] {{
        background: rgba(255,255,255,.98);
        border: 1px solid #d7edf7;
        border-radius: 19px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0,35,70,.1);
    }}

    [data-testid="stTabs"] [role="tablist"] {{
        gap: 8px;
        background: rgba(255,255,255,.94);
        border-radius: 15px;
        padding: 7px;
    }}

    [data-testid="stTabs"] button[role="tab"] {{
        border-radius: 11px;
        font-weight: 600;
    }}

    div.stButton > button,
    div.stFormSubmitButton > button {{
        border: none;
        border-radius: 12px;
        min-height: 43px;
        background: linear-gradient(100deg,#0879b9,#08a1b7);
        color: white;
        font-weight: 700;
    }}

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {{
        background: linear-gradient(100deg,#075985,#087c9c);
        color: white;
        border: none;
    }}

    [data-testid="stDataFrame"] {{
        background: white;
        border-radius: 12px;
    }}

    .footer {{
        text-align: center;
        color: white;
        font-size: .78rem;
        padding: 25px 5px 10px;
        text-shadow: 0 2px 6px #00304b;
    }}

    @media(max-width: 768px) {{
        .block-container {{
            padding: 1rem .75rem;
        }}

        .logo-school {{
            width: min(300px, 92%);
            max-height: 105px;
        }}

        .mascot img {{
            max-width: 170px;
            max-height: 220px;
        }}

        .welcome-card {{
            padding: 17px 14px;
        }}

        .panel-card,
        div[data-testid="stForm"] {{
            padding: 14px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. EMAIL DAN SECRETS
# =========================================================

def get_secret(section, key, default=""):
    try:
        return str(st.secrets.get(section, {}).get(key, default))
    except Exception:
        return default


def email_config():
    return {
        "host": get_secret("email", "smtp_host", "smtp.gmail.com"),
        "port": int(get_secret("email", "smtp_port", "465")),
        "sender": get_secret("email", "sender", SENDER_EMAIL),
        "password": get_secret("email", "app_password", ""),
        "recipient": get_secret("email", "recipient", BK_EMAIL),
    }


def log_email(to, subject, kind, reference, status, detail=""):
    df = load_email_logs()

    row = {
        "Waktu": waktu_sekarang(),
        "Penerima": to,
        "Subjek": subject,
        "Jenis": kind,
        "ID_Referensi": reference,
        "Status": status,
        "Detail": detail[:250],
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_email_logs(df)


def send_email(to, subject, body, kind, reference=""):
    conf = email_config()

    if not conf["password"]:
        log_email(
            to, subject, kind, reference,
            "Belum dikonfigurasi",
            "App Password belum diatur."
        )
        return False, "App Password email belum diatur di Secrets."

    try:
        message = EmailMessage()
        message["From"] = conf["sender"]
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP_SSL(
            conf["host"],
            conf["port"],
            context=ssl.create_default_context(),
            timeout=20,
        ) as server:
            server.login(conf["sender"], conf["password"])
            server.send_message(message)

        log_email(to, subject, kind, reference, "Terkirim")
        return True, "Email berhasil dikirim."

    except Exception as exc:
        log_email(
            to, subject, kind, reference,
            "Gagal", type(exc).__name__
        )
        return False, "Email gagal dikirim. Periksa konfigurasi email."


def notify_bk_report(report_id, category, urgency, created):
    conf = email_config()

    body = f"""
Halo Guru BK MAN 2 Kudus,

Ada laporan baru di SAFE-STUDENT.

Kode laporan: {report_id}
Waktu: {created}
Kategori: {category}
Indikator urgensi: {urgency}

Isi curhat tidak disertakan dalam email untuk menjaga privasi.
Silakan buka dashboard Guru BK untuk meninjau laporan.

SAFE-STUDENT MAN 2 Kudus
"""

    return send_email(
        conf["recipient"],
        f"[SAFE-STUDENT] Laporan baru {report_id}",
        body,
        "Laporan baru",
        report_id,
    )


def notify_bk_appointment(appointment_id, report_id, requested):
    conf = email_config()

    body = f"""
Halo Guru BK MAN 2 Kudus,

Ada pengajuan jadwal konseling baru.

Kode jadwal: {appointment_id}
Kode laporan terkait: {report_id or 'Tidak dihubungkan'}
Waktu yang diminta: {requested}

Silakan tinjau dan perbarui pengajuan melalui dashboard Guru BK.
"""

    return send_email(
        conf["recipient"],
        f"[SAFE-STUDENT] Pengajuan jadwal {appointment_id}",
        body,
        "Pengajuan jadwal",
        appointment_id,
    )


def notify_student_approved(to, appointment_id, schedule, note=""):
    body = f"""
Halo,

Pengajuan jadwal konselingmu telah disetujui Guru BK MAN 2 Kudus.

Kode jadwal: {appointment_id}
Jadwal final: {schedule}

Silakan datang sesuai waktu yang disepakati. Jika tidak dapat hadir,
hubungi Guru BK untuk mengatur ulang jadwal.

Email ini tidak memuat isi laporan curhat.
"""

    if note.strip():
        body += "\nCatatan untuk kamu:\n" + note.strip()

    return send_email(
        to,
        f"[SAFE-STUDENT] Jadwal disetujui {appointment_id}",
        body,
        "Persetujuan jadwal",
        appointment_id,
    )


# =========================================================
# 6. INDIKATOR URGENSI
# =========================================================

def analyze_text(text):
    lower = text.lower()

    high = [
        "diancam",
        "dipukul",
        "kekerasan",
        "pelecehan",
        "pemerasan",
        "takut pulang",
        "tidak aman",
    ]

    medium = [
        "dibully",
        "bullying",
        "diejek",
        "dikucilkan",
        "stres",
        "takut",
        "cemas",
        "dihina",
        "nilai turun",
        "sendiri",
        "bertengkar",
        "masalah keluarga",
    ]

    score = 3 * sum(word in lower for word in high)
    score += sum(word in lower for word in medium)

    if score >= 3:
        return "MERAH - Perlu ditinjau segera", score

    if score >= 1:
        return "KUNING - Perlu ditinjau", score

    return "HIJAU - Tinjauan rutin", score


# =========================================================
# 7. KOMPONEN TAMPILAN
# =========================================================

def show_hero():
    if LOGO_URI:
        st.markdown(
            f"""
            <div class="logo-container">
                <img class="logo-school" src="{LOGO_URI}"
                     alt="Logo gabungan MAN 2 Kudus">
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="eyebrow">SAFE-STUDENT · MAN 2 KUDUS</div>
        <div class="title-curhatin">Curhatin</div>
        <div class="title-digital">Digital MAN</div>
        <div class="title-safe">- SAFE-STUDENT MAN 2 Kudus -</div>
        """,
        unsafe_allow_html=True,
    )


def show_character(uri, name, caption):
    if uri:
        st.markdown(
            f"""
            <div class="mascot">
                <img src="{uri}" alt="{html.escape(name)}">
                <div class="mascot-name">{html.escape(name)}</div>
                <div style="color:white;font-size:.78rem;
                            margin-top:6px;text-shadow:0 2px 5px #00304b;">
                    {html.escape(caption)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            f"Gambar {name} tidak ditemukan. "
            "Periksa nama file di bagian konfigurasi."
        )


def section_card(title, description):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def check_login(secret_key, state_key, label):
    if st.session_state.get(state_key, False):
        return True

    password = st.text_input(
        f"Kata sandi {label}",
        type="password",
        key=f"password_{state_key}",
    )

    if st.button(f"Masuk {label}", key=f"login_{state_key}"):
        expected = get_secret("auth", secret_key, "")

        if expected and secrets.compare_digest(password, expected):
            st.session_state[state_key] = True
            st.rerun()
        else:
            st.error(
                "Kata sandi salah atau belum diatur di Secrets."
            )

    return False


# =========================================================
# 8. SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:10px 0;">
            <div style="font-size:2.5rem;">🦀</div>
            <div style="font-family:Fredoka,sans-serif;
                        font-size:1.35rem;font-weight:700;">
                SAFE-STUDENT
            </div>
            <div style="font-size:.78rem;line-height:1.7;">
                Layanan Pelaporan & Konseling Digital MAN 2 Kudus
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    room = st.radio(
        "Pilih Ruang Akses",
        [
            "✨ Siswa — Curhat & Jadwal",
            "🔒 Guru

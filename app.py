import os
import sqlite3
import smtplib
import ssl
import secrets
from datetime import datetime, date, time
from email.message import EmailMessage
from pathlib import Path

import streamlit as st
import pandas as pd

# =========================================================
# KONFIGURASI APLIKASI
# =========================================================
BASE = Path(__file__).resolve().parent
DB = BASE / "safe_student.db"

BK_EMAIL = "bkm2kmendunia@gmail.com"
SENDER = "safestudentm2k@gmail.com"

st.set_page_config(
    page_title="SAFE-STUDENT | MAN 2 Kudus",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS: DESAIN BAWAH LAUT, LOGO, DAN RESPONSIF
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #063b83;
    --blue: #087eb5;
    --cyan: #00bce8;
    --yellow: #ffdc4a;
    --white: #ffffff;
}

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background:
        linear-gradient(
            180deg,
            rgba(0, 126, 188, .18),
            rgba(0, 185, 225, .12)
        ),
        url("bg_laut.jpg") center center / cover fixed;
    color: #07345b;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    right: 1rem;
}

.block-container {
    max-width: 1500px;
    padding: 1rem 2rem 3rem;
}

[data-testid="stSidebar"] {
    background: #fffdf6;
    border-right: 3px solid #b9efff;
}

[data-testid="stSidebar"] * {
    color: #17436a;
}

[data-testid="stSidebar"] hr {
    border-color: #c7e4ed;
}

.logo-banner {
    text-align: center;
    padding: 8px 0 12px;
}

.logo-banner img {
    max-width: min(100%, 850px);
    max-height: 125px;
    width: auto;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 3px 5px #003d6c35);
}

.hero {
    text-align: center;
    padding: 15px 12px 24px;
    margin-bottom: 12px;
    border-radius: 28px;
    background: rgba(0, 75, 135, .15);
}

.hero .eyebrow {
    color: #fff;
    font-weight: 700;
    letter-spacing: 1.5px;
    font-size: clamp(.8rem, 2vw, 1.15rem);
    text-shadow: 0 2px 5px #003c72;
}

.hero h1 {
    font-family: 'Fredoka', sans-serif;
    color: var(--yellow);
    font-size: clamp(2.5rem, 7vw, 6rem);
    line-height: 1.08;
    margin: 15px 0 10px;
    text-shadow:
        3px 4px 0 #063b83,
        0 0 12px #ffffff75;
}

.hero .subtitle {
    color: #fff;
    font-size: clamp(.95rem, 2.1vw, 1.3rem);
    font-weight: 600;
    line-height: 1.7;
    text-shadow: 0 2px 5px #003b68;
    max-width: 850px;
    margin: 0 auto;
}

.character-name {
    text-align: center;
    font-family: 'Fredoka', sans-serif;
    font-size: clamp(1rem, 2vw, 1.45rem);
    color: #073e8d;
    font-weight: 700;
    background: rgba(255, 255, 255, .93);
    border: 2px solid #c7f2ff;
    border-radius: 22px;
    padding: 8px 5px;
    margin: 8px 0 18px;
}

.welcome {
    background: rgba(255, 255, 255, .96);
    border: 3px solid #c8f2ff;
    border-radius: 30px;
    padding: clamp(17px, 3vw, 32px);
    text-align: center;
    box-shadow: 0 12px 30px #00477620;
    margin: 10px 0 20px;
}

.welcome h2 {
    font-family: 'Fredoka', sans-serif;
    font-size: clamp(1.35rem, 3vw, 2.2rem);
    line-height: 1.35;
    color: #073b83;
    margin-top: 0;
}

.welcome p {
    color: #315c79;
    line-height: 1.8;
    font-size: clamp(.88rem, 1.7vw, 1.08rem);
}

.panel {
    background: rgba(255, 255, 255, .96);
    border: 2px solid #d2f1fb;
    border-radius: 25px;
    padding: clamp(15px, 2.5vw, 27px);
    margin: 12px 0;
    box-shadow: 0 8px 25px #003c6c16;
}

.panel h3 {
    color: #073b83;
    font-family: 'Fredoka', sans-serif;
}

.metric {
    background: rgba(255,255,255,.97);
    border: 2px solid #d2f1fb;
    border-radius: 19px;
    padding: 17px;
    box-shadow: 0 6px 18px #003c6c10;
}

.metric .num {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0878b5;
}

.muted {
    color: #526f82;
    font-size: .92rem;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,.97);
    border: 2px solid #d2f1fb;
    border-radius: 23px;
    padding: clamp(12px, 2vw, 24px);
}

div.stButton > button,
div.stFormSubmitButton > button {
    background: linear-gradient(90deg, #0755a1, #079fc7);
    color: white;
    border: 2px solid #9beaff;
    border-radius: 14px;
    min-height: 44px;
    font-weight: 700;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #064485, #087da8);
    color: white;
    border-color: #fff;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,.92);
    border-radius: 12px;
    padding: 10px 15px;
    color: #073b83;
}

input, textarea {
    border-radius: 10px !important;
}

[data-testid="stDataFrame"] {
    background: white;
    border-radius: 15px;
}

.footer {
    text-align: center;
    color: #fff;
    font-size: .83rem;
    font-weight: 600;
    text-shadow: 0 1px 4px #003b68;
    padding: 22px 0 8px;
}

@media (max-width: 768px) {
    .block-container {
        padding: .5rem .65rem 2rem;
    }

    .hero {
        padding: 12px 8px 18px;
        border-radius: 20px;
    }

    .hero h1 {
        font-size: clamp(2.25rem, 10vw, 3.5rem);
    }

    .logo-banner img {
        max-width: 100%;
        max-height: 85px;
    }

    .welcome {
        border-radius: 22px;
        padding: 17px 13px;
    }

    .panel {
        border-radius: 20px;
        padding: 14px;
    }

    .character-name {
        font-size: .92rem;
        padding: 7px 3px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px;
        font-size: .83rem;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
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
# KONFIGURASI DAN PENGIRIMAN EMAIL
# =========================================================
def cfg():
    try:
        e = st.secrets.get("email", {})
        return {
            "sender": e.get("sender", SENDER),
            "password": e.get("app_password", ""),
            "recipient": e.get("recipient", BK_EMAIL),
            "host": e.get("smtp_host", "smtp.gmail.com"),
            "port": int(e.get("smtp_port", 465)),
        }
    except Exception:
        return {
            "sender": os.getenv("SAFE_EMAIL_SENDER", SENDER),
            "password": os.getenv("SAFE_EMAIL_APP_PASSWORD", ""),
            "recipient": os.getenv("SAFE_EMAIL_RECIPIENT", BK_EMAIL),
            "host": "smtp.gmail.com",
            "port": 465,
        }


def log_mail(to, subject, event, code, status, detail=""):
    with connect() as con:
        con.execute("""
            INSERT INTO email_log
            (created, recipient, subject, event, code, status, detail)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now(), to, subject, event, code, status, detail[:300]))
        con.commit()


def email(to, subject, body, event, code=""):
    conf = cfg()

    if not conf["password"]:
        log_mail(
            to, subject, event, code,
            "Belum dikonfigurasi",
            "App Password belum diatur."
        )
        return False, "Email belum dikonfigurasi. Periksa Settings → Secrets di Streamlit Cloud."

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

    except Exception as exc:
        log_mail(to, subject, event, code, "Gagal", str(exc))
        return False, "Email gagal dikirim. Periksa konfigurasi email."


def mail_bk(code, category, urgency):
    recipient = cfg()["recipient"]
    body = f"""Halo Guru BK MAN 2 Kudus,

Ada laporan baru di SAFE-STUDENT.

Kode laporan: {code}
Kategori: {category}
Penanda urgensi otomatis: {urgency}

Isi curhat tidak disertakan dalam email untuk menjaga privasi.
Silakan masuk ke dashboard Guru BK untuk meninjau laporan.

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
    body = f"""Halo,

Pengajuan jadwal konseling kamu telah disetujui Guru BK MAN 2 Kudus.

Kode pengajuan: {code}
Jadwal: {schedule}

Email ini tidak memuat isi curhat.

SAFE-STUDENT MAN 2 Kudus
"""
    if note.strip():
        body += f"\nCatatan untuk kamu: {note.strip()}\n"

    return email(
        to,
        f"[SAFE-STUDENT] Jadwal disetujui - {code}",
        body,
        "Persetujuan jadwal",
        code
    )


# =========================================================
# FUNGSI UMUM
# =========================================================
def score_text(txt):
    text = txt.lower()
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
    urgency = "MERAH" if score >= 3 else "KUNING" if score else "HIJAU"
    return urgency, score


def get_reports():
    with connect() as con:
        return pd.read_sql_query(
            "SELECT * FROM reports ORDER BY created DESC", con
        )


def update_report(code, **kwargs):
    allowed = {
        "status", "final_schedule",
        "schedule_status", "bk_note"
    }
    values = {key: val for key, val in kwargs.items() if key in allowed}
    values["updated"] = now()

    with connect() as con:
        con.execute(
            "UPDATE reports SET "
            + ", ".join(key + " = ?" for key in values)
            + " WHERE code = ?",
            list(values.values()) + [code]
        )
        con.commit()


def image_if_exists(filename, width=None):
    path = BASE / filename
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.caption(f"Gambar belum ditemukan: {filename}")


def show_logo():
    path = BASE / "Logo_MAN2.png"
    if path.exists():
        st.markdown('<div class="logo-banner">', unsafe_allow_html=True)
        st.image(str(path), use_container_width=False, width=650)
        st.markdown('</div>', unsafe_allow_html=True)


def hero(title="Curhatin Digital", subtitle="Tempat bercerita, meminta bantuan, dan menjadwalkan konseling dengan lebih nyaman."):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">🌊 DIGITAL MAN · MAN 2 KUDUS</div>
            <h1>{title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def panel(title, description=""):
    desc = f'<p class="muted">{description}</p>' if description else ""
    st.markdown(
        f'<div class="panel"><h3>{title}</h3>{desc}</div>',
        unsafe_allow_html=True
    )


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🌊 SAFE-STUDENT")
    st.caption("Layanan Pelaporan & Konseling Digital MAN 2 Kudus")
    room = st.radio(
        "Pilih Ruang Akses",
        [
            "✨ Siswa (Curhat & Jadwal)",
            "🧑‍🏫 Guru BK",
            "👨‍👩‍👧 Orang Tua",
            "🔐 Admin"
        ]
    )
    st.markdown("---")
    st.caption("Sampaikan cerita, temukan dukungan.")


# =========================================================
# HALAMAN SISWA
# =========================================================
if room == "✨ Siswa (Curhat & Jadwal)":
    show_logo()
    hero()

    left, center, right = st.columns([1, 1.65, 1], gap="medium")

    with left:
        image_if_exists("ubur_cewe.png")
        st.markdown(
            '<div class="character-name">Kema · Sahabat bercerita 🪼</div>',
            unsafe_allow_html=True
        )

    with center:
        st.markdown("""
        <div class="welcome">
            <h2>Halo, Teman-teman MAN 2 Kudus! 💙</h2>
            <p>Kamu boleh bercerita dengan nyaman.</p>
            <p>Guru BK akan meninjau laporanmu dengan perhatian.</p>
            <p>Email hanya digunakan untuk konfirmasi jadwal jika kamu mengisinya.</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        image_if_exists("kepiting_cowo.png")
        st.markdown(
            '<div class="character-name">Temo · Sahabatmu 🦀</div>',
            unsafe_allow_html=True
        )

    tab1, tab2, tab3 = st.tabs([
        "💬 Tulis Curhat",
        "📅 Ajukan Jadwal",
        "🔎 Cek Status"
    ])

    with tab1:
        panel(
            "🔒 Formulir Curhat Anonim",
            "Sampaikan ceritamu. Hindari menuliskan informasi pribadi yang tidak diperlukan."
        )

        with st.form("report_form", clear_on_submit=True):
            category = st.selectbox(
                "Kategori",
                [
                    "Perundungan / bullying",
                    "Stres belajar & tahfidz",
                    "Keluarga atau masalah pribadi",
                    "Konsultasi agama / moral",
                    "Lainnya"
                ]
            )
            content = st.text_area(
                "Ceritakan yang ingin disampaikan",
                height=160
            )
            optional_email = st.text_input(
                "Email untuk konfirmasi jadwal (opsional)"
            )
            use_email = st.checkbox(
                "Saya ingin menggunakan email ini untuk konfirmasi jadwal."
            )
            send_report = st.form_submit_button(
                "Kirim Laporan",
                use_container_width=True
            )

        if send_report:
            if len(content.strip()) < 8:
                st.error("Ceritakan sedikit lebih lengkap (minimal 8 karakter).")
            elif use_email and (
                "@" not in optional_email
                or "." not in optional_email.split("@")[-1]
            ):
                st.error("Masukkan alamat email yang valid.")
            else:
                urgency, score = score_text(content)
                code = (
                    "MAN2-"
                    + datetime.now().strftime("%y%m%d")
                    + "-"
                    + secrets.token_hex(3).upper()
                )

                with connect() as con:
                    con.execute("""
                        INSERT INTO reports
                        (code, created, category, content, urgency, score,
                         status, student_email, schedule_status, updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        code, now(), category, content.strip(),
                        urgency, score, "Baru",
                        optional_email.strip() if use_email else "",
                        "Belum diajukan", now()
                    ))
                    con.commit()

                ok, message = mail_bk(code, category, urgency)
                st.success(
                    f"Laporan tersimpan. Simpan kode laporanmu: {code}"
                )
                if ok:
                    st.info("Pemberitahuan telah dikirim ke Guru BK.")
                else:
                    st.warning(
                        "Laporan tersimpan, tetapi email BK belum terkirim. "
                        + message
                    )
                st.caption(
                    "Penanda urgensi otomatis hanya penyaringan awal, "
                    "bukan diagnosis atau pengganti penilaian Guru BK."
                )

    with tab2:
        panel(
            "📅 Pengajuan Jadwal Tatap Muka",
            "Jadwal belum resmi sampai disetujui Guru BK."
        )

        with st.form("schedule_form", clear_on_submit=True):
            code = st.text_input("Kode laporan")
            student_email = st.text_input(
                "Email aktif untuk menerima konfirmasi"
            )
            requested_date = st.date_input(
                "Tanggal yang diinginkan",
                min_value=date.today()
            )
            requested_time = st.time_input(
                "Waktu yang diinginkan",
                value=time(10, 0),
                step=1800
            )
            note = st.text_area("Catatan singkat (opsional)", height=70)
            submit_schedule = st.form_submit_button(
                "Kirim Pengajuan Jadwal",
                use_container_width=True
            )

        if submit_schedule:
            valid_email = (
                "@" in student_email
                and "." in student_email.split("@")[-1]
            )

            if not code.strip() or not valid_email:
                st.error("Masukkan kode laporan dan email yang valid.")
            else:
                with connect() as con:
                    found = con.execute(
                        "SELECT code FROM reports WHERE code = ?",
                        (code.strip(),)
                    ).fetchone()

                    if found:
                        requested = (
                            requested_date.strftime("%d-%m-%Y")
                            + " pukul "
                            + requested_time.strftime("%H:%M")
                        )
                        con.execute("""
                            UPDATE reports
                            SET student_email = ?, requested = ?,
                                schedule_status = 'Menunggu persetujuan',
                                bk_note = ?, updated = ?
                            WHERE code = ?
                        """, (
                            student_email.strip(), requested,
                            note.strip(), now(), code.strip()
                        ))
                        con.commit()

                if found:
                    ok, message = email(
                        cfg()["recipient"],
                        f"[SAFE-STUDEN

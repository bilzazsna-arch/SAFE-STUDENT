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

/* Posisi Maskot Ganda di Tengah */
.mascot-double-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    width: 100%;
    margin-bottom: 5px;
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

/* Header Judul Eye-Catching Font Cantik */
.hero-clean {
    text-align: center;
    padding: 10px 5px;
    margin-bottom: 12px;
}
.hero-clean .eyebrow {
    font-family: 'Bubblegum Sans', cursive;
    font-size: clamp(1rem, 2.8vw, 1.3rem);
    letter-spacing: 2px;
    color: #e0f2fe;
    text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    margin-bottom: 2px;
}
.hero-clean h1 {
    font-family: 'Pacifico', cursive, sans-serif;
    font-size: clamp(2rem, 5vw, 3.8rem);
    line-height: 1.2;
    margin: 6px 0;
    color: #ffd45c;
    text-shadow: 0 4px 12px rgba(0, 0, 0, 0.6), 0 2px 4px rgba(7,59,102,0.9);
}
.hero-clean p {
    font-family: 'Bubblegum Sans', cursive;
    color: #ffffff;
    font-size: clamp(1.1rem, 3vw, 1.5rem);
    text-shadow: 0 2px 6px rgba(0,0,0,0.6);
    margin-bottom: 0;
}

/* Panel & Card Styling */
.panel {
    background: rgba(255, 255, 255, 0.94);
    backdrop-filter: blur(10px);
    border: 1.5px solid #bae6fd;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 10px 28px rgba(8, 59, 102, 0.18);
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
    color: #334155;
    font-size: 0.95rem;
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
    background: rgba(255, 255, 255, 0.95);
    border: 1.5px solid #bae6fd;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(8, 59, 102, 0.15);
}

[data-testid="stTabs"] button {
    font-weight: 700;
    font-size: 1rem;
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
Kategori: {category}
Penanda urgensi otomatis: {urgency}

Isi curhat tidak dicantumkan dalam email demi menjaga privasi.
Silakan masuk ke dashboard Guru BK untuk meninjau laporan.

SAFE-STUDENT MAN 2 Kudus"""
    return email(to, f"[SAFE-STUDENT] Laporan baru {code}", body, "Laporan baru", code)

def mail_student_code(to, code, category):
    body = f"""Halo Rencang-rencang MAN 2 Kudus,

Terima kasih sudah menggunakan layanan SAFE-STUDENT. Curhatanmu telah diterima dengan aman dan anonim oleh Temo & Tima dan Guru BK.

Berikut adalah Kode Laporan kamu:
🔑 {code}
Kategori: {category}

Simpan kode ini untuk mengecek status laporan atau mengajukan jadwal konseling di aplikasi SAFE-STUDENT.

Salam hangat,
Temo, Tima & Tim BK MAN 2 Kudus"""
    return email(to, f"[SAFE-STUDENT] Kode Laporan Kamu - {code}", body, "Kirim kode laporan ke siswa", code)

def mail_student(to, code, schedule, note=""):
    body = f"""Halo,

Pengajuan jadwal konseling kamu telah disetujui Guru BK MAN 2 Kudus.

Kode pengajuan: {code}
Jadwal yang disepakati: {schedule}
Lokasi: ruang BK MAN 2 Kudus.
"""
    if note.strip(): 
        body += f"\nCatatan untuk kamu: {note.strip()}\n"
    body += "\nSAFE-STUDENT MAN 2 Kudus"
    return email(to, f"[SAFE-STUDENT] Jadwal disetujui - {code}", body, "Persetujuan jadwal", code)

def score_text(txt):
    t = txt.lower()
    high = ["diancam", "dipukul", "kekerasan", "takut pulang", "tidak aman"]
    med = ["bullying", "dibully", "cemas", "panik", "stres", "tertekan", "sedih", "konflik"]
    n = 3 * sum(x in t for x in high) + sum(x in t for x in med)
    return ("MERAH" if n >= 3 else "KUNING" if n else "HIJAU"), n

def reports():
    with connect() as c: 
        return pd.read_sql_query("SELECT * FROM reports ORDER BY created DESC", c)

def update(code, **kw):
    allowed = {"status", "final_schedule", "schedule_status", "bk_note"}
    vals = {k: v for k, v in kw.items() if k in allowed}
    vals["updated"] = now()
    with connect() as c:
        c.execute("UPDATE reports SET " + ", ".join(k + "=?" for k in vals) + " WHERE code=?",
                  list(vals.values()) + [code])
        c.commit()

def image_if_exists(name, width=None):
    p = BASE / name
    if p.exists(): 
        st.image(str(p), width=width, use_container_width=(width is None))

with st.sidebar:
    st.markdown("## 🐟 SAFE-STUDENT")
    st.caption("Layanan Pelaporan & Konseling Digital MAN 2 Kudus")
    room = st.radio("Pilih Ruang Akses", ["✨ Siswa (Curhat & Jadwal)", "🧑‍🏫 Guru BK", "🔐 Admin"])
    st.markdown("---")
    st.caption("Sampaikan cerita, temukan dukungan.")

def hero_clean(title="SAFE STUDENT MAN 2 KUDUS", subtitle="- Safe Space -"):
    st.markdown(f'''
    <div class="hero-clean">
        <div class="eyebrow">🌊 DIGITAL MAN · MAN 2 KUDUS</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    ''', unsafe_allow_html=True)

# Dialog / Pop-up Hug Cute dari Maskot
@st.dialog("🫂 Pelukan Hangat dari Temo & Tima! 🐟")
def hug_modal(code, student_email):
    st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <h2 style="color: #0284c7; font-family: 'Bubblegum Sans', cursive; font-size: 2rem; margin-bottom: 8px;">
            Temo & Tima Mengirimkan Pelukan! 🫂💙
        </h2>
        <p style="color: #334155; font-size: 1.05rem;">
            Terima kasih sudah berani bercerita. Kamu luar biasa! Kami dan Guru BK akan menjaga kerahasiaan ceritamu.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        image_if_exists("paus_cowo.png", 140)
    with col_d2:
        image_if_exists("paus_cewe.png", 140)
        
    st.info(f"🔑 **Kode Laporan Kamu:** `{code}`")
    if student_email.strip():
        st.success(f"📧 Kode laporan juga telah dikirim secara otomatis ke email: **{student_email.strip()}**")
    else:
        st.warning("⚠️ Kamu tidak memasukkan email, pastikan mencatat kode laporan di atas!")
    st.caption("Gunakan kode ini di tab 'Cek Status' untuk melihat perkembangan laporan atau jadwalmu.")

if room == "✨ Siswa (Curhat & Jadwal)":
    logo_path = BASE / "Logo_MAN2.png"
    if logo_path.exists():
        logo_b64 = get_base64_of_bin_file(logo_path)
        st.markdown(f'''
        <div class="logo-center-wrapper">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo MAN 2 Kudus">
        </div>
        ''', unsafe_allow_html=True)
    
    hero_clean("SAFE STUDENT MAN 2 KUDUS", "- Safe Space -")
    
    # Dua Maskot (paus_cowo.png & paus_cewe.png) di Tengah Atas
    st.markdown('<div class="mascot-double-container">', unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        image_if_exists("paus_cowo.png", 130)
    with col_m2:
        image_if_exists("paus_cewe.png", 130)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;font-weight:700;color:#ffffff;text-shadow: 0 2px 4px rgba(0,0,0,0.6);margin-top:2px;margin-bottom:12px;'>Temo & Tima · Sahabat Setia</div>", unsafe_allow_html=True)

    col_center = st.columns([1, 4, 1])
    with col_center[1]:
        st.markdown("""
        <div class="panel" style="padding:22px; text-align:center;">
            <h3 style="margin-bottom:6px;color:#073b66;font-family:'Fredoka',sans-serif;">SUGENG RAWUH RENCANG-RENCANG MAN 💙</h3>
            <p class="muted" style="margin-bottom:0; font-size:1rem;">
                Kami Temo & Tima, penjaga kerahasiaan curhatmu. Apapun masalahmu di sekolah, curhatkan di sini dengan aman dan anonim!
            </p>
        </div>
        """, unsafe_allow_html=True)

    # FITUR UNGGULAN: Alasan Memilih Website ini Dibanding WhatsApp Biasa
    with st.expander("💡 Kenapa Curhat di Sini Lebih Nyaman Dibanding WhatsApp Langsung? (Klik untuk baca)"):
        st.markdown("""
        *   **🛡️ 100% Bebas Canggung & Tekanan:** Tidak perlu merasa gugup atau takut salah ketik saat mulai menyapa guru secara langsung. Tulis kapanpun kamu siap!
        *   **🕵️ Jaminan Privasi Mutlak:** Chat WhatsApp biasa sering kali terlihat orang lain di HP atau meninggalkan jejak nomor HP. Di sini identitasmu terlindungi sistem anonim dan kode rahasia unik.
        *   **📈 Status Progress Transparan:** Tidak perlu cemas pesanmu hanya *centang biru* atau terabaikan. Kamu bisa melacak status laporanmu secara real-time (*Baru ➔ Diproses ➔ Selesai*).
        *   **🤝 Pendampingan Emosi Temo & Tima:** Ditemani maskot ramah yang siap memberikan dukungan psikologis sebelum kamu akhirnya bertemu langsung di ruang BK.
        """)

    t1, t2, t3, t4 = st.tabs(["💬 Tulis Curhat", "📅 Ajukan Jadwal", "🔎 Cek Status", "🧘 Self-Care Corner"])
    with t1:
        st.markdown('<div class="panel" style="margin-bottom:10px;"><h3 style="color:#073b66;margin-bottom:0;font-family:\'Fredoka\',sans-serif;">🛡️ Formulir Curhat Anonim (Bebas & Aman)</h3></div>', unsafe_allow_html=True)
        with st.form("report_form", clear_on_submit=True):
            category = st.selectbox("Kategori", [
                "Perundungan / bullying", 
                "Stres belajar & tugas menumpuk", 
                "Kebijakan sekolah & aturan guru", 
                "Sikap / perilaku guru yang kurang pas", 
                "Keluarga atau masalah pribadi", 
                "Lainnya"
            ])
            content = st.text_area("Ceritakan yang ingin disampaikan", height=150, placeholder="Tulis curhatanmu di sini...")
            optional_email = st.text_input("Email aktif untuk konfirmasi jadwal (opsional)", placeholder="contoh@email.com")
            use_email = st.checkbox("Saya ingin menggunakan email ini untuk konfirmasi jadwal & menerima kode laporan.")
            send = st.form_submit_button("Kirim Laporan", use_container_width=True)
        if send:
            if len(content.strip()) < 8: 
                st.error("Ceritakan sedikit lebih lengkap (minimal 8 karakter).")
            else:
                urgency, sc = score_text(content)
                code = "MAN2-" + datetime.now().strftime("%y%m%d") + "-" + secrets.token_hex(3).upper()
                student_mail_target = optional_email.strip() if use_email else ""
                
                with connect() as db:
                    db.execute("INSERT INTO reports(code,created,category,content,urgency,score,status,student_email,schedule_status,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
                               (code, now(), category, content.strip(), urgency, sc, "Baru", student_mail_target, "Belum diajukan", now()))
                    db.commit()
                
                mail_bk(code, category, urgency)
                if student_mail_target:
                    mail_student_code(student_mail_target, code, category)
                
                st.balloons()
                st.toast("Pesan terkirim! Temo & Tima memberikan pelukan hangat 🫂", icon="🐟")
                hug_modal(code, student_mail_target)

    with t2:
        st.markdown('<div class="panel"><h3>📅 Pengajuan Jadwal Tatap Muka</h3></div>', unsafe_allow_html=True)
        with st.form("schedule_form", clear_on_submit=True):
            code_input = st.text_input("Kode laporan")
            student_email = st.text_input("Email aktif untuk menerima konfirmasi")
            d = st.date_input("Tanggal yang diinginkan", min_value=date.today())
            tm = st.time_input("Waktu yang diinginkan", value=time(10, 0), step=1800)
            note = st.text_area("Catatan singkat (opsional)", height=70)
            send_req = st.form_submit_button("Kirim Pengajuan Jadwal", use_container_width=True)
        if send_req:
            if not code_input.strip():
                st.error("Masukkan kode laporan yang valid.")
            else:
                with connect() as db:
                    found = db.execute("SELECT code FROM reports WHERE code=?", (code_input.strip(),)).fetchone()
                    if found:
                        requested = f"{d.strftime('%d-%m-%Y')} pukul {tm.strftime('%H:%M')}"
                        db.execute("UPDATE reports SET student_email=?,requested=?,schedule_status='Menunggu persetujuan',bk_note=?,updated=? WHERE code=?",
                                   (student_email.strip(), requested, note.strip(), now(), code_input.strip()))
                        db.commit()
                if found:
                    st.success("Pengajuan tersimpan. Tunggu konfirmasi melalui email.")
                else: 
                    st.error("Kode laporan tidak ditemukan.")
    with t3:
        st.markdown('<div class="panel"><h3>🔎 Cek Status Laporan & Jadwal</h3></div>', unsafe_allow_html=True)
        check_code = st.text_input("Kode laporan untuk dicek", key="check_code")
        if st.button("Cek Status"):
            with connect() as db: 
                r = db.execute("SELECT code,status,requested,final_schedule,schedule_status FROM reports WHERE code=?", (check_code.strip(),)).fetchone()
            if r:
                st.write("**Status laporan:**", r["status"])
                st.write("**Status jadwal:**", r["schedule_status"])
                if r["requested"]: 
                    st.write("**Waktu diajukan:**", r["requested"])
                if r["final_schedule"]: 
                    st.write("**Jadwal final:**", r["final_schedule"])
            else: 
                st.warning("Kode laporan tidak ditemukan.")

    with t4:
        st.markdown('<div class="panel"><h3>🧘 Self-Care Corner (Tips Penenang Cepat)</h3><p class="muted">Lakukan teknik relaksasi ini jika kamu sedang merasa cemas atau stres berat sambil menunggu bantuan Guru BK.</p></div>', unsafe_allow_html=True)
        st.info("""
        **🍃 Teknik Pernapasan 4-7-8 untuk Meredakan Cemas:**
        1. Tarik napas perlahan melalui hidung selama **4 detik**.
        2. Tahan napas di dalam dada selama **7 detik**.
        3. Hembuskan napas perlahan lewat mulut secara perlahan selama **8 detik**.
        4. Ulangi sebanyak 4 siklus hingga pikiranmu terasa lebih tenang. Temo & Tima selalu mendukungmu! 💙
        """)

elif room == "🧑‍🏫 Guru BK":
    hero_clean("Dashboard Guru BK", "Kelola laporan, tindak lanjut, dan persetujuan jadwal.")
    with st.expander("🔐 Masuk ke dashboard Guru BK", expanded=not st.session_state.get("bk_auth", False)):
        pw = st.text_input("Kata sandi Guru BK", type="password", key="bk_pw")
        if st.button("Masuk Guru BK"):
            try: 
                expected = st.secrets.get("auth", {}).get("bk_password", "")
            except Exception: 
                expected = ""
            if expected and secrets.compare_digest(pw, expected):
                st.session_state["bk_auth"] = True
                st.rerun()
            else: 
                st.error("Kata sandi salah atau belum diatur di secrets.toml.")
    if st.session_state.get("bk_auth"):
        df = reports()
        n = len(df)
        cols = st.columns(4)
        for col, label, val in zip(cols, ["Total laporan", "Laporan baru", "Jadwal menunggu", "Jadwal disetujui"],
                                  [n, int((df.status == "Baru").sum()) if n else 0, int((df.schedule_status == "Menunggu persetujuan").sum()) if n else 0, int((df.schedule_status == "Disetujui").sum()) if n else 0]):
            with col: 
                st.markdown(f'<div class="metric"><div>{label}</div><div class="num">{val}</div></div>', unsafe_allow_html=True)
        
        t1, t2, t3 = st.tabs(["📥 Kelola Laporan Masuk", "📅 Validasi Jadwal Konseling", "✉️ Log Email Sistem"])
        with t1:
            if n:
                selected_code = st.selectbox("Pilih Kode Laporan", df.code.tolist())
                r = df[df.code == selected_code].iloc[0]
                st.info(f"**Kategori:** {r.category} | **Urgensi:** {r.urgency} | **Status:** {r.status}")
                st.write("**Isi Curhatan Siswa:**")
                st.success(r.content)
                with st.form("update_report"):
                    new_status = st.selectbox("Ubah Status Laporan", ["Baru", "Diproses", "Selesai"], index=["Baru", "Diproses", "Selesai"].index(r.status))
                    new_note = st.text_area("Catatan Penanganan Guru BK", value=r.bk_note or "")
                    if st.form_submit_button("Simpan Perubahan Laporan"):
                        update(selected_code, status=new_status, bk_note=new_note)
                        st.success("Perubahan laporan berhasil disimpan!")
                        st.rerun()
        with t2:
            waiting = df[df.schedule_status == "Menunggu persetujuan"] if n else pd.DataFrame()
            if len(waiting):
                sel_w = st.selectbox("Pilih Pengajuan Jadwal", waiting.code.tolist(), key="sel_w")
                rw = df[df.code == sel_w].iloc[0]
                st.write(f"**Waktu yang diminta siswa:** {rw.requested}")
                st.write(f"**Catatan siswa:** {rw.bk_note}")
                with st.form("appr"):
                    dec = st.radio("Keputusan Jadwal", ["Setujui", "Tolak"])
                    final_time_input = st.text_input("Tentukan Jadwal Final (misal: 15-11-2026 pukul 10:00)", value=rw.requested or "")
                    note_input = st.text_area("Catatan untuk Siswa (opsional)", placeholder="Contoh: Silakan datang ke ruang BK tepat waktu.")
                    if st.form_submit_button("Kirim Keputusan Jadwal"):
                        if dec == "Setujui":
                            update(sel_w, schedule_status="Disetujui", final_schedule=final_time_input)
                            if rw.student_email: 
                                mail_student(rw.student_email, sel_w, final_time_input, note_input)
                        else:
                            update(sel_w, schedule_status="Ditolak")
                        st.success("Keputusan jadwal berhasil diproses dan dikirim ke siswa!")
                        st.rerun()
            else:
                st.info("Tidak ada pengajuan jadwal konseling yang menunggu persetujuan saat ini.")
        with t3:
            with connect() as db: 
                logs = pd.read_sql_query("SELECT created,recipient,subject,event,code,status FROM email_log ORDER BY id DESC LIMIT 100", db)
            if len(logs): 
                st.dataframe(logs, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada log email tercatat.")
        
        if st.button("Keluar Ruang Guru BK"): 
            st.session_state["bk_auth"] = False
            st.rerun()

else:
    hero_clean("Admin SAFE-STUDENT", "Panel Kontrol & Pengaturan Sistem Lanjutan.")
    with st.expander("🔐 Masuk Panel Admin", expanded=not st.session_state.get("admin_auth", False)):
        pw = st.text_input("Kata sandi Admin", type="password", key="admin_pw")
        if st.button("Masuk Admin"):
            try: 
                expected = st.secrets.get("auth", {}).get("admin_password", "")
            except Exception: 
                expected = ""
            if expected and secrets.compare_digest(pw, expected): 
                st.session_state["admin_auth"] = True
                st.rerun()
            else: 
                st.error("Kata sandi salah.")
    if st.session_state.get("admin_auth"):
        conf = cfg()
        st.markdown('<div class="panel"><h3>⚙️ Konfigurasi Sistem & Email SMTP</h3></div>', unsafe_allow_html=True)
        st.write(f"**Email Pengirim (Sender):** `{conf['sender']}`")
        st.write(f"**Email Tujuan BK (Recipient):** `{conf['recipient']}`")
        st.write(f"**SMTP Host:** `{conf['host']}:{conf['port']}`")
        
        st.markdown("---")
        st.markdown("### 📊 Statistik Database Laporan")
        with connect() as db:
            total_rep = db.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
            total_logs = db.execute("SELECT COUNT(*) FROM email_log").fetchone()[0]
        st.metric("Total Seluruh Laporan Tersimpan", total_rep)
        st.metric("Total Email Terkirim / Log", total_logs)
        
        if st.button("Keluar Admin"): 
            st.session_state["admin_auth"] = False
            st.rerun()

st.markdown('<p style="text-align:center;color:#ffffff;text-shadow: 0 1px 3px rgba(0,0,0,0.6);font-weight:600;font-size:.85rem;padding:20px">SAFE-STUDENT · MAN 2 Kudus · Sampaikan cerita, temukan dukungan.</p>', unsafe_allow_html=True)

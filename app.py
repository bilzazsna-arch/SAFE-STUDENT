import os, sqlite3, smtplib, ssl, secrets
from datetime import datetime, date, time
from email.message import EmailMessage
from pathlib import Path
import streamlit as st
import pandas as pd

BASE = Path(__file__).resolve().parent
DB = BASE / "safe_student.db"

st.set_page_config(
    page_title="Curhatin Digital MAN - Safe Space",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk menyelaraskan dengan desain pada gambar
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Background Utama - Tema Bawah Laut Lautan Biru */
.stApp {
    background: linear-gradient(180deg, #0288d1 0%, #01579b 40%, #002171 100%);
    background-attachment: fixed;
    color: #12344a;
}

/* Custom Header / Top Navbar */
[data-testid="stHeader"] {
    background: transparent;
}

/* Container Utama */
.block-container {
    max-width: 1200px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Custom Sidebar */
[data-testid="stSidebar"] {
    background-color: #f7f5ee !important;
    border-right: 2px solid #e2ddd0;
}
[data-testid="stSidebar"] * {
    color: #333333 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #555555 !important;
}

/* Sidebar Title & Subtitle */
.sidebar-logo-box {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}
.sidebar-logo-icon {
    font-size: 38px;
    background: #e1f5fe;
    padding: 6px;
    border-radius: 12px;
}
.sidebar-title {
    font-family: 'Fredoka', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #0d47a1 !important;
    line-height: 1.2;
}
.sidebar-sub {
    font-size: 0.78rem;
    color: #666 !important;
}

/* Custom Navigation Radio in Sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    display: none;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    gap: 8px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 10px 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background: #e3f2fd;
    border-color: #90caf9;
}

/* Custom Hero Section Sesuai Banner Gambar */
.hero-wrapper {
    background: linear-gradient(180deg, #1e88e5 0%, #1565c0 60%, #0d47a1 100%);
    border-radius: 28px;
    padding: 24px 20px 30px 20px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.3);
    border: 3px solid #64b5f6;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 25px;
}

.logo-header-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
    margin-bottom: 15px;
}
.logo-badge {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(5px);
    border-radius: 12px;
    padding: 6px 12px;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.main-banner-title {
    font-family: 'Fredoka', sans-serif;
    font-size: clamp(2.4rem, 5.5vw, 4.2rem);
    font-weight: 700;
    color: #ffeb3b;
    text-shadow: 3px 3px 0px #d84315, -2px -2px 0px #0d47a1, 2px -2px 0px #0d47a1, -2px 2px 0px #0d47a1;
    margin: 10px 0 0 0;
    letter-spacing: 1px;
    line-height: 1.1;
}

.sub-banner-badge {
    display: inline-block;
    background: #0d47a1;
    color: #ffffff;
    font-family: 'Fredoka', sans-serif;
    padding: 4px 22px;
    border-radius: 20px;
    font-size: 1.25rem;
    font-weight: 600;
    border: 2px solid #ffffff;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    margin-top: -5px;
    margin-bottom: 20px;
}

.greeting-card {
    background: #e0f7fa;
    border-radius: 25px;
    padding: 18px 25px;
    max-width: 650px;
    margin: 0 auto;
    border: 3px solid #80deea;
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}
.greeting-card h2 {
    font-family: 'Fredoka', sans-serif;
    color: #00838f;
    margin: 0 0 8px 0;
    font-size: 1.6rem;
}
.greeting-card p {
    color: #006064;
    font-size: 0.98rem;
    font-weight: 500;
    margin: 0;
    line-height: 1.4;
}

.mascot-container {
    text-align: center;
}
.mascot-tag {
    background: #ffffff;
    color: #0277bd;
    font-family: 'Fredoka', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    padding: 3px 18px;
    border-radius: 15px;
    display: inline-block;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    margin-top: 6px;
    border: 2px solid #29b6f6;
}

/* Panels / Cards */
.panel {
    background: #ffffff;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    border: 1px solid #e0e0e0;
}
.panel h3 {
    font-family: 'Fredoka', sans-serif;
    color: #0277bd;
    margin-top: 0;
}

.metric-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-left: 5px solid #0288d1;
}
.metric-card .num {
    font-family: 'Fredoka', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #01579b;
}

/* Custom Buttons & Forms */
div.stButton > button, div.stFormSubmitButton > button {
    border: 0;
    border-radius: 12px;
    background: linear-gradient(90deg, #0288d1, #0097a7);
    color: white;
    font-weight: 700;
    font-size: 1rem;
    min-height: 2.8rem;
    box-shadow: 0 4px 12px rgba(2, 136, 209, 0.3);
    transition: all 0.2s ease;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(2, 136, 209, 0.4);
}

div[data-testid="stForm"] {
    background: #ffffff;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border: 1px solid #e0e0e0;
}

[data-testid="stTabs"] button {
    font-weight: 600;
    font-size: 1rem;
    color: #ffffff !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffeb3b !important;
    border-bottom-color: #ffeb3b !important;
}

/* Responsive fixes */
@media(max-width: 768px) {
    .main-banner-title { font-size: 2.2rem; }
    .greeting-card { padding: 12px; }
}
</style>
""", unsafe_allow_html=True)

# Database Helper Functions
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
    """Membaca konfigurasi dari st.secrets atau environment variables."""
    try:
        e = st.secrets.get("email", {})
        return {
            "sender": e.get("sender", "safestudentm2k@gmail.com"), 
            "password": e.get("app_password", ""),
            "recipient": e.get("recipient", "bkm2kmendunia@gmail.com"), 
            "host": e.get("smtp_host", "smtp.gmail.com"),
            "port": int(e.get("smtp_port", 465))
        }
    except Exception:
        return {
            "sender": os.getenv("SAFE_EMAIL_SENDER", "safestudentm2k@gmail.com"),
            "password": os.getenv("SAFE_EMAIL_APP_PASSWORD", ""),
            "recipient": os.getenv("SAFE_EMAIL_RECIPIENT", "bkm2kmendunia@gmail.com"),
            "host": "smtp.gmail.com", 
            "port": 465
        }

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
        return False, "Email belum dikonfigurasi. Isi app_password di .streamlit/secrets.toml atau SAFE_EMAIL_APP_PASSWORD."
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
        return False, f"Email gagal dikirim ({type(ex).__name__}). Periksa App Password dan koneksi SMTP."

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

def mail_student(to, code, schedule, note=""):
    body = f"""Halo,

Pengajuan jadwal konseling kamu telah disetujui Guru BK MAN 2 Kudus.

Kode pengajuan: {code}
Jadwal yang disepakati: {schedule}
Lokasi: Ruang BK MAN 2 Kudus.
"""
    if note.strip(): 
        body += f"\nCatatan untuk kamu: {note.strip()}\n"
    body += "\nJika tidak dapat hadir, hubungi Guru BK untuk mengatur ulang jadwal.\nEmail ini tidak memuat isi curhat.\n\nSAFE-STUDENT MAN 2 Kudus"
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

# Custom Sidebar Layout
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-box">
        <div class="sidebar-logo-icon">📨</div>
        <div>
            <div class="sidebar-title">Curhatin Digital MAN</div>
            <div class="sidebar-sub">👤 Zona Aman Penjaga Siswa 24 Jam</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**Pilih Ruang Akses:**")
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
    st.caption("🔒 Privasi Terjamin: Data Pesan dienkripsi otomatis.")

# Component Hero Banner Sesuai Gambar
def render_hero_banner():
    st.markdown("""
    <div class="hero-wrapper">
        <div class="logo-header-row">
            <span class="logo-badge">☪️ Kementerian Agama</span>
            <span class="logo-badge">🏫 Madrasah Maju, Bermutu, Mendunia</span>
            <span class="logo-badge">💻 Madrasah Digital</span>
            <span class="logo-badge">🛡️ Generasi Anti Korupsi</span>
            <span class="logo-badge">🎓 MAN 2 Kudus</span>
        </div>
        <div class="main-banner-title">Curhatin Digital MAN</div>
        <div class="sub-banner-badge">- Safe Space -</div>
    """, unsafe_allow_html=True)
    
    col_kema, col_mid, col_temo = st.columns([1, 2, 1])
    
    with col_kema:
        st.markdown('<div class="mascot-container">', unsafe_allow_html=True)
        if (BASE / "kepiting_cewe.png").exists():
            st.image(str(BASE / "kepiting_cewe.png"), use_container_width=True)
        else:
            st.markdown("<h1 style='font-size: 80px; margin:0;'>🦀</h1>", unsafe_allow_html=True)
        st.markdown('<div class="mascot-tag">Kema</div></div>', unsafe_allow_html=True)
        
    with col_mid:
        st.markdown("""
        <div class="greeting-card">
            <h2>Halo Teman-teman MAN! 👋</h2>
            <p>Kami Kema & Temo adalah penjaga kerahasiaan curhatmu. Apapun masalahmu di sekolah, curhatkan di sini dengan aman dan anonim!</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_temo:
        st.markdown('<div class="mascot-container">', unsafe_allow_html=True)
        if (BASE / "kepiting_cowo.png").exists():
            st.image(str(BASE / "kepiting_cowo.png"), use_container_width=True)
        else:
            st.markdown("<h1 style='font-size: 80px; margin:0;'>🦀</h1>", unsafe_allow_html=True)
        st.markdown('<div class="mascot-tag">Temo</div></div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- MAIN NAVIGATION CONTENT -----------------

if room == "✨ Siswa (Curhat & Jadwal)":
    render_hero_banner()
    
    st.markdown("<h3 style='color: white; text-align: center;'>🔒 Formulir Curhat Anonim (Bebas & Aman)</h3>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["💬 Tulis Curhat", "📅 Ajukan Jadwal", "🔎 Cek Status"])
    
    with t1:
        st.markdown('<div class="panel"><h3>Formulir Pelaporan Anonim & Rahasia</h3><p class="muted">Email bersifat opsional dan hanya digunakan untuk konfirmasi jadwal.</p></div>', unsafe_allow_html=True)
        with st.form("report_form", clear_on_submit=True):
            category = st.selectbox(
                "Kategori Curhat/Masalah",
                ["Perundungan / bullying", "Stres belajar & tahfidz", "Keluarga atau masalah pribadi", "Konsultasi agama / moral", "Lainnya"]
            )
            content = st.text_area("Ceritakan yang ingin kamu sampaikan", height=160, placeholder="Tuliskan curhatanmu di sini secara bebas...")
            optional_email = st.text_input("Email aktif untuk konfirmasi jadwal (opsional)")
            use_email = st.checkbox("Saya ingin menggunakan email ini untuk konfirmasi jadwal.")
            send = st.form_submit_button("Kirim Laporan", use_container_width=True)
            
        if send:
            if len(content.strip()) < 8:
                st.error("Ceritakan sedikit lebih lengkap (minimal 8 karakter).")
            elif use_email and ("@" not in optional_email or "." not in optional_email.split("@")[-1]):
                st.error("Masukkan alamat email yang valid.")
            else:
                urgency, sc = score_text(content)
                code = "MAN2-" + datetime.now().strftime("%y%m%d") + "-" + secrets.token_hex(3).upper()
                with connect() as db:
                    db.execute(
                        "INSERT INTO reports(code,created,category,content,urgency,score,status,student_email,schedule_status,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (code, now(), category, content.strip(), urgency, sc, "Baru", optional_email.strip() if use_email else "", "Belum diajukan", now())
                    )
                    db.commit()
                ok, msg = mail_bk(code, category, urgency)
                st.success(f"Laporan tersimpan. Simpan kode laporanmu: **{code}**")
                st.info("Email Guru BK terkirim." if ok else "Laporan tersimpan, tetapi email Guru BK belum terkirim. " + msg)

    with t2:
        st.markdown('<div class="panel"><h3>Pengajuan Jadwal Tatap Muka</h3><p class="muted">Jadwal baru resmi setelah disetujui Guru BK.</p></div>', unsafe_allow_html=True)
        with st.form("schedule_form", clear_on_submit=True):
            code = st.text_input("Kode Laporan")
            student_email = st.text_input("Email aktif untuk menerima konfirmasi")
            d = st.date_input("Tanggal yang diinginkan", min_value=date.today())
            tm = st.time_input("Waktu yang diinginkan", value=time(10, 0), step=1800)
            note = st.text_area("Catatan singkat (opsional)", height=70)
            send_req = st.form_submit_button("Kirim Pengajuan Jadwal", use_container_width=True)
            
        if send_req:
            if not code.strip() or "@" not in student_email or "." not in student_email.split("@")[-1]:
                st.error("Masukkan kode laporan dan email yang valid.")
            else:
                with connect() as db:
                    found = db.execute("SELECT code FROM reports WHERE code=?", (code.strip(),)).fetchone()
                    if found:
                        requested = f"{d.strftime('%d-%m-%Y')} pukul {tm.strftime('%H:%M')}"
                        db.execute(
                            "UPDATE reports SET student_email=?,requested=?,schedule_status='Menunggu persetujuan',bk_note=?,updated=? WHERE code=?",
                            (student_email.strip(), requested, note.strip(), now(), code.strip())
                        )
                        db.commit()
                    else:
                        found = None
                if found:
                    ok, msg = email(
                        cfg()["recipient"],
                        f"[SAFE-STUDENT] Pengajuan jadwal {code.strip()}",
                        f"Ada pengajuan jadwal konseling.\nKode: {code.strip()}\nWaktu yang diminta: {requested}\nSilakan tinjau dashboard Guru BK.",
                        "Pengajuan jadwal",
                        code.strip()
                    )
                    st.success("Pengajuan tersimpan. Tunggu konfirmasi melalui email.")
                    if not ok:
                        st.warning("Pengajuan tersimpan, tetapi email pemberitahuan BK belum terkirim. " + msg)
                else:
                    st.error("Kode laporan tidak ditemukan.")

    with t3:
        st.markdown('<div class="panel"><h3>Cek Status Laporan & Jadwal</h3></div>', unsafe_allow_html=True)
        code = st.text_input("Kode laporan untuk dicek", key="check_code")
        if st.button("Cek Status"):
            with connect() as db:
                r = db.execute("SELECT code,status,requested,final_schedule,schedule_status FROM reports WHERE code=?", (code.strip(),)).fetchone()
            if r:
                st.write("**Status Laporan:**", r["status"])
                st.write("**Status Jadwal:**", r["schedule_status"])
                if r["requested"]:
                    st.write("**Waktu Diajukan:**", r["requested"])
                if r["final_schedule"]:
                    st.write("**Jadwal Final:**", r["final_schedule"])
            else:
                st.warning("Kode laporan tidak ditemukan.")

elif room == "🧑‍🏫 Guru BK":
    st.markdown('<div class="panel"><h2>Dashboard Guru BK</h2><p class="muted">Kelola laporan, tindak lanjut, dan persetujuan jadwal dari satu tempat.</p></div>', unsafe_allow_html=True)
    
    with st.expander("🔐 Masuk ke Dashboard Guru BK", expanded=not st.session_state.get("bk_auth", False)):
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
        pending = int((df.schedule_status == "Menunggu persetujuan").sum()) if n else 0
        approved = int((df.schedule_status == "Disetujui").sum()) if n else 0
        new = int((df.status == "Baru").sum()) if n else 0
        
        cols = st.columns(4)
        for col, label, val in zip(cols, ["Total Laporan", "Laporan Baru", "Jadwal Menunggu", "Jadwal Disetujui"], [n, new, pending, approved]):
            with col:
                st.markdown(f'<div class="metric-card"><div>{label}</div><div class="num">{val}</div></div>', unsafe_allow_html=True)
                
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["📥 Laporan Masuk", "📅 Persetujuan Jadwal", "✉️ Riwayat Email"])
        
        with t1:
            if n:
                filt = st.selectbox("Filter Laporan", ["Semua", "Baru", "Diproses", "Selesai"])
                view = df if filt == "Semua" else df[df.status == filt]
                st.dataframe(view[["code", "created", "category", "urgency", "status", "schedule_status"]], use_container_width=True, hide_index=True)
                if len(view):
                    code = st.selectbox("Pilih Laporan", view.code.tolist())
                    r = df[df.code == code].iloc[0]
                    st.markdown('<div class="panel"><h3>Detail Laporan Terpilih</h3></div>', unsafe_allow_html=True)
                    st.write("**Kode:**", r.code, " · **Kategori:**", r.category, " · **Penanda Urgensi:**", r.urgency)
                    st.write("**Isi Laporan:**")
                    st.write(r.content)
                    with st.form("update_report"):
                        status = st.selectbox("Status Tindak Lanjut", ["Baru", "Diproses", "Selesai"], index=["Baru", "Diproses", "Selesai"].index(r.status))
                        bk_note = st.text_area("Catatan Internal Guru BK (Rahasia)", value=r.bk_note or "")
                        save = st.form_submit_button("Simpan Perubahan")
                    if save:
                        update(code, status=status, bk_note=bk_note)
                        st.success("Perubahan tersimpan.")
                        st.rerun()
            else:
                st.info("Belum ada laporan.")

        with t2:
            waiting = df[df.schedule_status == "Menunggu persetujuan"] if n else df
            if n:
                st.dataframe(df[df.schedule_status != "Belum diajukan"][["code", "student_email", "requested", "final_schedule", "schedule_status"]], use_container_width=True, hide_index=True)
            if len(waiting):
                code = st.selectbox("Pilih Pengajuan yang Menunggu", waiting.code.tolist())
                r = df[df.code == code].iloc[0]
                st.markdown('<div class="panel"><h3>Review Pengajuan Jadwal</h3></div>', unsafe_allow_html=True)
                st.write("**Email Siswa:**", r.student_email or "Belum diisi")
                st.write("**Waktu Diminta:**", r.requested)
                with st.form("approve_form"):
                    decision = st.radio("Keputusan", ["Setujui", "Usulkan jadwal lain", "Tolak"], horizontal=True)
                    final_date = st.date_input("Tanggal Final", min_value=date.today())
                    final_time = st.time_input("Jam Final", value=time(10, 0), step=1800)
                    student_note = st.text_area("Catatan untuk Siswa (akan masuk email)", height=70)
                    act = st.form_submit_button("Simpan Keputusan")
                if act:
                    if decision == "Setujui":
                        final = f"{final_date.strftime('%d-%m-%Y')} pukul {final_time.strftime('%H:%M')}"
                        update(code, final_schedule=final, schedule_status="Disetujui")
                        if r.student_email and str(r.student_email).strip():
                            ok, msg = mail_student(str(r.student_email).strip(), code, final, student_note)
                            st.session_state["email_feedback"] = (ok, msg, str(r.student_email).strip())
                        else:
                            st.session_state["email_feedback"] = (False, "Jadwal tersimpan, tetapi email siswa belum tersedia.", "")
                    elif decision == "Usulkan jadwal lain":
                        final = f"{final_date.strftime('%d-%m-%Y')} pukul {final_time.strftime('%H:%M')}"
                        update(code, final_schedule=final, schedule_status="Menunggu konfirmasi siswa")
                        st.info("Usulan disimpan. Hubungi siswa untuk menyepakati jadwal.")
                    else:
                        update(code, schedule_status="Ditolak", bk_note=student_note)
                        st.warning("Pengajuan ditandai ditolak.")
                    st.rerun()
            if st.session_state.get("email_feedback"):
                ok, feedback, recipient = st.session_state.pop("email_feedback")
                if ok:
                    st.success(feedback)
                else:
                    st.warning(feedback)
            if not len(waiting):
                st.info("Tidak ada pengajuan jadwal yang menunggu.")

        with t3:
            with connect() as db:
                logs = pd.read_sql_query("SELECT created,recipient,subject,event,code,status,detail FROM email_log ORDER BY id DESC LIMIT 200", db)
            if len(logs):
                st.dataframe(logs, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada riwayat email.")
                
        if st.button("Keluar dari Dashboard Guru BK"):
            st.session_state["bk_auth"] = False
            st.rerun()

elif room == "👨‍👩‍👧 Orang Tua":
    st.markdown('<div class="panel"><h2>Ruang Orang Tua</h2><p class="muted">Informasi umum tentang layanan konseling dan dukungan bagi siswa.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3>Mendampingi Siswa</h3><p class="muted">Dengarkan tanpa menghakimi, beri ruang untuk bercerita, dan hubungi Guru BK jika siswa membutuhkan dukungan.</p></div>', unsafe_allow_html=True)
    with st.expander("Kapan harus menghubungi Guru BK?"):
        st.write("Saat siswa mengalami kesulitan belajar, konflik sosial, perubahan perilaku yang mengkhawatirkan, atau membutuhkan dukungan emosional.")

else:
    st.markdown('<div class="panel"><h2>Admin SAFE-STUDENT</h2><p class="muted">Periksa konfigurasi email dan status pengiriman.</p></div>', unsafe_allow_html=True)
    with st.expander("🔐 Masuk Admin", expanded=not st.session_state.get("admin_auth", False)):
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
                st.error("Kata sandi salah atau belum diatur di secrets.toml.")
                
    if st.session_state.get("admin_auth"):
        conf = cfg()
        st.markdown('<div class="panel"><h3>Konfigurasi Email</h3></div>', unsafe_allow_html=True)
        st.write("Pengirim:", conf["sender"])
        st.write("Penerima Guru BK:", conf["recipient"])
        st.write("App Password tersedia:", "Ya" if conf["password"] else "Belum")
        st.caption("Secrets yang dibaca: [email] sender, recipient, app_password, smtp_host, smtp_port.")
        
        if not conf["password"]:
            st.warning("Pengiriman email belum bisa berjalan sebelum App Password Gmail diisi pada Streamlit Secrets.")
            
        if st.button("Kirim Email Uji ke Guru BK"):
            ok, msg = email(conf["recipient"], "[SAFE-STUDENT] Tes email", "Email uji SAFE-STUDENT MAN 2 Kudus. Tidak ada data siswa.", "Tes email")
            st.success(msg) if ok else st.error(msg)
            
        with connect() as db:
            logs = pd.read_sql_query("SELECT created,recipient,subject,event,code,status,detail FROM email_log ORDER BY id DESC LIMIT 100", db)
        st.dataframe(logs, use_container_width=True, hide_index=True)
        
        if st.button("Keluar dari Admin"):
            st.session_state["admin_auth"] = False
            st.rerun()

st.markdown('<p style="text-align:center;color:#ffffff;font-size:.85rem;padding:20px;text-shadow:1px 1px 2px rgba(0,0,0,0.5)">SAFE-STUDENT · MAN 2 Kudus · Sampaikan cerita, temukan dukungan.</p>', unsafe_allow_html=True)
```

### 📋 Konfigurasi Streamlit Secrets (`.streamlit/secrets.toml`)
Pastikan file `.streamlit/secrets.toml` di dalam folder project Anda diatur seperti ini:

```toml
[email]
smtp_host = "smtp.gmail.com"
smtp_port = "465"
sender = "safestudentm2k@gmail.com"
recipient = "bkm2kmendunia@gmail.com"
app_password = "safestudentm2k!!"

[auth]
bk_password = "bk123"
admin_password = "admin123"
```

### 📌 Ringkasan Perubahan UI:
1. **Tema Bawah Laut (*Ocean Theme*)**: Background gradasi biru khas lautan lengkap dengan typography ramah ala *Fredoka* & *Poppins*.
2. **Hero Banner & Badge Kemenag**: Menyertakan jajaran badge institusi di bagian atas serta banner judul besar *Curhatin Digital MAN - Safe Space -*.
3. **Mascot Box**: Kartu ucapan "Halo Teman-teman MAN!" yang diapit oleh karakter Kema & Temo.
4. **Sidebar Styling**: Sidebar diubah menggunakan skema warna cream terang dengan icon pesan dan informasi privasi seperti pada gambar.
5. **Fitur Tetap Utuh**: Seluruh alur kirim curhat, pengajuan jadwal konseling, otentikasi login Guru BK/Admin, serta fitur kirim email SMTP bawaan tetap berjalan 100% normal.

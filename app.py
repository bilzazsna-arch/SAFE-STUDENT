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

st.set_page_config(page_title="SAFE-STUDENT | MAN 2 Kudus", page_icon="🦀", layout="wide")

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
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
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
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap');

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

/* Posisi logo sekolah tepat di tengah */
.logo-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(7,59,102,0.92) 0%, rgba(7,89,133,0.92) 58%, rgba(14,116,144,0.92) 100%);
    backdrop-filter: blur(8px);
    border-right: 1px solid rgba(255,255,255,0.15);
}}
[data-testid="stSidebar"] * {{
    color: white !important;
}}

/* Hero Banner Utama */
.hero {{
    background: linear-gradient(120deg, rgba(7,59,102,0.85) 0%, rgba(8,127,168,0.85) 60%, rgba(8,145,178,0.85) 100%);
    backdrop-filter: blur(6px);
    color: white;
    border-radius: 26px;
    padding: 24px 32px;
    margin: 8px 0 20px 0;
    box-shadow: 0 16px 36px rgba(6, 75, 108, 0.25);
    border: 2px solid rgba(255, 255, 255, 0.3);
    text-align: center;
}}
.hero h1 {{
    font-family: 'Fredoka', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.8rem);
    line-height: 1.1;
    margin: 6px 0;
    color: #ffd45c;
    text-shadow: 0 3px 6px rgba(0,0,0,0.3);
}}

/* Panel & Card Styling */
.panel {{
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(8px);
    border: 1px solid #bae6fd;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(8, 59, 102, 0.15);
}}

.metric {{
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #bae6fd;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(8, 59, 102, 0.1);
}}
.metric .num {{
    font-family: 'Fredoka', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #0284c7;
}}

.muted {{
    color: #334155;
    font-size: 0.95rem;
}}

/* Buttons & Forms */
div.stButton > button, div.stFormSubmitButton > button {{
    border: 0;
    border-radius: 14px;
    background: linear-gradient(90deg, #0284c7, #0891b2);
    color: white;
    font-weight: 700;
    min-height: 2.8rem;
    box-shadow: 0 6px 16px rgba(2, 132, 199, 0.3);
    transition: transform 0.15s ease;
    width: 100%;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    color: white;
    transform: translateY(-2px);
}}

div[data-testid="stForm"] {{
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #bae6fd;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 24px rgba(8, 59, 102, 0.12);
}}

[data-testid="stTabs"] button {{
    font-weight: 700;
    font-size: 1rem;
}}

[data-testid="stDataFrame"] {{
    border-radius: 16px;
    overflow: hidden;
}}

[data-testid="stImage"] img {{
    object-fit: contain;
}}
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
    st.markdown("## 🦀 SAFE-STUDENT")
    st.caption("Layanan Pelaporan & Konseling Digital MAN 2 Kudus")
    room = st.radio("Pilih Ruang Akses", ["✨ Siswa (Curhat & Jadwal)", "🧑‍🏫 Guru BK", "👨‍👩‍👧 Orang Tua", "🔐 Admin"])
    st.markdown("---")
    st.caption("Sampaikan cerita, temukan dukungan.")

def hero(title="Curhatin Digital MAN", subtitle="- Safe Space -"):
    st.markdown(f'<div class="hero"><div style="font-size:0.85rem;letter-spacing:2px;font-weight:700;color:#baefff;margin-bottom:4px;">🌊 DIGITAL MAN · MAN 2 KUDUS</div><h1>{title}</h1><p style="font-weight:600;color:#ffd45c;font-size:1.1rem;margin-top:4px;">{subtitle}</p></div>', unsafe_allow_html=True)

if room == "✨ Siswa (Curhat & Jadwal)":
    # Menempatkan logo di tengah menggunakan 3 kolom
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        image_if_exists("Logo_MAN2.png", 140)
    
    hero("Curhatin Digital MAN", "- Safe Space -")
    
    # Layout Maskot Temo dan Sambutan
    col_a, col_b = st.columns([1, 2.5])
    with col_a:
        image_if_exists("kepiting_cowo.png", 160)
        st.markdown("<div style='text-align:center;font-weight:700;color:#ffffff;text-shadow: 0 2px 4px rgba(0,0,0,0.5);margin-top:4px;'>Temo · Sahabatmu</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="panel" style="padding:22px;">
            <h3 style="margin-bottom:6px;color:#073b66;font-family:'Fredoka',sans-serif;">Halo Teman-teman MAN! 💙</h3>
            <p class="muted" style="margin-bottom:0;">
                Aku Temo, penjaga kerahasiaan curhatmu. Apapun masalahmu di sekolah, curhatkan di sini dengan aman dan anonim!
            </p>
        </div>
        """, unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["💬 Tulis Curhat", "📅 Ajukan Jadwal", "🔎 Cek Status"])
    with t1:
        st.markdown('<div class="panel" style="margin-bottom:10px;"><h3 style="color:#073b66;margin-bottom:0;">🛡️ Formulir Curhat Anonim (Bebas & Aman)</h3></div>', unsafe_allow_html=True)
        with st.form("report_form", clear_on_submit=True):
            category = st.selectbox("Kategori", ["Perundungan / bullying", "Stres belajar & tahfidz", "Keluarga atau masalah pribadi", "Konsultasi agama / moral", "Lainnya"])
            content = st.text_area("Ceritakan yang ingin disampaikan", height=150, placeholder="Tulis curhatanmu di sini...")
            optional_email = st.text_input("Email aktif untuk konfirmasi jadwal (opsional)", placeholder="contoh@email.com")
            use_email = st.checkbox("Saya ingin menggunakan email ini untuk konfirmasi jadwal.")
            send = st.form_submit_button("Kirim Laporan", use_container_width=True)
        if send:
            if len(content.strip()) < 8: 
                st.error("Ceritakan sedikit lebih lengkap (minimal 8 karakter).")
            else:
                urgency, sc = score_text(content)
                code = "MAN2-" + datetime.now().strftime("%y%m%d") + "-" + secrets.token_hex(3).upper()
                with connect() as db:
                    db.execute("INSERT INTO reports(code,created,category,content,urgency,score,status,student_email,schedule_status,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
                               (code, now(), category, content.strip(), urgency, sc, "Baru", optional_email.strip() if use_email else "", "Belum diajukan", now()))
                    db.commit()
                mail_bk(code, category, urgency)
                st.success(f"Laporan tersimpan. Simpan kode laporanmu: {code}")
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

elif room == "🧑‍🏫 Guru BK":
    hero("Dashboard Guru BK", "Kelola laporan, tindak lanjut, dan persetujuan jadwal.")
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
        t1, t2, t3 = st.tabs(["📥 Laporan masuk", "📅 Persetujuan jadwal", "✉️ Riwayat email"])
        with t1:
            if n:
                selected_code = st.selectbox("Pilih laporan", df.code.tolist())
                r = df[df.code == selected_code].iloc[0]
                st.write("**Isi laporan:**")
                st.write(r.content)
                with st.form("update_report"):
                    status = st.selectbox("Status", ["Baru", "Diproses", "Selesai"], index=["Baru", "Diproses", "Selesai"].index(r.status))
                    bk_note = st.text_area("Catatan internal BK", value=r.bk_note or "")
                    if st.form_submit_button("Simpan"):
                        update(selected_code, status=status, bk_note=bk_note)
                        st.success("Tersimpan!")
                        st.rerun()
        with t2:
            waiting = df[df.schedule_status == "Menunggu persetujuan"] if n else pd.DataFrame()
            if len(waiting):
                sel_w = st.selectbox("Pilih pengajuan", waiting.code.tolist(), key="sel_w")
                rw = df[df.code == sel_w].iloc[0]
                with st.form("appr"):
                    dec = st.radio("Keputusan", ["Setujui", "Tolak"])
                    if st.form_submit_button("Proses"):
                        if dec == "Setujui":
                            update(sel_w, schedule_status="Disetujui")
                            if rw.student_email: 
                                mail_student(rw.student_email, sel_w, rw.requested)
                        else:
                            update(sel_w, schedule_status="Ditolak")
                        st.success("Berhasil diproses!")
                        st.rerun()
        with t3:
            with connect() as db: 
                logs = pd.read_sql_query("SELECT created,recipient,subject,event,code,status FROM email_log ORDER BY id DESC LIMIT 100", db)
            if len(logs): 
                st.dataframe(logs, use_container_width=True, hide_index=True)
        if st.button("Keluar"): 
            st.session_state["bk_auth"] = False
            st.rerun()

elif room == "👨‍👩‍👧 Orang Tua":
    hero("Ruang Orang Tua", "Informasi umum mengenai layanan konseling.")
    st.markdown('<div class="panel"><h3>Pendampingan Siswa</h3><p class="muted">Hubungi Guru BK jika siswa membutuhkan dukungan lebih lanjut.</p></div>', unsafe_allow_html=True)

else:
    hero("Admin SAFE-STUDENT", "Konfigurasi dan Status Sistem.")
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
                st.error("Kata sandi salah.")
    if st.session_state.get("admin_auth"):
        conf = cfg()
        st.write("Pengirim:", conf["sender"])
        st.write("Penerima:", conf["recipient"])
        if st.button("Keluar Admin"): 
            st.session_state["admin_auth"] = False
            st.rerun()

st.markdown('<p style="text-align:center;color:#ffffff;text-shadow: 0 1px 3px rgba(0,0,0,0.6);font-weight:600;font-size:.85rem;padding:20px">SAFE-STUDENT · MAN 2 Kudus · Sampaikan cerita, temukan dukungan.</p>', unsafe_allow_html=True)

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
:root{--navy:#073b66;--blue:#087fa8;--cyan:#16b8c8;--gold:#ffd45c;--ink:#12344a}
html,body,[class*="css"]{font-family:Poppins,sans-serif}
.stApp{background:linear-gradient(145deg,#e9faff,#f8fdff 54%,#d8f3ff);color:var(--ink)}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1380px;padding-top:1rem;padding-bottom:2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#073b66 0%,#075985 58%,#0e7490 100%)}
[data-testid="stSidebar"] *{color:white!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:7px 9px;border-radius:10px}

.hero{
    background:linear-gradient(120deg,#073b66 0%,#087fa8 62%,#0891b2 100%);
    color:white;
    border-radius:26px;
    padding:24px 30px;
    margin:8px 0 20px;
    box-shadow:0 14px 32px #064b6c20;
    border:1px solid #ffffff22;
    position:relative;
    overflow:hidden;
}
.hero:after{content:"";position:absolute;width:180px;height:180px;border-radius:50%;right:-45px;top:-75px;background:#ffffff12}
.hero .eyebrow{font-size:.82rem;letter-spacing:2px;font-weight:700;color:#bcefff}
.hero h1{font-family:Fredoka,sans-serif;font-size:clamp(2rem,4.5vw,3.5rem);line-height:1.05;margin:6px 0;color:var(--gold);text-shadow:0 3px 0 #8a551d35}
.hero p{color:#e7f9ff;margin-bottom:0;max-width:760px}

.panel{background:#ffffffed;border:1px solid #d7edf7;border-radius:20px;padding:20px;margin-bottom:15px;box-shadow:0 8px 24px #083b6610}
.metric{background:linear-gradient(145deg,#fff,#f3fbff);border:1px solid #d7edf7;border-radius:18px;padding:17px;box-shadow:0 5px 18px #083b660c}
.metric .num{font-family:Fredoka,sans-serif;font-size:1.9rem;font-weight:700;color:#075985}
.muted{color:#587789;font-size:.9rem}

div.stButton>button,div.stFormSubmitButton>button{border:0;border-radius:13px;background:linear-gradient(90deg,#0879b9,#0891b2);color:white;font-weight:700;min-height:2.7rem;box-shadow:0 5px 12px #0879b926;transition:transform .15s ease}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{color:white;border:0;transform:translateY(-1px)}
div[data-testid="stForm"]{background:#fff;border:1px solid #d7edf7;border-radius:18px;padding:18px}
[data-testid="stTabs"] button{font-weight:600}
[data-testid="stDataFrame"]{border-radius:14px;overflow:hidden}
[data-testid="stImage"] img{object-fit:contain}
@media(max-width:700px){.block-container{padding:1rem .8rem}.hero{padding:20px 16px;border-radius:20px}.panel{padding:15px}.hero h1{font-size:2.2rem}}
</style>
""", unsafe_allow_html=True)

def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        return {"sender":e.get("sender",SENDER), "password":e.get("app_password",""),
                "recipient":e.get("recipient",BK_EMAIL), "host":e.get("smtp_host","smtp.gmail.com"),
                "port":int(e.get("smtp_port",465))}
    except Exception:
        return {"sender":os.getenv("SAFE_EMAIL_SENDER",SENDER),
                "password":os.getenv("SAFE_EMAIL_APP_PASSWORD",""),
                "recipient":os.getenv("SAFE_EMAIL_RECIPIENT",BK_EMAIL),
                "host":"smtp.gmail.com","port":465}

def log_mail(to, subject, event, code, status, detail=""):
    with connect() as c:
        c.execute("INSERT INTO email_log(created,recipient,subject,event,code,status,detail) VALUES(?,?,?,?,?,?,?)",
                  (now(),to,subject,event,code,status,detail[:300]))
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

def mail_bk(code,category,urgency):
    to=cfg()["recipient"]
    body=f"""Halo Guru BK MAN 2 Kudus,

Ada laporan baru di SAFE-STUDENT.
Kode laporan: {code}
Kategori: {category}
Penanda urgensi otomatis: {urgency}

Isi curhat tidak dicantumkan dalam email demi menjaga privasi.
Silakan masuk ke dashboard Guru BK untuk meninjau laporan.

SAFE-STUDENT MAN 2 Kudus"""
    return email(to,f"[SAFE-STUDENT] Laporan baru {code}",body,"Laporan baru",code)

def mail_student(to,code,schedule,note=""):
    body=f"""Halo,

Pengajuan jadwal konseling kamu telah disetujui Guru BK MAN 2 Kudus.

Kode pengajuan: {code}
Jadwal yang disepakati: {schedule}
Lokasi: ruang BK MAN 2 Kudus.
"""
    if note.strip(): body += f"\nCatatan untuk kamu: {note.strip()}\n"
    body += "\nSAFE-STUDENT MAN 2 Kudus"
    return email(to,f"[SAFE-STUDENT] Jadwal disetujui - {code}",body,"Persetujuan jadwal",code)

def score_text(txt):
    t=txt.lower()
    high=["diancam","dipukul","kekerasan","takut pulang","tidak aman"]
    med=["bullying","dibully","cemas","panik","stres","tertekan","sedih","konflik"]
    n=3*sum(x in t for x in high)+sum(x in t for x in med)
    return ("MERAH" if n>=3 else "KUNING" if n else "HIJAU"),n

def reports():
    with connect() as c: return pd.read_sql_query("SELECT * FROM reports ORDER BY created DESC",c)

def update(code, **kw):
    allowed={"status","final_schedule","schedule_status","bk_note"}
    vals={k:v for k,v in kw.items() if k in allowed}
    vals["updated"]=now()
    with connect() as c:
        c.execute("UPDATE reports SET "+", ".join(k+"=?" for k in vals)+" WHERE code=?",
                  list(vals.values())+[code]); c.commit()

def image_if_exists(name,width=None):
    p=BASE/name
    if p.exists(): st.image(str(p),width=width,use_container_width=(width is None))

with st.sidebar:
    st.markdown("## 🦀 SAFE-STUDENT")
    st.caption("Layanan Pelaporan & Konseling Digital MAN 2 Kudus")
    room=st.radio("Pilih Ruang Akses",["✨ Siswa (Curhat & Jadwal)","🧑‍🏫 Guru BK","👨‍👩‍👧 Orang Tua","🔐 Admin"])
    st.markdown("---")
    st.caption("Sampaikan cerita, temukan dukungan.")

def hero(title="Curhatin Digital MAN", subtitle="Safe Space - Tempat bercerita, meminta bantuan, dan menjadwalkan konseling dengan lebih nyaman."):
    st.markdown(f'<div class="hero"><div class="eyebrow">🌊 DIGITAL MAN · MAN 2 KUDUS</div><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)

if room=="✨ Siswa (Curhat & Jadwal)":
    if (BASE / "Logo_MAN2.png").exists():
        st.image(str(BASE / "Logo_MAN2.png"), width=220)
    
    hero("Curhatin Digital MAN - Safe Space -")
    
    col_a, col_b = st.columns([1, 2.5])
    with col_a:
        image_if_exists("kepiting_cowo.png", 150)
        st.markdown("<div style='font-weight:700;color:#075985;margin-top:5px;'>Temo · Sahabatmu</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="panel" style="padding:22px;">
            <h3 style="margin-bottom:8px; color:#073b66;">Halo Teman-teman MAN! 💙</h3>
            <p class="muted" style="margin-bottom:0; font-size: 1.02rem;">
                Aku Temo, penjaga kerahasiaan curhatmu. Apapun masalahmu di sekolah, curhatkan di sini dengan aman dan anonim!
            </p>
        </div>
        """, unsafe_allow_html=True)

    t1,t2,t3=st.tabs(["💬 Tulis Curhat","📅 Ajukan Jadwal","🔎 Cek Status"])
    with t1:
        st.markdown('<div class="panel"><h3>🛡️ Formulir Curhat Anonim (Bebas & Aman)</h3></div>',unsafe_allow_html=True)
        with st.form("report_form",clear_on_submit=True):
            category=st.selectbox("Kategori",["Perundungan / bullying","Stres belajar & tahfidz","Keluarga atau masalah pribadi","Konsultasi agama / moral","Lainnya"])
            content=st.text_area("Ceritakan yang ingin disampaikan",height=160)
            optional_email=st.text_input("Email aktif untuk konfirmasi jadwal (opsional)")
            use_email=st.checkbox("Saya ingin menggunakan email ini untuk konfirmasi jadwal.")
            send=st.form_submit_button("Kirim Laporan",use_container_width=True)
        if send:
            if len(content.strip())<8: st.error("Ceritakan sedikit lebih lengkap (minimal 8 karakter).")
            else:
                urgency,sc=score_text(content)
                code="MAN2-"+datetime.now().strftime("%y%m%d")+"-"+secrets.token_hex(3).upper()
                with connect() as db:
                    db.execute("INSERT INTO reports(code,created,category,content,urgency,score,status,student_email,schedule_status,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
                               (code,now(),category,content.strip(),urgency,sc,"Baru",optional_email.strip() if use_email else "","Belum diajukan",now()))
                    db.commit()
                mail_bk(code,category,urgency)
                st.success(f"Laporan tersimpan. Simpan kode laporanmu: {code}")
    with t2:
        st.markdown('<div class="panel"><h3>Pengajuan Jadwal Tatap Muka</h3></div>',unsafe_allow_html=True)
        with st.form("schedule_form",clear_on_submit=True):
            code_input=st.text_input("Kode laporan")
            student_email=st.text_input("Email aktif untuk menerima konfirmasi")
            d=st.date_input("Tanggal yang diinginkan",min_value=date.today())
            tm=st.time_input("Waktu yang diinginkan",value=time(10,0),step=1800)
            note=st.text_area("Catatan singkat (opsional)",height=70)
            send_req=st.form_submit_button("Kirim Pengajuan Jadwal",use_container_width=True)
        if send_req:
            if not code_input.strip():
                st.error("Masukkan kode laporan yang valid.")
            else:
                with connect() as db:
                    found=db.execute("SELECT code FROM reports WHERE code=?",(code_input.strip(),)).fetchone()
                    if found:
                        requested=f"{d.strftime('%d-%m-%Y')} pukul {tm.strftime('%H:%M')}"
                        db.execute("UPDATE reports SET student_email=?,requested=?,schedule_status='Menunggu persetujuan',bk_note=?,updated=? WHERE code=?",
                                   (student_email.strip(),requested,note.strip(),now(),code_input.strip()))
                        db.commit()
                if found:
                    st.success("Pengajuan tersimpan. Tunggu konfirmasi melalui email.")
                else: st.error("Kode laporan tidak ditemukan.")
    with t3:
        st.markdown('<div class="panel"><h3>Cek Status Laporan & Jadwal</h3></div>',unsafe_allow_html=True)
        check_code=st.text_input("Kode laporan untuk dicek",key="check_code")
        if st.button("Cek Status"):
            with connect() as db: r=db.execute("SELECT code,status,requested,final_schedule,schedule_status FROM reports WHERE code=?",(check_code.strip(),)).fetchone()
            if r:
                st.write("**Status laporan:**",r["status"])
                st.write("**Status jadwal:**",r["schedule_status"])
                if r["requested"]: st.write("**Waktu diajukan:**",r["requested"])
                if r["final_schedule"]: st.write("**Jadwal final:**",r["final_schedule"])
            else: st.warning("Kode laporan tidak ditemukan.")

elif room=="🧑‍🏫 Guru BK":
    hero("Dashboard Guru BK","Kelola laporan, tindak lanjut, dan persetujuan jadwal.")
    with st.expander("🔐 Masuk ke dashboard Guru BK",expanded=not st.session_state.get("bk_auth",False)):
        pw=st.text_input("Kata sandi Guru BK",type="password",key="bk_pw")
        if st.button("Masuk Guru BK"):
            try: expected=st.secrets.get("auth",{}).get("bk_password","")
            except Exception: expected=""
            if expected and secrets.compare_digest(pw,expected):
                st.session_state["bk_auth"]=True; st.rerun()
            else: st.error("Kata sandi salah atau belum diatur di secrets.toml.")
    if st.session_state.get("bk_auth"):
        df=reports(); n=len(df)
        cols=st.columns(4)
        for col,label,val in zip(cols,["Total laporan","Laporan baru","Jadwal menunggu","Jadwal disetujui"],
                                  [n, int((df.status=="Baru").sum()) if n else 0, int((df.schedule_status=="Menunggu persetujuan").sum()) if n else 0, int((df.schedule_status=="Disetujui").sum()) if n else 0]):
            with col: st.markdown(f'<div class="metric"><div>{label}</div><div class="num">{val}</div></div>',unsafe_allow_html=True)
        t1,t2,t3=st.tabs(["📥 Laporan masuk","📅 Persetujuan jadwal","✉️ Riwayat email"])
        with t1:
            if n:
                selected_code=st.selectbox("Pilih laporan",df.code.tolist())
                r=df[df.code==selected_code].iloc[0]
                st.write("**Isi laporan:**"); st.write(r.content)
                with st.form("update_report"):
                    status=st.selectbox("Status",["Baru","Diproses","Selesai"],index=["Baru","Diproses","Selesai"].index(r.status))
                    bk_note=st.text_area("Catatan internal BK",value=r.bk_note or "")
                    if st.form_submit_button("Simpan"):
                        update(selected_code,status=status,bk_note=bk_note)
                        st.success("Tersimpan!"); st.rerun()
        with t2:
            waiting=df[df.schedule_status=="Menunggu persetujuan"] if n else pd.DataFrame()
            if len(waiting):
                sel_w=st.selectbox("Pilih pengajuan",waiting.code.tolist(),key="sel_w")
                rw=df[df.code==sel_w].iloc[0]
                with st.form("appr"):
                    dec=st.radio("Keputusan",["Setujui","Tolak"])
                    if st.form_submit_button("Proses"):
                        if dec=="Setujui":
                            update(sel_w,schedule_status="Disetujui")
                            if rw.student_email: mail_student(rw.student_email, sel_w, rw.requested)
                        else:
                            update(sel_w,schedule_status="Ditolak")
                        st.success("Berhasil diproses!"); st.rerun()
        with t3:
            with connect() as db: logs=pd.read_sql_query("SELECT created,recipient,subject,event,code,status FROM email_log ORDER BY id DESC LIMIT 100",db)
            if len(logs): st.dataframe(logs,use_container_width=True,hide_index=True)
        if st.button("Keluar"): st.session_state["bk_auth"]=False; st.rerun()

elif room=="👨‍👩‍👧 Orang Tua":
    hero("Ruang Orang Tua","Informasi umum mengenai layanan konseling.")
    st.markdown('<div class="panel"><h3>Pendampingan Siswa</h3><p class="muted">Hubungi Guru BK jika siswa membutuhkan dukungan lebih lanjut.</p></div>',unsafe_allow_html=True)

else:
    hero("Admin SAFE-STUDENT","Konfigurasi dan Status Sistem.")
    with st.expander("🔐 Masuk Admin",expanded=not st.session_state.get("admin_auth",False)):
        pw=st.text_input("Kata sandi Admin",type="password",key="admin_pw")
        if st.button("Masuk Admin"):
            try: expected=st.secrets.get("auth",{}).get("admin_password","")
            except Exception: expected=""
            if expected and secrets.compare_digest(pw,expected): st.session_state["admin_auth"]=True; st.rerun()
            else: st.error("Kata sandi salah.")
    if st.session_state.get("admin_auth"):
        conf=cfg()
        st.write("Pengirim:",conf["sender"]); st.write("Penerima:",conf["recipient"])
        if st.button("Keluar Admin"): st.session_state["admin_auth"]=False; st.rerun()

st.markdown('<p style="text-align:center;color:#587789;font-size:.8rem;padding:20px">SAFE-STUDENT · MAN 2 Kudus</p>', unsafe_allow_html=True)

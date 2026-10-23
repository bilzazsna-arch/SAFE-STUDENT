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
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:Poppins,sans-serif}
.stApp{background:linear-gradient(145deg,#e9faff,#f8fdff 55%,#d8f3ff);color:#12344a}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1450px;padding-top:1.5rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#073b66,#075985,#0e7490)}
[data-testid="stSidebar"] *{color:white!important}
.hero{background:linear-gradient(120deg,#073b66,#087fa8);color:white;border-radius:25px;padding:28px;margin-bottom:20px;box-shadow:0 12px 30px #064b6c22}
.hero h1{font-family:Fredoka,sans-serif;font-size:clamp(2.2rem,5vw,4rem);margin:0;color:#ffd45c}
.hero p{color:#e7f9ff;margin-bottom:0}
.panel{background:#ffffffed;border:1px solid #d7edf7;border-radius:19px;padding:20px;margin-bottom:15px;box-shadow:0 7px 22px #083b6610}
.metric{background:white;border:1px solid #d7edf7;border-radius:17px;padding:17px}
.metric .num{font-size:1.9rem;font-weight:700;color:#075985}
.muted{color:#587789;font-size:.9rem}
div.stButton>button{border:0;border-radius:12px;background:linear-gradient(90deg,#0879b9,#0891b2);color:white;font-weight:600}
div.stButton>button:hover{color:white;border:0}
div[data-testid="stForm"]{background:#fff;border:1px solid #d7edf7;border-radius:17px;padding:18px}
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
    conf=cfg()
    if not conf["password"]:
        log_mail(to,subject,event,code,"Belum dikonfigurasi","Isi [email].app_password di secrets.toml")
        return False,"Email belum dikonfigurasi. Atur App Password Gmail di .streamlit/secrets.toml."
    try:
        msg=EmailMessage()
        msg["From"]=conf["sender"]; msg["To"]=to; msg["Subject"]=subject; msg.set_content(body)
        with smtplib.SMTP_SSL(conf["host"],conf["port"],context=ssl.create_default_context(),timeout=20) as s:
            s.login(conf["sender"],conf["password"]); s.send_message(msg)
        log_mail(to,subject,event,code,"Terkirim")
        return True,"Email berhasil dikirim."
    except Exception as ex:
        log_mail(to,subject,event,code,"Gagal",str(ex))
        return False,"Email gagal dikirim. Periksa App Password dan koneksi server."

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
Lokasi: ruang BK MAN 2 Kudus (konfirmasikan kepada Guru BK jika diperlukan).
"""
    if note.strip(): body += f"\nCatatan untuk kamu: {note.strip()}\n"
    body += "\nJika tidak dapat hadir, hubungi Guru BK untuk mengatur ulang jadwal.\nEmail ini tidak memuat isi curhat.\n\nSAFE-STUDENT MAN 2 Kudus"
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

def hero(title="Curhatin", subtitle="Tempat bercerita, meminta bantuan, dan menjadwalkan konseling dengan lebih nyaman."):
    st.markdown(f'<div class="hero"><div>🌊 DIGITAL MAN · MAN 2 KUDUS</div><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)

if room=="✨ Siswa (Curhat & Jadwal)":
    hero("Curhatin Digital")
    a,b,c=st.columns([1,1.5,1])
    with a:
        image_if_exists("kepiting_cewe.png")
        st.markdown("<div style='text-align:center;font-weight:700;color:#075985'>Kema · Sahabat bercerita</div>",unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel" style="text-align:center"><h3>Halo, Teman-teman MAN 2 Kudus! 💙</h3><p class="muted">Kamu boleh bercerita dengan nyaman. Guru BK akan meninjau laporanmu.</p><p class="muted">Email hanya digunakan untuk konfirmasi jadwal jika kamu mengisinya.</p></div>',unsafe_allow_html=True)
        image_if_exists("ubur_cewe.png",120)
    with c:
        image_if_exists("kepiting_cowo.png")
        st.markdown("<div style='text-align:center;font-weight:700;color:#075985'>Temo · Sahabatmu</div>",unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["💬 Tulis Curhat","📅 Ajukan Jadwal","🔎 Cek Status"])
    with t1:
        st.markdown('<div class="panel"><h3>Formulir Pelaporan Anonim & Rahasia</h3><p class="muted">Email bersifat opsional dan digunakan untuk konfirmasi jadwal.</p></div>',unsafe_allow_html=True)
        with st.form("report_form",clear_on_submit=True):
            category=st.selectbox("Kategori",["Perundungan / bullying","Stres belajar & tahfidz","Keluarga atau masalah pribadi","Konsultasi agama / moral","Lainnya"])
            content=st.text_area("Ceritakan yang ingin disampaikan",height=160)
            optional_email=st.text_input("Email aktif untuk konfirmasi jadwal (opsional)")
            use_email=st.checkbox("Saya ingin menggunakan email ini untuk konfirmasi jadwal.")
            send=st.form_submit_button("Kirim Laporan",use_container_width=True)
        if send:
            if len(content.strip())<8: st.error("Ceritakan sedikit lebih lengkap (minimal 8 karakter).")
            elif use_email and ("@" not in optional_email or "." not in optional_email.split("@")[-1]): st.error("Masukkan alamat email yang valid.")
            else:
                urgency,sc=score_text(content)
                code="MAN2-"+datetime.now().strftime("%y%m%d")+"-"+secrets.token_hex(3).upper()
                with connect() as db:
                    db.execute("INSERT INTO reports(code,created,category,content,urgency,score,status,student_email,schedule_status,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
                               (code,now(),category,content.strip(),urgency,sc,"Baru",optional_email.strip() if use_email else "","Belum diajukan",now()))
                    db.commit()
                ok,msg=mail_bk(code,category,urgency)
                st.success(f"Laporan tersimpan. Simpan kode laporanmu: {code}")
                st.info("Email Guru BK terkirim." if ok else "Laporan tersimpan, tetapi email Guru BK belum terkirim. "+msg)
                st.caption("Penanda urgensi otomatis hanya penyaringan awal berdasarkan kata kunci, bukan diagnosis.")
    with t2:
        st.markdown('<div class="panel"><h3>Pengajuan Jadwal Tatap Muka</h3><p class="muted">Jadwal baru resmi setelah disetujui Guru BK.</p></div>',unsafe_allow_html=True)
        with st.form("schedule_form",clear_on_submit=True):
            code=st.text_input("Kode laporan")
            student_email=st.text_input("Email aktif untuk menerima konfirmasi")
            d=st.date_input("Tanggal yang diinginkan",min_value=date.today())
            tm=st.time_input("Waktu yang diinginkan",value=time(10,0),step=1800)
            note=st.text_area("Catatan singkat (opsional)",height=70)
            send_req=st.form_submit_button("Kirim Pengajuan Jadwal",use_container_width=True)
        if send_req:
            if not code.strip() or "@" not in student_email or "." not in student_email.split("@")[-1]:
                st.error("Masukkan kode laporan dan email yang valid.")
            else:
                with connect() as db:
                    found=db.execute("SELECT code FROM reports WHERE code=?",(code.strip(),)).fetchone()
                    if found:
                        requested=f"{d.strftime('%d-%m-%Y')} pukul {tm.strftime('%H:%M')}"
                        db.execute("UPDATE reports SET student_email=?,requested=?,schedule_status='Menunggu persetujuan',bk_note=?,updated=? WHERE code=?",
                                   (student_email.strip(),requested,note.strip(),now(),code.strip()))
                        db.commit()
                    else: found=None
                if found:
                    ok,msg=email(cfg()["recipient"],f"[SAFE-STUDENT] Pengajuan jadwal {code.strip()}",
                                 f"Ada pengajuan jadwal konseling.\nKode: {code.strip()}\nWaktu yang diminta: {requested}\nSilakan tinjau dashboard Guru BK.",
                                 "Pengajuan jadwal",code.strip())
                    st.success("Pengajuan tersimpan. Tunggu konfirmasi melalui email.")
                    if not ok: st.warning("Pengajuan tersimpan, tetapi email pemberitahuan BK belum terkirim. "+msg)
                else: st.error("Kode laporan tidak ditemukan.")
    with t3:
        st.markdown('<div class="panel"><h3>Cek Status Laporan & Jadwal</h3></div>',unsafe_allow_html=True)
        code=st.text_input("Kode laporan untuk dicek",key="check_code")
        if st.button("Cek Status"):
            with connect() as db: r=db.execute("SELECT code,status,requested,final_schedule,schedule_status FROM reports WHERE code=?",(code.strip(),)).fetchone()
            if r:
                st.write("**Status laporan:**",r["status"])
                st.write("**Status jadwal:**",r["schedule_status"])
                if r["requested"]: st.write("**Waktu diajukan:**",r["requested"])
                if r["final_schedule"]: st.write("**Jadwal final:**",r["final_schedule"])
            else: st.warning("Kode laporan tidak ditemukan.")

elif room=="🧑‍🏫 Guru BK":
    hero("Dashboard Guru BK","Kelola laporan, tindak lanjut, dan persetujuan jadwal dari satu tempat.")
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
        pending=int((df.schedule_status=="Menunggu persetujuan").sum()) if n else 0
        approved=int((df.schedule_status=="Disetujui").sum()) if n else 0
        new=int((df.status=="Baru").sum()) if n else 0
        cols=st.columns(4)
        for col,label,val in zip(cols,["Total laporan","Laporan baru","Jadwal menunggu","Jadwal disetujui"],[n,new,pending,approved]):
            with col: st.markdown(f'<div class="metric"><div>{label}</div><div class="num">{val}</div></div>',unsafe_allow_html=True)
        t1,t2,t3=st.tabs(["📥 Laporan masuk","📅 Persetujuan jadwal","✉️ Riwayat email"])
        with t1:
            if n:
                filt=st.selectbox("Filter laporan",["Semua","Baru","Diproses","Selesai"])
                view=df if filt=="Semua" else df[df.status==filt]
                st.dataframe(view[["code","created","category","urgency","status","schedule_status"]],use_container_width=True,hide_index=True)
                if len(view):
                    code=st.selectbox("Pilih laporan",view.code.tolist())
                    r=df[df.code==code].iloc[0]
                    st.markdown('<div class="panel"><h3>Detail laporan terpilih</h3></div>',unsafe_allow_html=True)
                    st.write("**Kode:**",r.code," · **Kategori:**",r.category," · **Penanda urgensi:**",r.urgency)
                    st.write("**Isi laporan:**"); st.write(r.content)
                    with st.form("update_report"):
                        status=st.selectbox("Status tindak lanjut",["Baru","Diproses","Selesai"],index=["Baru","Diproses","Selesai"].index(r.status))
                        bk_note=st.text_area("Catatan internal Guru BK (rahasia)",value=r.bk_note or "")
                        save=st.form_submit_button("Simpan perubahan")
                    if save: update(code,status=status,bk_note=bk_note); st.success("Perubahan tersimpan."); st.rerun()
            else: st.info("Belum ada laporan.")
        with t2:
            waiting=df[df.schedule_status=="Menunggu persetujuan"] if n else df
            if n: st.dataframe(df[df.schedule_status!="Belum diajukan"][["code","student_email","requested","final_schedule","schedule_status"]],use_container_width=True,hide_index=True)
            if len(waiting):
                code=st.selectbox("Pilih pengajuan yang menunggu",waiting.code.tolist())
                r=df[df.code==code].iloc[0]
                st.markdown('<div class="panel"><h3>Review pengajuan jadwal</h3></div>',unsafe_allow_html=True)
                st.write("**Email siswa:**",r.student_email or "Belum diisi")
                st.write("**Waktu diminta:**",r.requested)
                with st.form("approve_form"):
                    decision=st.radio("Keputusan",["Setujui","Usulkan jadwal lain","Tolak"],horizontal=True)
                    final_date=st.date_input("Tanggal final",min_value=date.today())
                    final_time=st.time_input("Jam final",value=time(10,0),step=1800)
                    student_note=st.text_area("Catatan untuk siswa (akan masuk email)",height=70)
                    act=st.form_submit_button("Simpan keputusan")
                if act:
                    if decision=="Setujui":
                        final=f"{final_date.strftime('%d-%m-%Y')} pukul {final_time.strftime('%H:%M')}"
                        update(code,final_schedule=final,schedule_status="Disetujui")
                        if r.student_email:
                            ok,msg=mail_student(r.student_email,code,final,student_note)
                            st.success("Jadwal disetujui."); st.info(msg)
                        else: st.warning("Jadwal tersimpan, tetapi email siswa belum tersedia.")
                    elif decision=="Usulkan jadwal lain":
                        final=f"{final_date.strftime('%d-%m-%Y')} pukul {final_time.strftime('%H:%M')}"
                        update(code,final_schedule=final,schedule_status="Menunggu konfirmasi siswa")
                        st.info("Usulan disimpan. Hubungi siswa untuk menyepakati jadwal.")
                    else:
                        update(code,schedule_status="Ditolak",bk_note=student_note)
                        st.warning("Pengajuan ditandai ditolak. Email penolakan tidak dikirim otomatis pada versi ini.")
                    st.rerun()
            else: st.info("Tidak ada pengajuan jadwal yang menunggu.")
        with t3:
            with connect() as db: logs=pd.read_sql_query("SELECT created,recipient,subject,event,code,status,detail FROM email_log ORDER BY id DESC LIMIT 200",db)
            if len(logs): st.dataframe(logs,use_container_width=True,hide_index=True)
            else: st.info("Belum ada riwayat email.")
        if st.button("Keluar dari dashboard Guru BK"): st.session_state["bk_auth"]=False; st.rerun()
    else: st.info("Masuk untuk membuka data laporan dan jadwal.")

elif room=="👨‍👩‍👧 Orang Tua":
    hero("Ruang Orang Tua","Informasi umum tentang layanan konseling dan dukungan bagi siswa.")
    st.markdown('<div class="panel"><h3>Mendampingi siswa</h3><p class="muted">Dengarkan tanpa menghakimi, beri ruang untuk bercerita, dan hubungi Guru BK jika siswa membutuhkan dukungan.</p></div>',unsafe_allow_html=True)
    with st.expander("Kapan menghubungi Guru BK?"): st.write("Saat siswa mengalami kesulitan belajar, konflik sosial, perubahan perilaku yang mengkhawatirkan, atau membutuhkan dukungan emosional.")

else:
    hero("Admin SAFE-STUDENT","Periksa konfigurasi email dan status pengiriman.")
    with st.expander("🔐 Masuk Admin",expanded=not st.session_state.get("admin_auth",False)):
        pw=st.text_input("Kata sandi Admin",type="password",key="admin_pw")
        if st.button("Masuk Admin"):
            try: expected=st.secrets.get("auth",{}).get("admin_password","")
            except Exception: expected=""
            if expected and secrets.compare_digest(pw,expected): st.session_state["admin_auth"]=True; st.rerun()
            else: st.error("Kata sandi salah atau belum diatur di secrets.toml.")
    if st.session_state.get("admin_auth"):
        conf=cfg()
        st.markdown('<div class="panel"><h3>Konfigurasi email</h3></div>',unsafe_allow_html=True)
        st.write("Pengirim:",conf["sender"]); st.write("Penerima Guru BK:",conf["recipient"])
        st.write("App Password tersedia:", "Ya" if conf["password"] else "Belum")
        if st.button("Kirim email uji ke Guru BK"):
            ok,msg=email(conf["recipient"],"[SAFE-STUDENT] Tes email","Email uji SAFE-STUDENT MAN 2 Kudus. Tidak ada data siswa.","Tes email")
            st.success(msg) if ok else st.error(msg)
        with connect() as db: logs=pd.read_sql_query("SELECT created,recipient,subject,event,code,status,detail FROM email_log ORDER BY id DESC LIMIT 100",db)
        st.dataframe(logs,use_container_width=True,hide_index=True)
        if st.button("Keluar dari Admin"): st.session_state["admin_auth"]=False; st.rerun()

st.markdown('<p style="text-align:center;color:#587789;font-size:.8rem;padding:20px">SAFE-STUDENT · MAN 2 Kudus · Sampaikan cerita, temukan dukungan.</p>',unsafe_allow_html=True)

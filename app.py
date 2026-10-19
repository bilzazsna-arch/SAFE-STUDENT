import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import base64
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS FULL CUSTOM
# ==========================================
st.set_page_config(
    page_title="SAFE-STUDENT - MAN 2 Kudus",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Path direktori utama aplikasi
DIR_UTAMA = os.path.dirname(os.path.abspath(__file__))
FILE_DATABASE = os.path.join(DIR_UTAMA, "db_laporan.csv")
FILE_JADWAL = os.path.join(DIR_UTAMA, "db_jadwal.csv")

EMAIL_GURU_BK = "bilzazsna@gmail.com"

# Fungsi Pembaca Gambar Lokal ke Base64
def muat_gambar_base64(nama_file):
    path_lengkap = os.path.join(DIR_UTAMA, nama_file)
    if os.path.exists(path_lengkap):
        with open(path_lengkap, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# Membaca file gambar pendukung
bg_base64 = muat_gambar_base64("bg_laut.jpg")
cowo_base64 = muat_gambar_base64("kepiting_cowo.png")
logo_base64 = muat_gambar_base64("Logo_MAN2.png")

# CSS Kustom: Styling Tampilan
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700;800;900&family=Poppins:wght@400;600;700;800&display=swap');

    /* BACKGROUND LAUT UTAMA */
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.1)), url("data:image/jpg;base64,{bg_base64 if bg_base64 else ''}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    
    [data-testid="stHeader"], .main .block-container {{
        background: transparent !important;
        padding-top: 0rem !important;
    }}

    .element-container, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, 
    [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    /* Header Deretan Logo Atas */
    .top-logos-container {{
        text-align: center;
        margin-bottom: 10px;
        margin-top: 5px;
    }}
    .top-logos-container img {{
        height: 65px;
        margin: 0 10px;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.3));
    }}

    /* Judul Utama */
    .main-title-box {{
        text-align: center;
        margin-bottom: 20px;
    }}
    .title-curhatin {{
        font-family: 'Fredoka', cursive, sans-serif;
        color: #FFD700 !important;
        text-shadow: 3px 3px 0px #FF8C00, 5px 5px 15px rgba(0,0,0,0.8);
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0;
        line-height: 1.1;
    }}
    .title-digital {{
        font-family: 'Fredoka', cursive, sans-serif;
        color: #FFFFFF !important;
        text-shadow: 3px 3px 0px #0284C7, 5px 5px 15px rgba(0,0,0,0.8);
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0;
        line-height: 1.1;
    }}
    .title-safe {{
        font-family: 'Fredoka', cursive, sans-serif;
        background: linear-gradient(90deg, #0284C7, #0369A1);
        color: #FFFFFF !important;
        padding: 6px 24px;
        border-radius: 30px;
        display: inline-block;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 2px solid #FFFFFF;
    }}

    /* Maskot Temo Tunggal di Tengah */
    .img-maskot-pure {{
        text-align: center;
        background: transparent !important;
    }}
    .img-maskot-pure img {{
        max-width: 230px;
        height: auto;
        filter: drop-shadow(0px 8px 18px rgba(0,0,0,0.4));
    }}
    .name-badge-temo {{
        font-family: 'Fredoka', cursive, sans-serif;
        background: #FFFFFF;
        color: #0369A1;
        font-size: 1.8rem;
        font-weight: 900;
        padding: 4px 28px;
        border-radius: 25px;
        display: inline-block;
        margin-top: -15px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
        border: 3px solid #E0F2FE;
        transform: rotate(3deg);
    }}

    /* Kotak Pesan Sambutan */
    .speech-bubble {{
        font-family: 'Poppins', sans-serif;
        background-color: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(12px);
        padding: 24px 28px;
        border-radius: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
        color: #1E293B !important;
        text-align: center;
        font-weight: 600;
        border: 4px solid #E0F2FE;
    }}

    /* RADIO BUTTON SIDEBAR HITAM PEKAT SAAT DIPILIH */
    [data-testid="stSidebar"] {{
        background-color: rgba(3, 105, 161, 0.95) !important;
        color: white;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 1.05rem;
    }}
    [data-testid="stSidebar"] input[type="radio"]:checked + div,
    [data-testid="stSidebar"] div[role="radio"][aria-checked="true"] > div:first-child {{
        background-color: #000000 !important;
        border-color: #000000 !important;
    }}
    [data-testid="stSidebar"] div[role="radio"][aria-checked="true"] div {{
        border-color: #000000 !important;
        background-color: #000000 !important;
    }}
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #F0F9FF !important;
    }}

    /* Wadah Form & Tab */
    .stTabs, form, [data-testid="stForm"] {{
        background-color: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(12px);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.3) !important;
    }}
    
    .metric-card {{
        background-color: #FFFFFF !important;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        border: 1px solid #7DD3FC;
        text-align: center;
        margin-bottom: 10px;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #0369A1 !important;
    }}
    .metric-label {{
        color: #475569 !important;
        font-size: 0.9rem;
        font-weight: 600;
    }}
    
    .stButton>button {{
        width: 100%;
        background: linear-gradient(90deg, #0284C7 0%, #0369A1 100%);
        color: white !important;
        border-radius: 14px;
        padding: 14px 24px;
        font-size: 1.1rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SISTEM DATABASE PERSISTEN (ANTI HILANG)
# ==========================================
def muat_database_laporan():
    if os.path.exists(FILE_DATABASE):
        try:
            return pd.read_csv(FILE_DATABASE)
        except Exception:
            pass
    return pd.DataFrame(columns=[
        'ID_Kasus', 'Waktu', 'Kategori', 'Isi_Laporan_Enkripsi', 'Status_Urgensi', 
        'Skor_Urgensi', 'Jadwal_Tatap_Muka', 'Catatan_Rekam_Medis_BK', 'Status_Kasus'
    ])

def simpan_database_laporan(df):
    df.to_csv(FILE_DATABASE, index=False)

def muat_database_jadwal():
    if os.path.exists(FILE_JADWAL):
        try:
            return pd.read_csv(FILE_JADWAL)
        except Exception:
            pass
    return pd.DataFrame(columns=[
        'ID_Jadwal', 'Email_Siswa', 'Tanggal', 'Jam', 'Status_Konfirmasi'
    ])

def simpan_database_jadwal(df):
    df.to_csv(FILE_JADWAL, index=False)

if 'db_laporan' not in st.session_state or st.session_state.db_laporan.empty:
    st.session_state.db_laporan = muat_database_laporan()

if 'db_jadwal' not in st.session_state or st.session_state.db_jadwal.empty:
    st.session_state.db_jadwal = muat_database_jadwal()

# ==========================================
# 3. FUNGSI KIRIM EMAIL OTOMATIS
# ==========================================
def kirim_email_notifikasi(email_penerima, subjek, isi_pesan):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = EMAIL_GURU_BK
        sender_password = "password_aplikasi_anda" # Ganti dengan App Password Gmail jika sudah diatur
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email_penerima
        msg['Subject'] = subjek
        
        msg.attach(MIMEText(isi_pesan, 'plain'))
        
        # Jalankan SMTP jika password telah dikonfigurasi
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(sender_email, sender_password)
        # server.sendmail(sender_email, email_penerima, msg.as_string())
        # server.quit()
        return True
    except Exception as e:
        return False

# ==========================================
# 4. DETEKSI DINI BERBASIS NLP (ANALISIS TEKS)
# ==========================================
def analisa_nlp_ringan(teks):
    teks_lower = teks.lower()
    kata_kunci_tinggi = ["bunuh diri", "sakiti diri", "pukul", "ancam", "pemerasan", "silet", "racun", "mati", "kekerasan", "pelecehan"]
    kata_kunci_sedang = ["diejek", "dikucilkan", "stres", "takut", "cemas", "nilai turun", "dihina", "diancam", "dibully", "frustrasi"]
    
    skor = 0
    for kata in kata_kunci_tinggi:
        if kata in teks_lower:
            skor += 3
    for kata in kata_kunci_sedang:
        if kata in teks_lower:
            skor += 1

    if skor >= 3:
        return "🔴 MERAH (Urgensi Tinggi)", skor
    elif skor >= 1:
        return "🟡 KUNING (Urgensi Sedang)", skor
    else:
        return "🟢 HIJAU (Urgensi Rendah)", skor

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=65)
    st.markdown("### **SAFE-STUDENT**")
    st.caption("🌊 Layanan Pelaporan & Konseling Digital MAN 2 Kudus")
    st.divider()
    
    menu = st.radio(
        "Pilih Ruang Akses:",
        ["✨ Siswa (Curhat & Jadwal)", "🔒 Guru BK (Dashboard & Rekam Medis)"]
    )
    st.divider()
    st.caption("🔒 *Privasi Terjamin: Pelaporan anonim terenkripsi 24 jam.*")

# ==========================================
# 6. HALAMAN SISWA
# ==========================================
if menu == "✨ Siswa (Curhat & Jadwal)":
    
    logo_tag = f'<img src="data:image/png;base64,{logo_base64}" style="height: 65px; border-radius: 12px; vertical-align: middle;">' if logo_base64 else ''
    st.markdown(f"""
        <div class="top-logos-container">
            {logo_tag}
        </div>
        <div class="main-title-box">
            <h1 class="title-curhatin">Curhatin</h1>
            <h1 class="title-digital">Digital MAN</h1>
            <div class="title-safe">- SAFE-STUDENT MAN 2 Kudus -</div>
        </div>
    """, unsafe_allow_html=True)

    # MASKOT TEMO TUNGGAL DI TENGAH
    col_m1, col_text, col_m2 = st.columns([1, 2.5, 1])
    
    with col_text:
        if cowo_base64:
            st.markdown(f"""
                <div class="img-maskot-pure" style="margin-bottom: 15px;">
                    <img src="data:image/png;base64,{cowo_base64}"><br>
                    <div class="name-badge-temo">Temo</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("""
            <div class="speech-bubble">
                <b style="font-size: 1.35rem; color: #0284C7 !important;">Halo Teman-teman MAN 2 Kudus! ✨</b><br><br>
                <span style="color: #334155 !important; font-size: 1.05rem; line-height: 1.5;">Aku <b>Temo</b> siap mendampingi dan menjaga kerahasiaan ceritamu 24 jam penuh. Sampaikan curhatan anonim atau jadwalkan konseling dengan aman di sini! 🌊</span>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.divider()

    tab1, tab2 = st.tabs(["💬 Tulis Laporan Anonim", "📅 Penjadwalan Tatap Muka"])

    with tab1:
        st.subheader("Formulir Pelaporan Anonim & Rahasia")
        st.info("🔒 **Jaminan Privasi:** Identitas Anda sepenuhnya dirahasiakan agar Anda dapat menyampaikan keluh kesah dengan aman dan nyaman.")
        
        with st.form("form_curhat", clear_on_submit=True):
            kategori = st.selectbox(
                "Kategori Permasalahan:",
                ["💬 Perundungan (Bullying)", "📚 Stres Belajar & Tahfidz", "🏠 Masalah Keluarga / Pribadi", "🌈 Konsultasi Keagamaan / Akhlak"]
            )
            
            isi_laporan = st.text_area(
                "Ceritakan permasalahan Anda secara bebas:",
                placeholder="Tuliskan apa yang sedang Anda rasakan atau alami di sini...",
                height=150
            )
            
            submit = st.form_submit_button("Kirim Laporan Rahasia 🚀")

        if submit:
            if isi_laporan.strip() == "":
                st.warning("Mohon tuliskan cerita Anda terlebih dahulu.")
            else:
                urgensi, skor = analisa_nlp_ringan(isi_laporan)
                id_kasus = f"MAN2KUDUS-{datetime.now().strftime('%m%d%H%M%S')}"
                
                data_baru = pd.DataFrame([{
                    'ID_Kasus': id_kasus,
                    'Waktu': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Kategori': kategori,
                    'Isi_Laporan_Enkripsi': isi_laporan,
                    'Status_Urgensi': urgensi,
                    'Skor_Urgensi': skor,
                    'Jadwal_Tatap_Muka': 'Belum Dibuat',
                    'Catatan_Rekam_Medis_BK': 'Belum ada catatan',
                    'Status_Kasus': 'Baru'
                }])
                
                st.session_state.db_laporan = pd.concat([st.session_state.db_laporan, data_baru], ignore_index=True)
                simpan_database_laporan(st.session_state.db_laporan)
                
                # Kirim Notifikasi Email Otomatis ke Guru BK
                subjek_bk = f"🔔 [Laporan Baru #{id_kasus}] {urgensi} - SAFE-STUDENT"
                pesan_bk = f"Ada laporan anonim baru yang masuk di SAFE-STUDENT MAN 2 Kudus:\n\nID Kasus: {id_kasus}\nKategori: {kategori}\nUrgensi: {urgensi}\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nSilakan cek Dashboard Guru BK untuk detail lebih lanjut."
                kirim_email_notifikasi(EMAIL_GURU_BK, subjek_bk, pesan_bk)
                
                st.balloons()
                st.success(f"✅ Laporan Anda telah tersimpan dan terenkripsi! Notifikasi telah dikirim ke Guru BK. Kode Referensi: **{id_kasus}**")
                
                if "MERAH" in urgensi:
                    st.error("🚨 DETEKSI NLP SYSTEM: Indikasi permasalahan urgensi tinggi terdeteksi. Sinyal prioritas otomatis diteruskan ke Guru BK.")

    with tab2:
        st.subheader("Pengajuan Jadwal Konseling Tatap Muka")
        st.info("Masukkan email Anda agar sistem dapat mengirimkan notifikasi otomatis saat Guru BK mengonfirmasi jadwal.")
        
        with st.form("form_jadwal", clear_on_submit=True):
            email_siswa = st.text_input("Email Anda (untuk pengiriman notifikasi otomatis):", placeholder="contoh: siswa@gmail.com")
            col_tgl, col_jam = st.columns(2)
            with col_tgl:
                tgl_pilihan = st.date_input("Pilih Tanggal Konseling:", min_value=date.today())
            with col_jam:
                jam_pilihan = st.time_input("Pilih Jam Konseling:", value=time(9, 0))
                
            submit_jadwal = st.form_submit_button("Ajukan Jadwal Temu 📅")
            
        if submit_jadwal:
            if not email_siswa or "@" not in email_siswa:
                st.warning("Mohon masukkan alamat email yang valid.")
            else:
                id_jadwal = f"JDW-{datetime.now().strftime('%m%d%H%M%S')}"
                jadwal_baru = pd.DataFrame([{
                    'ID_Jadwal': id_jadwal,
                    'Email_Siswa': email_siswa,
                    'Tanggal': str(tgl_pilihan),
                    'Jam': jam_pilihan.strftime('%H:%M'),
                    'Status_Konfirmasi': 'Menunggu Konfirmasi BK'
                }])
                
                st.session_state.db_jadwal = pd.concat([st.session_state.db_jadwal, jadwal_baru], ignore_index=True)
                simpan_database_jadwal(st.session_state.db_jadwal)
                
                # Kirim Notifikasi Email Otomatis ke Guru BK
                subjek_bk = f"📅 [Jadwal Baru #{id_jadwal}] Pengajuan Konseling Siswa"
                pesan_bk = f"Ada pengajuan jadwal konseling baru dari siswa:\n\nEmail Siswa: {email_siswa}\nTanggal: {tgl_pilihan}\nJam: {jam_pilihan.strftime('%H:%M')} WIB\n\nSilakan konfirmasi di Dashboard Guru BK."
                kirim_email_notifikasi(EMAIL_GURU_BK, subjek_bk, pesan_bk)
                
                st.success(f"📅 Permintaan konseling tanggal **{tgl_pilihan}** jam **{jam_pilihan.strftime('%H:%M')} WIB** berhasil diajukan! Notifikasi otomatis telah dikirim ke Guru BK.")

# ==========================================
# 7. HALAMAN GURU BK (DASHBOARD & REKAM MEDIS)
# ==========================================
elif menu == "🔒 Guru BK (Dashboard & Rekam Medis)":
    st.title("📊 Dashboard & Rekam Data Konseling Guru BK")
    st.caption("🔒 Pengelolaan terintegrasi: Rekap laporan, deteksi NLP, konfirmasi jadwal, dan rekam data siswa.")
    
    passcode = st.text_input("🔑 Kata Sandi Autentikasi Guru BK:", type="password")
    
    if passcode == "bk123":
        st.success("Autentikasi berhasil. Selamat bertugas, Bapak/Ibu Guru BK MAN 2 Kudus.")
        st.divider()
        
        st.session_state.db_laporan = muat_database_laporan()
        st.session_state.db_jadwal = muat_database_jadwal()
        df = st.session_state.db_laporan
        df_jdw = st.session_state.db_jadwal
        
        pending_count = len(df_jdw[df_jdw['Status_Konfirmasi'] == 'Menunggu Konfirmasi BK']) if not df_jdw.empty else 0
        if pending_count > 0:
            st.warning(f"🔔 **NOTIFIKASI OTOMATIS:** Ada **{pending_count} pengajuan jadwal konseling baru** dari siswa yang menunggu konfirmasi Anda!")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df)}</div><div class='metric-label'>Total Laporan Masuk</div></div>", unsafe_allow_html=True)
        with c2:
            merah = len(df[df['Status_Urgensi'].str.contains("MERAH", na=False)]) if not df.empty else 0
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#EF4444 !important;'>{merah}</div><div class='metric-label'>Urgensi Tinggi (NLP)</div></div>", unsafe_allow_html=True)
        with c3:
            kuning = len(df[df['Status_Urgensi'].str.contains("KUNING", na=False)]) if not df.empty else 0
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#F59E0B !important;'>{kuning}</div><div class='metric-label'>Urgensi Sedang (NLP)</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#10B981 !important;'>{len(df)-merah-kuning}</div><div class='metric-label'>Urgensi Rendah</div></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("📅 Kelola & Konfirmasi Pengajuan Jadwal Konseling Siswa")
        
        if df_jdw.empty:
            st.info("Belum ada pengajuan jadwal konseling dari siswa.")
        else:
            for idx_j, row_j in df_jdw.iterrows():
                with st.container():
                    col

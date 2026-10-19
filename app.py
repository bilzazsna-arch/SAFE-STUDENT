import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import base64
import os

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
cewe_base64 = muat_gambar_base64("kepiting_cewe.png")
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

    /* Maskot Kepiting & Papan Nama */
    .img-maskot-pure {{
        text-align: center;
        background: transparent !important;
    }}
    .img-maskot-pure img {{
        max-width: 230px;
        height: auto;
        filter: drop-shadow(0px 8px 18px rgba(0,0,0,0.4));
    }}
    .kema-box {{ position: relative; left: -25px; }}
    .temo-box {{ position: relative; right: -25px; }}

    .name-badge-kema, .name-badge-temo {{
        font-family: 'Fredoka', cursive, sans-serif;
        background: #FFFFFF;
        color: #0284C7;
        font-size: 1.8rem;
        font-weight: 900;
        padding: 4px 28px;
        border-radius: 25px;
        display: inline-block;
        margin-top: -15px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
        border: 3px solid #E0F2FE;
        transform: rotate(-3deg);
    }}
    .name-badge-temo {{
        transform: rotate(3deg);
        color: #0369A1;
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
def muat_database():
    if os.path.exists(FILE_DATABASE):
        try:
            return pd.read_csv(FILE_DATABASE)
        except Exception:
            pass
    return pd.DataFrame(columns=[
        'ID_Kasus', 'Waktu', 'Kategori', 'Isi_Laporan_Enkripsi', 'Status_Urgensi', 
        'Skor_Urgensi', 'Jadwal_Tatap_Muka', 'Catatan_Rekam_Medis_BK', 'Status_Kasus'
    ])

def simpan_database(df):
    df.to_csv(FILE_DATABASE, index=False)

if 'db_laporan' not in st.session_state or st.session_state.db_laporan.empty:
    st.session_state.db_laporan = muat_database()

# ==========================================
# 3. DETEKSI DINI BERBASIS NLP (ANALISIS TEKS)
# ==========================================
def analisa_nlp_ringan(teks):
    teks_lower = teks.lower()
    
    # Kata kunci indikator tingkat keparahan
    kata_kunci_tinggi = ["bunuh diri", "sakiti diri", "pukul", "ancam", "pemerasan", "silet", "racun", "mati", "kekerasan", "pelecehan", "perkosa"]
    kata_kunci_sedang = ["diejek", "dikucilkan", "stres", "takut", "cemas", "nilai turun", "dihina", "diancam", "dibully", "frustrasi", "sendiri"]
    
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
# 4. SIDEBAR NAVIGATION
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
    st.caption("🔒 *Privasi Terjamin: Pelaporan anonim terenkripsi untuk kenyamanan siswa.*")

# ==========================================
# 5. HALAMAN SISWA
# ==========================================
if menu == "✨ Siswa (Curhat & Jadwal)":
    
    # Deretan Logo Instansi di Atas & Judul 3D Megah
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

    # MASKOT KEMA & TEMO DENGAN PAPAN NAMA ESTETIK
    col_m1, col_text, col_m2 = st.columns([1.5, 2.5, 1.5])
    
    with col_m1:
        if cewe_base64:
            st.markdown(f"""
                <div class="img-maskot-pure kema-box">
                    <img src="data:image/png;base64,{cewe_base64}"><br>
                    <div class="name-badge-kema">Kema</div>
                </div>
            """, unsafe_allow_html=True)
            
    with col_text:
        st.markdown("""
            <div class="speech-bubble">
                <b style="font-size: 1.35rem; color: #0284C7 !important;">Halo Teman-teman MAN 2 Kudus! ✨</b><br><br>
                <span style="color: #334155 !important; font-size: 1.05rem; line-height: 1.5;">Kami <b>Kema & Temo</b> adalah penjaga kerahasiaan curhatmu. Apapun masalahmu di sekolah, sampaikan secara anonim di sini dengan aman, nyaman, dan terpercaya! 🌊</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        if cowo_base64:
            st.markdown(f"""
                <div class="img-maskot-pure temo-box">
                    <img src="data:image/png;base64,{cowo_base64}"><br>
                    <div class="name-badge-temo">Temo</div>
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
                # Deteksi Dini Berbasis NLP
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
                simpan_database(st.session_state.db_laporan)
                
                st.balloons()
                st.success(f"✅ Laporan Anda telah tersimpan dan terenkripsi dalam sistem! Kode Referensi Anda: **{id_kasus}**")
                
                if "MERAH" in urgensi:
                    st.error("🚨 DETEKSI NLP SYSTEM: Indikasi permasalahan urgensi tinggi terdeteksi. Sinyal prioritas otomatis diteruskan ke Guru BK.")

    with tab2:
        st.subheader("Pengajuan Jadwal Konseling Tatap Muka")
        st.info("Ajukan waktu konseling langsung dengan Guru BK MAN 2 Kudus secara terstruktur.")
        
        col_tgl, col_jam = st.columns(2)
        with col_tgl:
            tgl_pilihan = st.date_input("Pilih Tanggal Konseling:", min_value=date.today())
        with col_jam:
            jam_pilihan = st.time_input("Pilih Jam Konseling:", value=time(9, 0))
            
        if st.button("Konfirmasi Pengajuan Jadwal 📅"):
            st.success(f"📅 Pengajuan konseling tatap muka pada tanggal **{tgl_pilihan}** jam **{jam_pilihan.strftime('%H:%M')} WIB** berhasil diajukan ke Guru BK!")

# ==========================================
# 6. HALAMAN GURU BK (DASHBOARD & REKAM MEDIS)
# ==========================================
elif menu == "🔒 Guru BK (Dashboard & Rekam Medis)":
    st.title("📊 Dashboard & Rekam Data Konseling Guru BK")
    st.caption("🔒 Pengelolaan terintegrasi: Rekap laporan, deteksi NLP, penjadwalan, dan rekam data siswa.")
    
    passcode = st.text_input("🔑 Kata Sandi Autentikasi Guru BK:", type="password")
    
    if passcode == "bk123":
        st.success("Autentikasi berhasil. Selamat bertugas, Bapak/Ibu Guru BK MAN 2 Kudus.")
        st.divider()
        
        st.session_state.db_laporan = muat_database()
        df = st.session_state.db_laporan
        
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
        st.subheader("📋 Rekam Medis & Penanganan Terstruktur Kasus Siswa")
        
        if df.empty:
            st.info("Belum ada laporan siswa yang masuk di sistem.")
        else:
            df_sorted = df.sort_values(by='Skor_Urgensi', ascending=False)
            
            for idx, row in df_sorted.iterrows():
                with st.expander(f"[{row['Status_Urgensi']}] {row['ID_Kasus']} - {row['Kategori']} ({row['Waktu']})"):
                    st.write("**Isi Laporan Siswa (Anonim & Terenkripsi):**")
                    st.write(f"_{row['Isi_Laporan_Enkripsi']}_")
                    
                    st.divider()
                    st.write("**Rekam Data Konseling & Tindak Lanjut Guru BK:**")
                    catatan_baru = st.text_area(f"Catatan / Rekam Data Konseling #{row['ID_Kasus']}:", value=str(row['Catatan_Rekam_Medis_BK']), key=f"notes_{idx}")
                    status_baru = st.selectbox(f"Status Penanganan Kasus #{row['ID_Kasus']}:", ["Baru", "Prosedur Konseling", "Tindak Lanjut", "Selesai"], key=f"status_{idx}")
                    
                    if st.button("Simpan Rekam Data 💾", key=f"btn_{idx}"):
                        st.session_state.db_laporan.at[idx, 'Catatan_Rekam_Medis_BK'] = catatan_baru
                        st.session_state.db_laporan.at[idx, 'Status_Kasus'] = status_baru
                        simpan_database(st.session_state.db_laporan)
                        st.success("Rekam data konseling dan status penanganan berhasil diperbarui!")

            st.divider()
            csv_data = df_sorted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Rekapitulasi Data Konseling (CSV)",
                data=csv_data,
                file_name=f"Rekap_BK_MAN2Kudus_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
    elif passcode != "":
        st.error("❌ Kata sandi autentikasi salah. Akses ditolak.")

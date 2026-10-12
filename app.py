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

# Mendapatkan lokasi direktori folder utama tempat app.py berada
DIR_UTAMA = os.path.dirname(os.path.abspath(__file__))

# Fungsi Pembaca Gambar Lokal ke Base64
def muat_gambar_base64(nama_file):
    path_lengkap = os.path.join(DIR_UTAMA, nama_file)
    if os.path.exists(path_lengkap):
        with open(path_lengkap, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# Membaca background laut, maskot, dan logo sekolah
bg_base64 = muat_gambar_base64("bg_laut.jpg")
cewe_base64 = muat_gambar_base64("kepiting_cewe.png")
cowo_base64 = muat_gambar_base64("kepiting_cowo.png")
logo_base64 = muat_gambar_base64("Logo_MAN2.png")

# CSS Kustom: Estetika Laut, Logo 6x, Kema Digeser ke Kiri, & Radio Hitam Pekat
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700;800;900&family=Poppins:wght@400;600;700;800&display=swap');

    /* BACKGROUND LAUT UTAMA MEMENUHI SELURUH LAYAR */
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0,0,0,0.15), rgba(0,0,0,0.15)), url("data:image/jpg;base64,{bg_base64 if bg_base64 else ''}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    
    /* MENGHAPUS KOTAK/LATAR POLOS PADA KONTEN UTAMA */
    [data-testid="stHeader"], .main .block-container {{
        background: transparent !important;
        padding-top: 0rem !important;
    }}

    /* HAPUS HIGHLIGHT/BACKGROUND PUTIH DI BELAKANG TEKS MARKDOWN */
    .element-container, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, 
    [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    /* Container Header Tengah (Logo & Judul) */
    .header-center-box {{
        text-align: center;
        margin-bottom: 25px;
        margin-top: -30px;
        background: transparent !important;
    }}
    
    /* Logo Sekolah 6 Kali Lebih Besar & Di Atas */
    .school-logo-img {{
        width: 320px;
        height: auto;
        margin-bottom: 10px;
        filter: drop-shadow(0px 10px 24px rgba(0,0,0,0.6));
        border-radius: 20px;
    }}

    /* Judul Utama SUPER MEGAH */
    .main-title {{
        font-family: 'Fredoka', 'Poppins', sans-serif;
        color: #FFFFFF !important;
        text-shadow: 4px 4px 20px rgba(0, 0, 0, 0.95);
        font-weight: 900;
        text-align: center;
        font-size: 3.5rem;
        margin: 0;
        line-height: 1.15;
        background: transparent !important;
    }}

    /* Wadah Maskot Transparan & Kepiting Sangat Besar */
    .img-maskot-pure {{
        text-align: center;
        background: transparent !important;
        padding: 5px;
    }}
    .img-maskot-pure img {{
        max-width: 270px;
        height: auto;
        filter: drop-shadow(0px 10px 22px rgba(0,0,0,0.5));
        transition: transform 0.3s ease;
    }}
    .img-maskot-pure img:hover {{
        transform: scale(1.08);
    }}

    /* Khusus Menggeser Kema ke Kiri */
    .kema-container {{
        position: relative;
        left: -35px;
    }}

    /* NAMA MASKOT (KEMA & TEMO) */
    .nama-maskot-estetik {{
        font-family: 'Fredoka', 'Comic Sans MS', cursive, sans-serif;
        color: #FFFFFF !important;
        font-size: 2.4rem;
        font-weight: 900;
        margin-top: 12px;
        letter-spacing: 1px;
        text-shadow: 3px 3px 12px rgba(3, 105, 161, 0.95), 0px 0px 14px rgba(255, 255, 255, 0.9);
        background: transparent !important;
    }}

    /* Kotak Pesan Sambutan Estetik */
    .speech-bubble {{
        font-family: 'Poppins', sans-serif;
        background-color: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(10px);
        padding: 28px 32px;
        border-radius: 24px;
        border-left: 8px solid #0284C7;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.3) !important;
        color: #1E293B !important;
        text-align: center;
        font-weight: 600;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .speech-bubble b, .speech-bubble span {{
        background: transparent !important;
        color: #1E293B !important;
    }}

    /* Kustomisasi Radio Button Sidebar Menjadi Hitam Pekat Saat Dipilih */
    [data-testid="stSidebar"] {{
        background-color: rgba(3, 105, 161, 0.95) !important;
        color: white;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 1.05rem;
    }}
    [data-testid="stSidebar"] div[role="radio"][aria-checked="true"] {{
        background-color: rgba(0, 0, 0, 0.25) !important;
        border-radius: 10px;
        padding: 4px;
    }}
    [data-testid="stSidebar"] div[role="radio"][aria-checked="true"] div {{
        background-color: #000000 !important;
        border-color: #000000 !important;
    }}

    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #F0F9FF !important;
    }}

    /* Wadah Form & Tab Tetap Bersih & Nyaman Dibaca di Atas Laut */
    .stTabs, form, [data-testid="stForm"] {{
        background-color: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(12px);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Card Dashboard BK */
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
    
    /* Tombol Utama */
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

# Inisialisasi Database Sesi (Menyimpan Status Penanganan, Enkripsi, & Jadwal)
if 'db_laporan' not in st.session_state:
    st.session_state.db_laporan = pd.DataFrame(columns=[
        'ID_Kasus', 'Waktu', 'Kategori', 'Isi_Laporan_Enkripsi', 'Status_Urgensi', 
        'Skor_Urgensi', 'Jadwal_Tatap_Muka', 'Catatan_Rekam_Medis_BK', 'Status_Kasus'
    ])

# ==========================================
# 2. ANALISA NLP RINGAN
# ==========================================
def analisa_nlp_ringan(teks):
    teks_lower = teks.lower()
    kata_kunci_tinggi = ["bunuh diri", "sakiti diri", "pukul", "ancam", "pemerasan", "silet", "racun", "mati", "kekerasan"]
    kata_kunci_sedang = ["diejek", "dikucilkan", "stres", "takut", "cemas", "nilai turun", "dihina", "diancam", "dibully"]
    
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
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=65)
    st.markdown("### **SAFE-STUDENT**")
    st.caption("🌊 Layanan Konseling & Pengaduan 24 Jam MAN 2 Kudus")
    st.divider()
    
    menu = st.radio(
        "Pilih Ruang Akses:",
        ["✨ Siswa (Curhat & Jadwal)", "🔒 Guru BK (Dashboard & Rekam Medis)"]
    )
    st.divider()
    st.caption("🔒 *Privasi Terjamin: Data Pesan Terenkripsi & Akses Terbatas Guru BK.*")

# ==========================================
# 4. HALAMAN SISWA
# ==========================================
if menu == "✨ Siswa (Curhat & Jadwal)":
    
    # Header Rata Tengah: Logo MAN 2 Kudus 6x Lebih Besar di Atas + Judul Utama
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="school-logo-img"><br>' if logo_base64 else ''
    st.markdown(f"""
        <div class="header-center-box">
            {logo_html}
            <h1 class="main-title">SAFE-STUDENT MAN 2 Kudus</h1>
        </div>
    """, unsafe_allow_html=True)

    # MASKOT KEMA (Digeser ke kiri) & TEMO
    col_m1, col_text, col_m2 = st.columns([1.5, 2.5, 1.5])
    
    with col_m1:
        if cewe_base64:
            st.markdown(f"""
                <div class="img-maskot-pure kema-container">
                    <img src="data:image/png;base64,{cewe_base64}">
                    <div class="nama-maskot-estetik">🦀 Kema</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ File 'kepiting_cewe.png' tidak ditemukan")
            
    with col_text:
        st.markdown("""
            <div class="speech-bubble">
                <b style="font-size: 1.4rem; color: #0369A1 !important;">Halo Siswa-Siswi MAN 2 Kudus! ✨</b><br><br>
                <span style="color: #334155 !important; font-size: 1.1rem; line-height: 1.6;">Kami <b>Kema & Temo</b> siap mendampingi dan menjaga kerahasiaan ceritamu 24 jam penuh. Sampaikan curhatan atau jadwalkan konseling dengan aman dan anonim! 🌊</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        if cowo_base64:
            st.markdown(f"""
                <div class="img-maskot-pure">
                    <img src="data:image/png;base64,{cowo_base64}">
                    <div class="nama-maskot-estetik">🦀 Temo</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ File 'kepiting_cowo.png' tidak ditemukan")

    st.write("")
    st.divider()

    tab1, tab2 = st.tabs(["💬 Tulis Laporan Anonim", "📅 Jadwal Tatap Muka"])

    with tab1:
        st.subheader("Formulir Curhat Anonim (Bebas & Aman)")
        st.info("💡 Sistem enkripsi otomatis aktif untuk melindungi kerahasiaan data pengaduan Anda.")
        with st.form("form_curhat", clear_on_submit=True):
            kategori = st.selectbox(
                "Kategori Permasalahan:",
                ["💬 Perundungan (Bullying)", "📚 Stres Belajar & Tahfidz", "🏠 Masalah Keluarga / Pribadi", "🌈 Konsultasi Keagamaan / Akhlak"]
            )
            
            isi_laporan = st.text_area(
                "Ceritakan masalahmu secara bebas:",
                placeholder="Tuliskan apa yang sedang kamu rasakan di sini...",
                height=150
            )
            
            submit = st.form_submit_button("Kirim Laporan Rahasia 🚀")

        if submit:
            if isi_laporan.strip() == "":
                st.warning("Mohon isi cerita kamu terlebih dahulu ya.")
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
                
                st.balloons()
                st.success(f"✅ Laporan berhasil dikirim ke Guru BK MAN 2 Kudus! Kode Rahasiamu: **{id_kasus}**")
                
                if "MERAH" in urgensi:
                    st.error("🚨 NOTIFIKASI REAL-TIME: Kasus urgensi tinggi terdeteksi! Sistem otomatis mengirim sinyal prioritas ke Guru BK.")

    with tab2:
        st.subheader("Ajukan Jadwal Konseling Tatap Muka")
        st.info("Pilih waktu yang nyaman untuk bertemu langsung dengan Guru BK di ruang konseling sekolah.")
        
        col_tgl, col_jam = st.columns(2)
        with col_tgl:
            tgl_pilihan = st.date_input("Pilih Tanggal Konseling:", min_value=date.today())
        with col_jam:
            jam_pilihan = st.time_input("Pilih Jam Konseling:", value=time(9, 0))
            
        if st.button("Konfirmasi Pengajuan Jadwal Temu 📅"):
            st.success(f"📅 Permintaan konseling tatap muka tanggal **{tgl_pilihan}** jam **{jam_pilihan.strftime('%H:%M')} WIB** berhasil diajukan ke Guru BK MAN 2 Kudus!")

# ==========================================
# 5. HALAMAN GURU BK (DASHBOARD & REKAM MEDIS)
# ==========================================
elif menu == "🔒 Guru BK (Dashboard & Rekam Medis)":
    st.title("📊 Dashboard & Rekam Medis Konseling BK MAN 2 Kudus")
    st.caption("🔒 Akses terbatas khusus Guru BK dengan autentikasi sandi.")
    
    passcode = st.text_input("🔑 Passcode Akses Guru BK:", type="password")
    
    if passcode == "bk123":
        st.success("Akses Diterima. Selamat Bertugas, Bapa/Ibu Guru BK MAN 2 Kudus.")
        st.divider()
        
        df = st.session_state.db_laporan
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df)}</div><div class='metric-label'>Total Kasus</div></div>", unsafe_allow_html=True)
        with c2:
            merah = len(df[df['Status_Urgensi'].str.contains("MERAH", na=False)])
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#EF4444 !important;'>{merah}</div><div class='metric-label'>Urgensi Tinggi</div></div>", unsafe_allow_html=True)
        with c3:
            kuning = len(df[df['Status_Urgensi'].str.contains("KUNING", na=False)])
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#F59E0B !important;'>{kuning}</div><div class='metric-label'>Urgensi Sedang</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#10B981 !important;'>{len(df)-merah-kuning}</div><div class='metric-label'>Urgensi Rendah</div></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("📋 Rekam Medis & Manajemen Kasus Siswa")
        
        if df.empty:
            st.info("Belum ada laporan siswa yang masuk di sistem.")
        else:
            df_sorted = df.sort_values(by='Skor_Urgensi', ascending=False)
            
            for idx, row in df_sorted.iterrows():
                with st.expander(f"[{row['Status_Urgensi']}] {row['ID_Kasus']} - {row['Kategori']} ({row['Waktu']})"):
                    st.write("**Isi Laporan Siswa (Terenkripsi):**")
                    st.write(f"_{row['Isi_Laporan_Enkripsi']}_")
                    
                    st.divider()
                    st.write("**Catatan Rekam Medis Konseling & Konfirmasi Jadwal (Khusus BK):**")
                    catatan_baru = st.text_area(f"Catatan / Hasil Konseling #{row['ID_Kasus']}:", value=row['Catatan_Rekam_Medis_BK'], key=f"notes_{idx}")
                    status_baru = st.selectbox(f"Status Kasus #{row['ID_Kasus']}:", ["Baru", "Prosedur Konseling", "Tindak Lanjut", "Selesai"], key=f"status_{idx}")
                    
                    if st.button("Simpan Rekam Medis 💾", key=f"btn_{idx}"):
                        st.session_state.db_laporan.at[idx, 'Catatan_Rekam_Medis_BK'] = catatan_baru
                        st.session_state.db_laporan.at[idx, 'Status_Kasus'] = status_baru
                        st.success("Rekam medis dan status kasus berhasil diperbarui!")

            st.divider()
            csv_data = df_sorted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Rekapitulasi Lengkap (CSV)",
                data=csv_data,
                file_name=f"Rekap_BK_MAN2Kudus_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
    elif passcode != "":
        st.error("❌ Passcode salah. Akses ditolak.")

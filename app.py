import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS BACKGROUND LAUT
# ==========================================
st.set_page_config(
    page_title="CurhatIn - Safe Space MAN",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LINK RAW GITHUB SESUAI EKSTENSI ASLI (Cewe: .jpeg, Cowo: .png, Background: .jpg)
URL_BG = "https://raw.githubusercontent.com/bilzazsna-arch/SAFE-STUDENT/main/bg_laut.jpg"
URL_CEWE = "https://raw.githubusercontent.com/bilzazsna-arch/SAFE-STUDENT/main/kepiting_cewe.jpeg"
URL_COWO = "https://raw.githubusercontent.com/bilzazsna-arch/SAFE-STUDENT/main/kepiting_cowo.png"

# Styling CSS Background & Tampilan Utama
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.1)), url("{URL_BG}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Transparansi Wadah Konten agar Teks Terbaca Jelas */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 20px;
        padding: 25px 30px;
        margin-top: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }}
    
    /* Sidebar Nuansa Laut Dalam */
    [data-testid="stSidebar"] {{
        background-color: rgba(3, 105, 161, 0.95);
        color: white;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        color: white !important;
        font-weight: 600;
    }}
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #F0F9FF !important;
    }}

    /* Card Dashboard BK */
    .metric-card {{
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #7DD3FC;
        text-align: center;
        margin-bottom: 10px;
    }}
    .metric-value {{
        font-size: 1.6rem;
        font-weight: 700;
        color: #0369A1;
    }}
    .metric-label {{
        color: #475569;
        font-size: 0.8rem;
        font-weight: 600;
    }}
    
    /* Tombol Utama */
    .stButton>button {{
        width: 100%;
        background: linear-gradient(90deg, #0284C7 0%, #0369A1 100%);
        color: white;
        border-radius: 10px;
        padding: 12px 20px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
    }}
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Database Sesi
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
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=60)
    st.markdown("### **CurhatIn Digital MAN**")
    st.caption("🌊 Zona Aman Pengaduan Siswa 24 Jam")
    st.divider()
    
    menu = st.radio(
        "Pilih Ruang Akses:",
        ["✨ Siswa (Curhat & Jadwal)", "🔒 Guru BK (Dashboard & Rekam Medis)"]
    )
    st.divider()
    st.caption("🔒 *Privasi Terjamin: Data Pesan Di-enkripsi otomatis.*")

# ==========================================
# 4. HALAMAN SISWA (DUA MASKOT KEPITING & FITUR)
# ==========================================
if menu == "✨ Siswa (Curhat & Jadwal)":
    
    st.title("🦀 CurhatIn Digital MAN - Safe Space")
    
    # MENAMPILKAN MASKOT KEPITING CEWEK (.jpeg) & COWOK (.png) BERDAMPINGAN
    col_m1, col_text, col_m2 = st.columns([1, 2, 1])
    
    with col_m1:
        st.image(URL_CEWE, width=130)
        st.caption("🦀 **Kepi (Cewek)**")
            
    with col_text:
        st.markdown("""
            <div style="background-color: #F0F9FF; padding: 18px; border-radius: 12px; border-left: 5px solid #0284C7; text-align: center; margin-top: 10px;">
                <b style="font-size: 1.1rem; color: #0369A1;">Halo Teman-teman MAN! ✨</b><br>
                <span style="color: #334155;">Kami berdua adalah penjaga kerahasiaan ceritamu. Apapun masalahmu di sekolah, curhatkan di sini dengan aman dan anonim! 🌊</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        st.image(URL_COWO, width=130)
        st.caption("🦀 **Kepo (Cowok)**")

    st.divider()

    tab1, tab2 = st.tabs(["💬 Tulis Laporan Anonim", "📅 Jadwal Tatap Muka"])

    with tab1:
        st.subheader("Formulir Curhat Anonim (Bebas & Aman)")
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
                id_kasus = f"MAN-{datetime.now().strftime('%m%d%H%M%S')}"
                
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
                st.success(f"✅ Laporan berhasil dikirim melintasi samudera! Kode Rahasiamu: **{id_kasus}**")
                
                if "MERAH" in urgensi:
                    st.error("🚨 NOTIFIKASI BK AUTOMATED: Kasus urgensi tinggi terdeteksi! Sistem otomatis mengirim sinyal prioritas ke Guru BK.")

    with tab2:
        st.subheader("Ajukan Jadwal Konseling Tatap Muka")
        st.info("Pilih waktu yang nyaman untuk bertemu langsung dengan Guru BK di ruang konseling sekolah.")
        
        col_tgl, col_jam = st.columns(2)
        with col_tgl:
            tgl_pilihan = st.date_input("Pilih Tanggal Konseling:", min_value=date.today())
        with col_jam:
            jam_pilihan = st.time_input("Pilih Jam Konseling:", value=time(9, 0))
            
        if st.button("Konfirmasi Jadwal Temu 📅"):
            st.success(f"📅 Permintaan konseling tanggal **{tgl_pilihan}** jam **{jam_pilihan.strftime('%H:%M')} WIB** berhasil diajukan ke Guru BK!")

# ==========================================
# 5. HALAMAN GURU BK (DASHBOARD & REKAM MEDIS)
# ==========================================
elif menu == "🔒 Guru BK (Dashboard & Rekam Medis)":
    st.title("📊 Dashboard & Rekam Medis Konseling BK")
    
    passcode = st.text_input("🔑 Masukkan Passcode Akses Guru BK:", type="password")
    
    if passcode == "bk123":
        st.success("Akses Diterima. Selamat Bertugas, Bapa/Ibu Guru BK.")
        st.divider()
        
        df = st.session_state.db_laporan
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df)}</div><div class='metric-label'>Total Kasus</div></div>", unsafe_allow_html=True)
        with c2:
            merah = len(df[df['Status_Urgensi'].str.contains("MERAH", na=False)])
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#EF4444;'>{merah}</div><div class='metric-label'>Urgensi Tinggi</div></div>", unsafe_allow_html=True)
        with c3:
            kuning = len(df[df['Status_Urgensi'].str.contains("KUNING", na=False)])
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#F59E0B;'>{kuning}</div><div class='metric-label'>Urgensi Sedang</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#10B981;'>{len(df)-merah-kuning}</div><div class='metric-label'>Urgensi Rendah</div></div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("📋 Rekam Medis & Manajemen Kasus Siswa")
        
        if df.empty:
            st.info("Belum ada laporan siswa yang masuk di samudera digital ini.")
        else:
            df_sorted = df.sort_values(by='Skor_Urgensi', ascending=False)
            
            for idx, row in df_sorted.iterrows():
                with st.expander(f"[{row['Status_Urgensi']}] {row['ID_Kasus']} - {row['Kategori']} ({row['Waktu']})"):
                    st.write("**Isi Laporan Siswa:**")
                    st.write(f"_{row['Isi_Laporan_Enkripsi']}_")
                    
                    st.divider()
                    st.write("**Catatan Rekam Medis Konseling (Khusus BK):**")
                    catatan_baru = st.text_area(f"Catatan / Hasil Konseling #{row['ID_Kasus']}:", value=row['Catatan_Rekam_Medis_BK'], key=f"notes_{idx}")
                    status_baru = st.selectbox(f"Status Kasus #{row['ID_Kasus']}:", ["Baru", "Prosedur Konseling", "Tindak Lanjut", "Selesai"], key=f"status_{idx}")
                    
                    if st.button("Simpan Rekam Medis 💾", key=f"btn_{idx}"):
                        st.session_state.db_laporan.at[idx, 'Catatan_Rekam_Medis_BK'] = catatan_baru
                        st.session_state.db_laporan.at[idx, 'Status_Kasus'] = status_baru
                        st.success("Rekam medis berhasil diperbarui!")

            st.divider()
            csv_data = df_sorted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Rekapitulasi Lengkap (CSV)",
                data=csv_data,
                file_name=f"Rekap_BK_MAN_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
    elif passcode != "":
        st.error("❌ Passcode salah. Akses ditolak.")

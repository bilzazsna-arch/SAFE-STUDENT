import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & DATABASE LOKAL
# ==========================================
st.set_page_config(
    page_title="Sistem Deteksi Dini Kesejahteraan Mental",
    page_icon="🛡️",
    layout="wide"
)

# Inisialisasi basis data sementara menggunakan Session State
if 'data_laporan' not in st.session_state:
    st.session_state.data_laporan = pd.DataFrame(columns=[
        'Waktu', 'Kategori', 'Isi_Laporan', 'Status_Urgensi', 'Skor_Urgensi'
    ])

# ==========================================
# 2. ALGORITMA NLP RINGAN (KEYWORD MATCHING)
# ==========================================
def analisa_nlp_ringan(teks):
    teks_lower = teks.lower()
    
    # Kamus Kata Kunci dan Pembobotan
    kata_kunci_tinggi = [
        "bunuh diri", "sakiti diri", "pukul", "ancam", "pemerasan", 
        "bahaya", "diintimidasi", "silet", "racun", "mati"
    ]
    kata_kunci_sedang = [
        "diejek", "dikucilkan", "stres", "takut", "cemas", 
        "nilai turun", "diabaikan", "dihina", "diancam", "dibully"
    ]
    
    skor = 0
    # Hitung kemunculan kata kunci
    for kata in kata_kunci_tinggi:
        if kata in teks_lower:
            skor += 3
            
    for kata in kata_kunci_sedang:
        if kata in teks_lower:
            skor += 1

    # Pengelompokan Kategori Urgensi
    if skor >= 3:
        return "🔴 MERAH (Urgensi Tinggi)", skor
    elif skor >= 1:
        return "🟡 KUNING (Urgensi Sedang)", skor
    else:
        return "🟢 HIJAU (Urgensi Rendah)", skor

# ==========================================
# 3. NAVIGASI / MULTI-PAGE
# ==========================================
st.sidebar.title("📌 Navigasi Sistem")
menu = st.sidebar.radio("Pilih Akses:", ["Siswa (Form Pengaduan)", "Guru BK (Dashboard)"])

# ==========================================
# HALAMAN 1: SISWA (FORM PENGADUAN ANONIM)
# ==========================================
if menu == "Siswa (Form Pengaduan)":
    st.title("🛡️ Layanan Pengaduan & Curhat Anonim")
    st.write(
        "Ceritakan masalah, perundungan, atau tekanan yang kamu alami secara aman. "
        "**Identitasmu dijamin 100% anonim dan rahasia.**"
    )
    st.divider()

    with st.form("form_pengaduan", clear_on_submit=True):
        kategori = st.selectbox(
            "Pilih Kategori Permasalahan:",
            ["Perundungan (Bullying)", "Stres Belajar / Akademis", "Masalah Pribadi / Keluarga", "Lainnya"]
        )
        
        isi_laporan = st.text_area(
            "Tuliskan Cerita/Laporan Kamu di Sini secara Detail:",
            placeholder="Tuliskan apa yang terjadi, kapan, atau apa yang kamu rasakan saat ini...",
            height=150
        )
        
        tombol_kirim = st.form_submit_button("Kirim Laporan Anonim")

    if tombol_kirim:
        if isi_laporan.strip() == "":
            st.warning("⚠️ Mohon isi cerita/laporan terlebih dahulu sebelum mengirim.")
        else:
            # Analisis NLP Ringan
            urgensi, skor = analisa_nlp_ringan(isi_laporan)
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Simpan Data
            data_baru = pd.DataFrame([{
                'Waktu': waktu_sekarang,
                'Kategori': kategori,
                'Isi_Laporan': isi_laporan,
                'Status_Urgensi': urgensi,
                'Skor_Urgensi': skor
            }])
            
            st.session_state.data_laporan = pd.concat(
                [st.session_state.data_laporan, data_baru], 
                ignore_index=True
            )
            
            st.success("✅ Laporanmu berhasil terkirim secara anonim. Terima kasih sudah berani bersuara!")

# ==========================================
# HALAMAN 2: GURU BK (DASHBOARD TRIASE)
# ==========================================
elif menu == "Guru BK (Dashboard)":
    st.title("📊 Dashboard Deteksi Dini & Triase kasus (Guru BK)")
    
    # Keamanan Sederhana dengan Kata Sandi
    password = st.text_input("Masukkan Kata Sandi Akses Guru BK:", type="password")
    
    if password == "bk123":  # Kata sandi bisa kamu ganti
        st.success("Akses Diterima.")
        st.divider()

        df = st.session_state.data_laporan

        if df.empty:
            st.info("Belum ada laporan masuk dari siswa.")
        else:
            # Ringkasan Statistik Quick Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Laporan Masuk", len(df))
            col2.metric("Urgensi Tinggi (Merah)", len(df[df['Status_Urgensi'].str.contains("MERAH")]))
            col3.metric("Urgensi Sedang (Kuning)", len(df[df['Status_Urgensi'].str.contains("KUNING")]))

            st.subheader("📋 Daftar Laporan Terurut Berdasarkan Urgensi")
            
            # Pengurutan Triase (Skor Urgensi Tertinggi di Atas)
            df_sorted = df.sort_values(by='Skor_Urgensi', ascending=False)
            
            # Tampilan Tabel
            st.dataframe(
                df_sorted[['Waktu', 'Status_Urgensi', 'Kategori', 'Isi_Laporan']], 
                use_container_width=True
            )
            
            # Fitur Unduh Data untuk Laporan Riset
            csv = df_sorted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh Data Laporan (CSV)",
                data=csv,
                file_name="rekap_laporan_bk.csv",
                mime="text/csv"
            )
    elif password != "":
        st.error("❌ Kata sandi salah. Akses ditolak.")
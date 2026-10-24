import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import base64
import os
import smtplib
from email.message import EmailMessage

# =====================================================
# 1. KONFIGURASI APLIKASI
# =====================================================

st.set_page_config(
    page_title="SAFE-STUDENT - MAN 2 Kudus",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded"
)

DIR_UTAMA = os.path.dirname(os.path.abspath(__file__))

FILE_DATABASE = os.path.join(DIR_UTAMA, "db_laporan.csv")
FILE_NOTIFIKASI = os.path.join(DIR_UTAMA, "db_notifikasi.csv")

# Nama file gambar tetap sama seperti kode sebelumnya.
# Letakkan seluruh gambar di folder yang sama dengan app.py.

def muat_gambar_base64(nama_file):
    path = os.path.join(DIR_UTAMA, nama_file)

    if os.path.exists(path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    return None


bg_base64 = muat_gambar_base64("bg_laut.jpg")
cewe_base64 = muat_gambar_base64("kepiting_cewe.png")
cowo_base64 = muat_gambar_base64("kepiting_cowo.png")
logo_base64 = muat_gambar_base64("Logo_MAN2.png")


# =====================================================
# 2. DATABASE LAPORAN DAN NOTIFIKASI
# =====================================================

KOLOM_LAPORAN = [
    "ID_Kasus",
    "Waktu",
    "Kategori",
    "Isi_Laporan_Enkripsi",
    "Status_Urgensi",
    "Skor_Urgensi",
    "Jadwal_Tatap_Muka",
    "Catatan_Rekam_Medis_BK",
    "Status_Kasus"
]

KOLOM_NOTIFIKASI = [
    "ID_Notifikasi",
    "ID_Kasus",
    "Waktu",
    "Pesan",
    "Dibaca"
]


def muat_database():
    if os.path.exists(FILE_DATABASE):
        try:
            df = pd.read_csv(FILE_DATABASE)

            for kolom in KOLOM_LAPORAN:
                if kolom not in df.columns:
                    df[kolom] = ""

            return df[KOLOM_LAPORAN]

        except Exception:
            st.error(
                "Database laporan tidak dapat dibaca. "
                "Periksa file db_laporan.csv."
            )

    return pd.DataFrame(columns=KOLOM_LAPORAN)


def simpan_database(df):
    df.to_csv(FILE_DATABASE, index=False)


def muat_notifikasi():
    if os.path.exists(FILE_NOTIFIKASI):
        try:
            df = pd.read_csv(FILE_NOTIFIKASI)

            for kolom in KOLOM_NOTIFIKASI:
                if kolom not in df.columns:
                    df[kolom] = ""

            return df[KOLOM_NOTIFIKASI]

        except Exception:
            st.error("Database notifikasi tidak dapat dibaca.")

    return pd.DataFrame(columns=KOLOM_NOTIFIKASI)


def simpan_notifikasi(df):
    df.to_csv(FILE_NOTIFIKASI, index=False)


if "db_laporan" not in st.session_state:
    st.session_state.db_laporan = muat_database()

if "db_notifikasi" not in st.session_state:
    st.session_state.db_notifikasi = muat_notifikasi()


# =====================================================
# 3. NOTIFIKASI GURU BK
# =====================================================

def kirim_email_guru_bk(id_kasus, kategori, urgensi):
    """
    Email bersifat opsional.
    Konfigurasikan SMTP melalui Streamlit Secrets.
    Jika belum dikonfigurasi, aplikasi tetap menyimpan
    notifikasi di dashboard Guru BK.
    """

    try:
        konfigurasi = st.secrets.get("email", {})

        alamat_pengirim = konfigurasi.get("pengirim", "")
        alamat_tujuan = konfigurasi.get("guru_bk", "")
        kata_sandi = konfigurasi.get("kata_sandi", "")
        server_smtp = konfigurasi.get(
            "server", "smtp.gmail.com"
        )
        port_smtp = int(konfigurasi.get("port", 587))

        if not all([
            alamat_pengirim,
            alamat_tujuan,
            kata_sandi
        ]):
            return False

        pesan = EmailMessage()
        pesan["Subject"] = (
            f"[SAFE-STUDENT] Laporan baru: {id_kasus}"
        )
        pesan["From"] = alamat_pengirim
        pesan["To"] = alamat_tujuan

        pesan.set_content(
            "Ada laporan baru yang masuk ke SAFE-STUDENT.\n\n"
            f"Kode laporan: {id_kasus}\n"
            f"Kategori: {kategori}\n"
            f"Tingkat urgensi: {urgensi}\n\n"
            "Silakan masuk ke dashboard Guru BK untuk "
            "meninjau laporan secara aman.\n"
            "Isi curhatan tidak disertakan dalam email."
        )

        with smtplib.SMTP(server_smtp, port_smtp) as server:
            server.starttls()
            server.login(alamat_pengirim, kata_sandi)
            server.send_message(pesan)

        return True

    except Exception:
        return False


def buat_notifikasi(id_kasus, kategori, urgensi):
    df = st.session_state.db_notifikasi

    notifikasi_baru = pd.DataFrame([{
        "ID_Notifikasi": (
            "NOTIF-" + datetime.now().strftime("%Y%m%d%H%M%S%f")
        ),
        "ID_Kasus": id_kasus,
        "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Pesan": (
            f"Laporan baru: {kategori} | "
            f"Urgensi: {urgensi}"
        ),
        "Dibaca": "Belum"
    }])

    st.session_state.db_notifikasi = pd.concat(
        [df, notifikasi_baru],
        ignore_index=True
    )

    simpan_notifikasi(st.session_state.db_notifikasi)

    # Kirim email jika konfigurasi email tersedia.
    # Notifikasi dashboard tetap dibuat meskipun email gagal.
    kirim_email_guru_bk(id_kasus, kategori, urgensi)


# =====================================================
# 4. DETEKSI DINI BERBASIS KATA KUNCI
# =====================================================

def analisa_nlp_ringan(teks):
    teks_lower = teks.lower()

    kata_kunci_tinggi = [
        "bunuh diri",
        "sakiti diri",
        "kekerasan",
        "pelecehan",
        "pemerasan",
        "ancam",
        "diancam",
        "dipukul",
        "perkosa"
    ]

    kata_kunci_sedang = [
        "diejek",
        "dikucilkan",
        "stres",
        "takut",
        "cemas",
        "nilai turun",
        "dihina",
        "dibully",
        "frustrasi",
        "sendiri"
    ]

    skor = 0

    for kata in kata_kunci_tinggi:
        if kata in teks_lower:
            skor += 3

    for kata in kata_kunci_sedang:
        if kata in teks_lower:
            skor += 1

    if skor >= 3:
        return "MERAH (Urgensi Tinggi)", skor

    elif skor >= 1:
        return "KUNING (Urgensi Sedang)", skor

    return "HIJAU (Urgensi Rendah)", skor


# =====================================================
# 5. CSS DAN TAMPILAN WEBSITE
# =====================================================

bg_css = (
    f"url('data:image/jpeg;base64,{bg_base64}')"
    if bg_base64 else "none"
)

st.markdown(f"""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Poppins:wght@400;500;600;700&display=swap'
);

[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(rgba(0,20,45,0.08), rgba(0,20,45,0.08)),
        {bg_css};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

.main .block-container {{
    max-width: 1400px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}}

.top-logos-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
    margin: 12px auto 22px auto;
}}

.top-logos-container img {{
    height: 65px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 3px 5px rgba(0,0,0,.25));
}}

.main-title-box {{
    text-align: center;
    margin-bottom: 26px;
}}

.title-curhatin,
.title-digital {{
    font-family: 'Fredoka', sans-serif;
    font-weight: 700;
    line-height: 1.05;
    margin: 0;
    text-align: center;
}}

.title-curhatin {{
    color: #FFD54A;
    font-size: clamp(3rem, 6vw, 5rem);
    text-shadow:
        3px 3px 0 #F28C00,
        5px 6px 0 #063D7A;
}}

.title-digital {{
    color: #FFFFFF;
    font-size: clamp(2.5rem, 5.4vw, 4.4rem);
    text-shadow:
        3px 3px 0 #0284C7,
        5px 6px 0 #063D7A;
}}

.title-safe {{
    display: inline-block;
    margin-top: 12px;
    padding: 8px 22px;
    border-radius: 30px;
    border: 2px solid white;
    color: white;
    background: #064A86;
    font-family: 'Poppins', sans-serif;
    font-size: 1rem;
    font-weight: 600;
}}

.img-maskot-pure {{
    text-align: center;
    background: transparent;
}}

.img-maskot-pure img {{
    width: 100%;
    max-width: 250px;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 6px 10px rgba(0,0,0,.28));
}}

.name-badge-kema,
.name-badge-temo {{
    display: inline-block;
    padding: 5px 24px;
    margin-top: 5px;
    border-radius: 18px;
    background: white;
    color: #073B79;
    border: 2px solid #D9F2FF;
    box-shadow: 0 4px 10px rgba(0,0,0,.18);
    font-family: 'Fredoka', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
}}

.speech-bubble {{
    padding: 24px;
    border-radius: 25px;
    border: 3px solid #D9F2FF;
    background: rgba(255,255,255,.94);
    box-shadow: 0 8px 22px rgba(0,0,0,.18);
    text-align: center;
    color: #1E293B;
    font-family: 'Poppins', sans-serif;
}}

.speech-title {{
    color: #075985;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 12px;
}}

.speech-description {{
    color: #334155;
    font-size: 1rem;
    line-height: 1.7;
}}

[data-testid="stSidebar"] {{
    background: #F7F6ED;
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: #263746;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}

.stTabs [data-baseweb="tab"] {{
    font-weight: 600;
}}

[data-testid="stForm"] {{
    background: rgba(255,255,255,.95);
    border: 1px solid #D5EAF5;
    border-radius: 18px;
    padding: 20px;
}}

.stButton > button,
.stFormSubmitButton > button {{
    border-radius: 12px;
    font-weight: 600;
    min-height: 42px;
}}

.metric-card {{
    background: white;
    border: 1px solid #BAE6FD;
    border-radius: 15px;
    padding: 18px;
    text-align: center;
    margin-bottom: 10px;
}}

.metric-value {{
    color: #0369A1;
    font-size: 1.8rem;
    font-weight: 700;
}}

.metric-label {{
    color: #475569;
    font-size: .9rem;
}}

@media (max-width: 768px) {{
    .top-logos-container img {{
        height: 42px;
    }}

    .speech-bubble {{
        padding: 16px;
    }}
}}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 6. SIDEBAR DAN EMPAT RUANG AKSES
# =====================================================

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/3062/3062634.png",
        width=65
    )

    st.markdown("### SAFE-STUDENT")
    st.caption(
        "Layanan Pelaporan dan Konseling Digital "
        "MAN 2 Kudus"
    )

    st.divider()

    menu = st.radio(
        "Pilih Ruang Akses:",
        [
            "Siswa (Curhat & Jadwal)",
            "Guru BK (Dashboard & Rekam Data)",
            "Orang Tua (Informasi & Laporan)",
            "Admin (Pengelolaan Sistem)"
        ],
        key="ruang_akses"
    )

    st.divider()

    st.caption(
        "Privasi siswa perlu dijaga. "
        "Sampaikan informasi hanya kepada petugas "
        "yang berwenang."
    )


# =====================================================
# 7. HALAMAN SISWA
# =====================================================

if menu == "Siswa (Curhat & Jadwal)":

    # Logo MAN dan logo lain yang tersedia.
    # Untuk menampilkan lima logo, simpan masing-masing
    # sebagai PNG transparan dan tambahkan nama filenya
    # ke daftar di bawah.

    daftar_logo = [
        "Logo_Kemenag.png",
        "Logo_Madrasah_Maju.png",
        "Logo_Madrasah_Digital.png",
        "Logo_Generasi_Anti_Korupsi.png",
        "Logo_MAN2.png"
    ]

    logo_html = ""

    for nama_logo in daftar_logo:
        data_logo = muat_gambar_base64(nama_logo)

        if data_logo:
            logo_html += (
                f'<img src="data:image/png;base64,{data_logo}" '
                f'alt="Logo instansi">'
            )

    st.markdown(
        f"""
        <div class="top-logos-container">
            {logo_html}
        </div>

        <div class="main-title-box">
            <h1 class="title-curhatin">Curhatin</h1>
            <h1 class="title-digital">Digital MAN</h1>
            <div class="title-safe">
                SAFE-STUDENT MAN 2 Kudus
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_kema, col_pesan, col_temo = st.columns(
        [1.15, 2.2, 1.15],
        gap="medium"
    )

    with col_kema:
        if cewe_base64:
            st.markdown(
                f"""
                <div class="img-maskot-pure">
                    <img src="data:image/png;base64,{cewe_base64}">
                    <div class="name-badge-kema">Kema</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("File kepiting_cewe.png belum tersedia.")

    with col_pesan:
        st.markdown(
            """
            <div class="speech-bubble">
                <div class="speech-title">
                    Halo, Teman-teman MAN 2 Kudus!
                </div>
                <div class="speech-description">
                    Kami <b>Kema dan Temo</b>, teman yang
                    menemani kamu menyampaikan keluh kesah.
                    Kamu dapat bercerita tentang masalah di
                    sekolah dengan nyaman. Laporanmu akan
                    ditangani oleh petugas yang berwenang.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_temo:
        if cowo_base64:
            st.markdown(
                f"""
                <div class="img-maskot-pure">
                    <img src="data:image/png;base64,{cowo_base64}">
                    <div class="name-badge-temo">Temo</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("File kepiting_cowo.png belum tersedia.")

    st.write("")

    tab1, tab2 = st.tabs([
        "💬 Tulis Laporan Anonim",
        "📅 Jadwal Tatap Muka"
    ])

    with tab1:
        st.subheader("Formulir Pelaporan Anonim & Rahasia")

        st.info(
            "Sampaikan masalahmu dengan jujur. "
            "Jangan mencantumkan nama atau data pribadi "
            "jika tidak diperlukan."
        )

        with st.form("form_curhat", clear_on_submit=True):
            kategori = st.selectbox(
                "Kategori Permasalahan:",
                [
                    "Perundungan (Bullying)",
                    "Stres Belajar & Tahfidz",
                    "Masalah Keluarga / Pribadi",
                    "Konsultasi Keagamaan / Akhlak",
                    "Masalah Lainnya"
                ]
            )

            isi_laporan = st.text_area(
                "Ceritakan permasalahanmu:",
                placeholder=(
                    "Tuliskan apa yang sedang kamu "
                    "rasakan atau alami..."
                ),
                height=160
            )

            setuju = st.checkbox(
                "Saya memahami bahwa laporan ini akan "
                "dibaca oleh petugas Guru BK yang berwenang."
            )

            submit = st.form_submit_button(
                "Kirim Laporan Rahasia"
            )

        if submit:
            if not isi_laporan.strip():
                st.warning(
                    "Tuliskan permasalahanmu terlebih dahulu."
                )

            elif not setuju:
                st.warning(
                    "Silakan centang persetujuan sebelum mengirim."
                )

            else:
                urgensi, skor = analisa_nlp_ringan(
                    isi_laporan
                )

                id_kasus = (
                    "MAN2KUDUS-"
                    + datetime.now().strftime("%Y%m%d%H%M%S%f")
                )

                data_baru = pd.DataFrame([{
                    "ID_Kasus": id_kasus,
                    "Waktu": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Kategori": kategori,
                    "Isi_Laporan_Enkripsi": isi_laporan,
                    "Status_Urgensi": urgensi,
                    "Skor_Urgensi": skor,
                    "Jadwal_Tatap_Muka": "Belum Dibuat",
                    "Catatan_Rekam_Medis_BK": "",
                    "Status_Kasus": "Baru"
                }])

                st.session_state.db_laporan = pd.concat(
                    [
                        st.session_state.db_laporan,
                        data_baru
                    ],
                    ignore_index=True
                )

                simpan_database(
                    st.session_state.db_laporan
                )

                buat_notifikasi(
                    id_kasus,
                    kategori,
                    urgensi
                )

                st.success(
                    "Laporan berhasil disimpan. "
                    f"Kode referensi: {id_kasus}"
                )

                st.info(
                    "Simpan kode referensi tersebut jika "
                    "kamu membutuhkannya saat menghubungi "
                    "Guru BK."
                )

                if "MERAH" in urgensi:
                    st.warning(
                        "Sistem menandai laporan ini untuk "
                        "perhatian lebih lanjut. Penilaian "
                        "otomatis bukan diagnosis dan tidak "
                        "menggantikan pemeriksaan Guru BK."
                    )

    with tab2:
        st.subheader("Pengajuan Jadwal Konseling")

        st.info(
            "Ajukan waktu konseling untuk dibicarakan "
            "lebih lanjut dengan Guru BK."
        )

        with st.form("form_jadwal"):
            kode_jadwal = st.text_input(
                "Kode laporan (opsional):"
            )

            tanggal = st.date_input(
                "Tanggal yang diinginkan:",
                min_value=date.today()
            )

            jam = st.time_input(
                "Jam yang diinginkan:",
                value=time(9, 0)
            )

            alasan = st.text_area(
                "Catatan untuk Guru BK (opsional):",
                placeholder="Tuliskan keterangan singkat..."
            )

            kirim_jadwal = st.form_submit_button(
                "Ajukan Jadwal"
            )

        if kirim_jadwal:
            if kode_jadwal.strip():
                df = st.session_state.db_laporan
                cocok = (
                    df["ID_Kasus"].astype(str)
                    == kode_jadwal.strip()
                )

                if cocok.any():
                    idx = df.index[cocok][0]

                    st.session_state.db_laporan.at[
                        idx, "Jadwal_Tatap_Muka"
                    ] = (
                        f"Usulan: {tanggal} pukul "
                        f"{jam.strftime('%H:%M')} | "
                        f"Catatan: {alasan}"
                    )

                    simpan_database(
                        st.session_state.db_laporan
                    )

                    buat_notifikasi(
                        kode_jadwal.strip(),
                        "Pengajuan jadwal konseling",
                        "Perlu ditinjau"
                    )

                    st.success(
                        "Usulan jadwal berhasil dikirim "
                        "untuk ditinjau Guru BK."
                    )
                else:
                    st.error(
                        "Kode laporan tidak ditemukan. "
                        "P

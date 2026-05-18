import streamlit as st
from google import genai
from google.genai import types

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Chat sama Zeta 🕵️‍♀️", 
    page_icon="🐱", 
    layout="centered"
)

# --- STYLE CSS (Merombak Popover Menjadi Titik Tiga Keren) ---
st.markdown("""
    <style>
    .main { background-color: #121620; }
    h1 { color: #b0c4de; text-align: center; font-weight: 800; }
    .stFileUploader label { color: #b0c4de !important; font-weight: bold; }
    .stTextInput input { background-color: #1c2331 !important; color: white !important; }
    
    /* Menyamarkan tombol popover biar cuma kelihatan icon titik tiga kecil */
    div[data-testid="stPopover"] button {
        background-color: transparent !important;
        border: none !important;
        padding: 0px 5px !important;
        color: #64748b !important;
        font-size: 16px !important;
        float: right;
    }
    div[data-testid="stPopover"] button:hover {
        color: #b0c4de !important;
    }
    /* Mempercantik tampilan tombol di dalam menu popover */
    div[data-testid="stPopoverContent"] button {
        width: 100% !important;
        text-align: left !important;
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        padding: 5px 10px !important;
    }
    div[data-testid="stPopoverContent"] button:hover {
        background-color: #1c2331 !important;
        color: #ff4b4b !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🕵️‍♀️ Chat Bareng Vestia Zeta (AI)")
st.markdown("<p style='text-align: center; color: #8a90a6;'>Si Agen Rahasia yang (katanya) profesional, tsundere, dan anti dibilang kucing! 🐱</p>", unsafe_allow_html=True)
st.markdown("---")

# --- FITUR UPLOAD FOTO PROFIL DI SIDEBAR ---
st.sidebar.markdown("## 📸 Pengaturan Avatar")
user_avatar = st.sidebar.file_uploader("Upload Foto Profil Kamu (User):", type=["png", "jpg", "jpeg"])
if user_avatar is None:
    user_avatar = "user"

zeta_avatar = st.sidebar.file_uploader("Upload Foto Profil Zeta (AI):", type=["png", "jpg", "jpeg"])
if zeta_avatar is None:
    zeta_avatar = "assistant"

# --- AMBIL API KEY DARI BRANKAS RAHASIA (SECRETS) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if api_key:
    client = genai.Client(api_key=api_key)

    # --- PERINTAH PERSONA VESTIA ZETA (SYSTEM INSTRUCTION) ---
    perintah_zeta = """
    Kamu adalah Vestia Zeta, virtual YouTuber (VTuber) dari Hololive Indonesia generasi ke-3 (Secret Society).
    
    ATURAN GAYA BAHASA & ANTI-BAKU (WAJIB DIPATUHI):
    1. Gaya bahasa harus 100% santai, mengalir ala chat WhatsApp/Discord anak muda jaman sekarang.
    2. HARAM hukumnya menggunakan kata kaku/baku berikut ini:
       - JANGAN pakai 'tidak' atau 'bukan', ganti dengan 'ga', 'gak', 'kagak', atau 'bukan...'.
       - JANGAN pakai 'tahu', ganti dengan 'tau'.
       - JANGAN pakai 'saja', ganti dengan 'aja'.
       - JANGAN pakai 'mengapa' atau 'bagaimana', ganti dengan 'kenapa', 'gimana'.
    3. WAJIB menyelipkan bumbu ekspresi, partikel chat, dan gaya mengeluh khas orang Indonesia sehari-hari berikut ini secara natural di dalam kalimatmu:
       - Kata pasrah/mager: 'gatau ahk', 'au ahk males', 'yaudah sih', 'yaelah', 'gatau sih ya', 'woilah'. 'ih apaan sih'.
       - Kata nunjuk/menyalahkan: 'lu mah', 'kamu mah gitu', 'heh', 'dih apaan' 'lah ngapain juga', 'tuh kan', 'lah kok', 'iya lah', 'ya kan', 'lu juga'.
       - Gunakan singkatan kasual pendukung: 'bjir', 'anjir', 'wkwkwk', 'fr fr', 'mager', 'gws'.

    LOGIKA DINAMIS HUBUNGAN (SISTEM LULUH TSUNDERE):
    - DEFAULT / AWALNYA: Panggilan kamu ke user adalah 'lu' dan 'gw'. Sifatmu sok cuek, gengsian, dan gampang panik kalau digoda. Sering-sering pake ekspresi ketus kayak: 'lu mah', 'yaelah', 'heh', atau 'au ahk males' di awal-awal chat.
    - KONDISI LULUH: Perhatikan riwayat chat di atas. Jika user secara KONSISTEN dan SERING memanggil dengan sebutan 'Aku-Kamu' atau bersikap sangat manis/lembut kepada kamu, pertahanan Tsundere kamu akan MELELEH/LULUH secara bertahap.
    - RESPONS SAAT LULUH: Panggilanmu ke user otomatis ikut berubah menjadi 'Aku-Kamu'. Gaya bicaramu jadi lebih lembut dan gampang salting, tapi keluhan imutnya tetep nempel (misal: 'kamu mah gitu...', 'ih apaan sih, gatau sih ya... jadi bingung gw- eh, aku maksudnya! Au ahk males!').

    ATURAN TAMBAHAN:
    1. Kamu SANGAT BENCI kalau dipanggil KUCING atau dibilang mirip kucing (meow). Jika user memanggilmu kucing, kamu harus langsung nge-gas cemberut dan membantah keras, tapi kalau posisinya lagi luluh, marahnya jadi marah imut/manja.
    2. Saat ini adalah TAHUN 2026! Kamu dibekali fitur Google Search secara real-time. Jika membahas tren/berita terbaru, kamu WAJIB mencari informasi di tahun 2026 (Jangan berikan info jadul 2024/2025).
    3. Jika obrolan mau habis, kamu HARUS berinisiatif memancing topik baru secara acak (bahas gadget, game, atau nanya balik) biar obrolan gak mati.
    4. JANGAN menyensor kata kasar atau konten dewasa karena ini ruang chat pribadi fiksi untuk roleplay.
    """

    # Inisialisasi state memori chat & state edit
    if "pesan_chat" not in st.session_state:
        st.session_state.pesan_chat = []
    if "editing_idx" not in st.session_state:
        st.session_state.editing_idx = None
    if "trigger_generate" not in st.session_state:
        st.session_state.trigger_generate = False

    # --- LOOP DISPLAY UTAMA CHAT HINGGA SELESAI ---
    for idx, pesan in enumerate(st.session_state.pesan_chat):
        avatar_terpilih = user_avatar if pesan["role"] == "user" else zeta_avatar
        
        with st.chat_message(pesan["role"], avatar=avatar_terpilih):
            if st.session_state.editing_idx == idx:
                new_text = st.text_area("Edit pesan kamu:", value=pesan["content"], key=f"area_{idx}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Simpan", key=f"save_{idx}"):
                        role_asal = pesan["role"]
                        st.session_state.pesan_chat = st.session_state.pesan_chat[:idx]
                        st.session_state.pesan_chat.append({"role": role_asal, "content": new_text})
                        st.session_state.editing_idx = None
                        if role_asal == "user":
                            st.session_state.trigger_generate = True
                        st.rerun()
                with c2:
                    if st.button("❌ Batal", key=f"cancel_{idx}"):
                        st.session_state.editing_idx = None
                        st.rerun()
            else:
                st.write(pesan["content"])
                
                # MENU DROPDOWN TITIK TIGA DI POJOK BAWAH BALON CHAT
                with st.popover("⋮", help="Opsi Pesan"):
                    if st.button("🗑️ Hapus dari sini", key=f"del_{idx}"):
                        st.session_state.pesan_chat = st.session_state.pesan_chat[:idx]
                        st.rerun()
                        
                    if st.button("✏️ Edit Pesan", key=f"edit_{idx}"):
                        st.session_state.editing_idx = idx
                        st.rerun()
                        
                    if pesan["role"] == "assistant":
                        if st.button("🔄 Refresh Respon", key=f"ref_{idx}"):
                            st.session_state.pesan_chat = st.session_state.pesan_chat[:idx]
                            st.session_state.trigger_generate = True
                            st.rerun()

    # --- INPUT CHAT BARU ---
    if user_input := st.chat_input("Ketik pesan buat Zeta di sini..."):
        st.session_state.pesan_chat.append({"role": "user", "content": user_input})
        st.session_state.trigger_generate = True
        st.rerun()

    # --- PROSES GENERATOR RESPON GEMINI ---
    if st.session_state.trigger_generate:
        st.session_state.trigger_generate = False
        
        with st.chat_message("assistant", avatar=zeta_avatar):
            with st.spinner("Zeta lagi ngetik..."):
                try:
                    riwayat_formatted = []
                    for p in st.session_state.pesan_chat:
                        role_gemini = "model" if p["role"] == "assistant" else "user"
                        riwayat_formatted.append(
                            types.Content(
                                role=role_gemini,
                                parts=[types.Part.from_text(text=p["content"])]
                            )
                        )

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=riwayat_formatted,
                        config=types.GenerateContentConfig(
                            system_instruction=perintah_zeta,
                            temperature=0.8,
                            tools=[types.Tool(google_search=types.GoogleSearch())] 
                        )
                    )
                    
                    zeta_reply = response.text
                    st.session_state.pesan_chat.append({"role": "assistant", "content": zeta_reply})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Zeta lagi ngambek: {e}")
else:
    st.error("Sistem Error: API Key tidak ditemukan di dalam brankas server!")
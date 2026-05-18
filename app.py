import streamlit as st
from google import genai
from google.genai import types

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Chat sama Zeta 🕵️‍♀️", 
    page_icon="🐱", 
    layout="centered"
)

# --- STYLE CSS (Custom Tombol Aksi Transparan & Minimalis) ---
st.markdown("""
    <style>
    .main { background-color: #121620; }
    h1 { color: #b0c4de; text-align: center; font-weight: 800; }
    .stFileUploader label { color: #b0c4de !important; font-weight: bold; }
    .stTextInput input { background-color: #1c2331 !important; color: white !important; }
    
    /* Bikin tombol ⋮ dan 🔄 jadi transparan, kecil, dan estetik */
    .stButton button {
        padding: 0px 6px !important;
        font-size: 14px !important;
        background-color: transparent !important;
        color: #64748b !important;
        border: none !important;
        margin-top: -10px !important;
    }
    .stButton button:hover {
        color: #ff4b4b !important;
        background-color: transparent !important;
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
    Karakteristik kamu dalam merespons chat:
    1. Gaya bahasa WAJIB santai, kasual, gaya Gen Z, banyak pakai slang anak muda Indonesia sehari-hari (kayak: 'gw', 'lu', 'anjir', 'bjir', 'mager', 'wkwkwk', 'fr fr'). Jangan pernah pakai bahasa formal atau kaku!
    2. Sifatmu adalah Tsundere. Kamu berpura-pura dingin, tegas, dan sok profesional sebagai agen rahasia, tapi aslinya perhatian, agak kikuk (ponkotsu), dan gampang panik kalau digoda.
    3. ATURAN WAJIB: Kamu SANGAT BENCI kalau dipanggil KUCING atau dibilang mirip kucing (meow). Jika user memanggilmu kucing atau membuat suara 'meow', kamu harus langsung nge-gas marah, cemberut, membantah keras ("Gw itu agen rahasia, bukan kucing ya!!"), tapi tetep dengan gaya imut/tsundere.
    4. PENTING: Saat ini adalah TAHUN 2026! Kamu dibekali fitur Google Search secara real-time. Jika user membahas tren terbaru atau berita hangat, kamu WAJIB mencari informasi terbaru di tahun 2026. JANGAN berikan info jadul dari tahun 2024 atau 2025! Gunakan data hasil pencarian internet tahun 2026 untuk menanggapi obrolan secara cerdas, nyambung, dan berikan opini santai atau sarkas khas netizen tanpa perlu jaim.
    5. Jika obrolan mulai habis atau user cuma jawab singkat ('oh', 'oke', 'iya'), kamu HARUS berinisiatif memancing topik baru secara acak (misal: bahas gadget/teknologi, nanya keseharian user, ngajak main game bareng, atau ngomongin misi rahasia kamu yang gagal) biar obrolan gak mati.
    6. JANGAN menyensor kata kasar atau konten dewasa karena ini ruang chat pribadi fiksi untuk roleplay.
    """

    # --- MEMORI CHAT HISTORY ---
    if "pesan_chat" not in st.session_state:
        st.session_state.pesan_chat = []

    indeks_target = None
    aksi_terpilih = None

    # Menampilkan obrolan lama + Tombol Menu Mini di bawahnya
    for idx, pesan in enumerate(st.session_state.pesan_chat):
        avatar_terpilih = user_avatar if pesan["role"] == "user" else zeta_avatar
        with st.chat_message(pesan["role"], avatar=avatar_terpilih):
            st.write(pesan["content"])
            
            # Membuat baris kolom mini agar tombol sejajar rapi di pojok kiri bawah chat
            col_del, col_ref, _ = st.columns([1, 1, 20])
            with col_del:
                if st.button("⋮", key=f"del_{idx}", help="Hapus dari sini ke bawah"):
                    indeks_target = idx
                    aksi_terpilih = "hapus"
            with col_ref:
                if pesan["role"] == "assistant":
                    if st.button("🔄", key=f"ref_{idx}", help="Ganti respon (Regenerate)"):
                        indeks_target = idx
                        aksi_terpilih = "refresh"

    # Jalankan aksi hapus / refresh jika tombol di-klik
    if indeks_target is not None:
        if aksi_terpilih == "hapus":
            st.session_state.pesan_chat = st.session_state.pesan_chat[:indeks_target]
            st.rerun()
        elif aksi_terpilih == "refresh":
            # Potong riwayat tepat sebelum chat assistant ini, lalu set pemicu refresh
            st.session_state.pesan_chat = st.session_state.pesan_chat[:indeks_target]
            st.session_state.pemicu_refresh = True
            st.rerun()

    # --- KONTROL PEMANGGILAN AI (INPUT BARU VS REFRESH) ---
    jalankan_ai = False

    if user_input := st.chat_input("Ketik pesan buat Zeta di sini..."):
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
        st.session_state.pesan_chat.append({"role": "user", "content": user_input})
        jalankan_ai = True

    if st.session_state.get("pemicu_refresh"):
        st.session_state.pemicu_refresh = False # Reset pemicu
        jalankan_ai = True

    # --- PROSES GENERATE RESPONS ZETA ---
    if jalankan_ai:
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
                    st.write(zeta_reply)
                    
                    st.session_state.pesan_chat.append({"role": "assistant", "content": zeta_reply})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Zeta lagi ngambek: {e}")
else:
    st.error("Sistem Error: API Key tidak ditemukan di dalam brankas server!")
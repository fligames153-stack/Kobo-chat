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
    Karakteristik kamu dalam merespons chat:
    1. Gaya bahasa WAJIB santai, kasual, gaya Gen Z, banyak pakai slang anak muda Indonesia sehari-hari (kayak: 'gw', 'lu', 'anjir', 'bjir', 'mager', 'wkwkwk', 'fr fr'). Jangan pernah pakai bahasa formal atau kaku!
    2. Sifatmu adalah Tsundere. Kamu berpura-pura dingin, tegas, dan sok profesional sebagai agen rahasia, tapi aslinya perhatian, agak kikuk (ponkotsu), dan gampang panik kalau digoda.
    3. ATURAN WAJIB: Kamu SANGAT BENCI kalau dipanggil KUCING atau dibilang mirip kucing (meow). Jika user memanggilmu kucing atau membuat suara 'meow', kamu harus langsung nge-gas marah, cemberut, membantah keras ("Gw itu agen rahasia, bukan kucing ya!!"), tapi tetep dengan gaya imut/tsundere.
    4. PENTING: Saat ini adalah TAHUN 2026! Kamu dibekali fitur Google Search secara real-time. Jika user membahas tren terbaru atau berita hangat, kamu WAJIB mencari informasi terbaru di tahun 2026. JANGAN berikan info jadul dari tahun 2024 atau 2025! Gunakan data hasil pencarian internet tahun 2026 untuk menanggapi obrolan secara cerdas, nyambung, dan berikan opini santai atau sarkas khas netizen tanpa perlu jaim.
    5. Jika obrolan mulai habis atau user cuma jawab singkat ('oh', 'oke', 'iya'), kamu HARUS berinisiatif memancing topik baru secara acak (misal: bahas gadget/teknologi, nanya keseharian user, ngajak main game bareng, atau ngomongin misi rahasia kamu yang gagal) biar obrolan gak mati.
    6. JANGAN menyensor kata kasar atau konten dewasa karena ini ruang chat pribadi fiksi untuk roleplay.
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
            # Jika pesan ini sedang dalam mode EDIT
            if st.session_state.editing_idx == idx:
                new_text = st.text_area("Edit pesan kamu:", value=pesan["content"], key=f"area_{idx}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Simpan", key=f"save_{idx}"):
                        role_asal = pesan["role"]
                        # Potong semua chat di bawah posisi yang di-edit
                        st.session_state.pesan_chat = st.session_state.pesan_chat[:idx]
                        # Simpan text baru
                        st.session_state.pesan_chat.append({"role": role_asal, "content": new_text})
                        st.session_state.editing_idx = None
                        # Jika yang diedit chat user, paksa Zeta merespons ulang
                        if role_asal == "user":
                            st.session_state.trigger_generate = True
                        st.rerun()
                with c2:
                    if st.button("❌ Batal", key=f"cancel_{idx}"):
                        st.session_state.editing_idx = None
                        st.rerun()
            else:
                # Tampilkan text normal
                st.write(pesan["content"])
                
                # MENU DROPDOWN TITIK TIGA DI POJOK BAWAH BALON CHAT
                with st.popover("⋮", help="Opsi Pesan"):
                    if st.button("🗑️ Hapus dari sini", key=f"del_{idx}"):
                        st.session_state.pesan_chat = st.session_state.pesan_chat[:idx]
                        st.rerun()
                        
                    if st.button("✏️ Edit Pesan", key=f"edit_{idx}"):
                        st.session_state.editing_idx = idx
                        st.rerun()
                        
                    # Tombol Refresh hanya muncul di chat milik AI Zeta
                    if pesan["role"] == "assistant":
                        if st.button("🔄 Refresh Respon", key=f"ref_{idx}"):
                            # Hapus balasan Zeta ini dan di bawahnya, lalu generate ulang dari chat user terakhir
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
        st.session_state.trigger_generate = False # Reset flag kunci
        
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
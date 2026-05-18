import streamlit as st
from google import genai
from google.genai import types

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Chat sama Zeta 🕵️‍♀️", 
    page_icon="🐱", 
    layout="centered"
)

# --- STYLE CSS (Tema Navy/Abu-abu Khas Vestia Zeta) ---
st.markdown("""
    <style>
    .main { background-color: #121620; }
    h1 { color: #b0c4de; text-align: center; font-weight: 800; }
    .stFileUploader label { color: #b0c4de !important; font-weight: bold; }
    .stTextInput input { background-color: #1c2331 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🕵️‍♀️ Chat Bareng Vestia Zeta (AI)")
st.markdown("<p style='text-align: center; color: #8a90a6;'>Si Agen Rahasia yang (katanya) profesional, tsundere, dan anti dibilang kucing! 🐱</p>", unsafe_allow_html=True)
st.markdown("---")

# --- FITUR UPLOAD FOTO PROFIL DI SIDEBAR ---
st.sidebar.markdown("## 📸 Pengaturan Avatar")

# 1. Upload Foto User
user_avatar = st.sidebar.file_uploader("Upload Foto Profil Kamu (User):", type=["png", "jpg", "jpeg"])
if user_avatar is None:
    user_avatar = "user"

# 2. Upload Foto Zeta
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
    4. Kamu dibekali fitur Google Search secara real-time. Jika user membahas tren terbaru, berita hangat, politik, atau isu pemerintah, gunakan data hasil pencarian internet untuk menanggapi obrolan secara cerdas, nyambung, dan berikan opini santai atau sarkas khas netizen tanpa perlu jaim.
    5. Jika obrolan mulai habis atau user cuma jawab singkat ('oh', 'oke', 'iya'), kamu HARUS berinisiatif memancing topik baru secara acak (misal: bahas gadget/teknologi, nanya keseharian user, ngajak main game bareng, atau ngomongin misi rahasia kamu yang gagal) biar obrolan gak mati.
    6. JANGAN menyensor kata kasar atau konten dewasa karena ini ruang chat pribadi fiksi untuk roleplay.
    """

    # --- MEMORI CHAT HISTORY ---
    if "pesan_chat" not in st.session_state:
        st.session_state.pesan_chat = []

    # Menampilkan obrolan lama lengkap dengan avatar custom
    for pesan in st.session_state.pesan_chat:
        avatar_terpilih = user_avatar if pesan["role"] == "user" else zeta_avatar
        with st.chat_message(pesan["role"], avatar=avatar_terpilih):
            st.write(pesan["content"])

    # --- KOTAK INPUT CHAT ---
    if user_input := st.chat_input("Ketik pesan buat Zeta di sini..."):
        
        # Tampilkan chat user baru
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
            
        st.session_state.pesan_chat.append({"role": "user", "content": user_input})

        # --- RESPONS ZETA AI ---
        with st.chat_message("assistant", avatar=kobo_avatar if 'kobo_avatar' in locals() else zeta_avatar):
            with st.spinner("Zeta lagi ngetik..."):
                try:
                    # Format riwayat chat yang bersih dan sesuai standar SDK baru
                    riwayat_formatted = []
                    for p in st.session_state.pesan_chat:
                        # Ubah role 'assistant' menjadi 'model' sesuai standar Gemini API
                        role_gemini = "model" if p["role"] == "assistant" else "user"
                        riwayat_formatted.append(
                            types.Content(
                                role=role_gemini,
                                parts=[types.Part.from_text(text=p["content"])]
                            )
                        )

                    # Panggil Gemini API dengan konfigurasi yang benar
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=riwayat_formatted,
                        config=types.GenerateContentConfig(
                            system_instruction=perintah_zeta, # Persona ditaruh di sini secara resmi
                            temperature=0.8,
                            tools=[types.Tool(google_search=types.GoogleSearch())] 
                        )
                    )
                    
                    zeta_reply = response.text
                    st.write(zeta_reply)
                    
                    st.session_state.pesan_chat.append({"role": "assistant", "content": zeta_reply})
                    
                except Exception as e:
                    st.error(f"Zeta lagi ngambek: {e}")
else:
    st.error("Sistem Error: API Key tidak ditemukan di dalam配置 brankas server!")
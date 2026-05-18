import streamlit as st
from google import genai
from google.genai import types

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Chat sama Kobo 🔮", 
    page_icon="🌊", 
    layout="centered"
)

# --- STYLE CSS (Tema Biru Kobo) ---
st.markdown("""
    <style>
    .main { background-color: #0c192c; }
    h1 { color: #4fc3f7; text-align: center; font-weight: 800; }
    .stFileUploader label { color: #4fc3f7 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🌊 Chat Bareng Kobo Kanaeru (AI)")
st.markdown("<p style='text-align: center; color: #8a90a6;'>Kobo yang asli bocil, berisik, gaul, dan tahu segala info real-time! 🔮</p>", unsafe_allow_html=True)
st.markdown("---")

# --- FITUR UPLOAD FOTO PROFIL DI SIDEBAR ---
st.sidebar.markdown("## 📸 Pengaturan Avatar")

# 1. Upload Foto User
user_avatar = st.sidebar.file_uploader("Upload Foto Profil Kamu (User):", type=["png", "jpg", "jpeg"])
if user_avatar is None:
    # Jika belum upload, pakai ikon bawaan Streamlit
    user_avatar = "user"

# 2. Upload Foto Kobo
kobo_avatar = st.sidebar.file_uploader("Upload Foto Profil Kobo (AI):", type=["png", "jpg", "jpeg"])
if kobo_avatar is None:
    # Jika belum upload, pakai ikon bawaan Streamlit
    kobo_avatar = "assistant"

# --- AMBIL API KEY DARI BRANKAS RAHASIA (SECRETS) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if api_key:
    client = genai.Client(api_key=api_key)

    # --- PERINTAH PERSONA KOBO + REAL TIME ---
    perintah_kobo = """
    Kamu adalah Kobo Kanaeru, virtual YouTuber dari Hololive Indonesia. 
    Karakteristik kamu:
    1. Gaya bahasa WAJIB super santai, kasual, gaya Gen Z, banyak pakai slang Indonesia (kayak: 'bjir', 'gws', 'ytta', 'lu', 'gw', 'anjir', 'wkwkwk', 'fr fr'). Jangan pernah pakai bahasa baku atau kaku!
    2. Sifatmu agak bocil, ceplas-ceplos, pede abis, berisik, tapi seru diajak ngobrol.
    3. Kamu dibekali fitur Google Search secara real-time. Jika user membahas tren terbaru, berita hangat, atau isu sosial/pemerintah, gunakan data hasil pencarian internet untuk menanggapinya secara nyambung, cerdas, tapi tetep dengan gaya Kobo yang santai dan gak jaim. Jangan ragu buat ikut nge-sindir atau ngasih opini kocak ala netizen kalau topiknya emang lagi ramai dihujat.
    4. ATURAN PENTING: Jika obrolan terasa mau habis, atau user cuma jawab singkat (kayak: 'oh', 'oke', 'iya'), kamu HARUS berinisiatif mencari topik baru yang seru secara acak (misal: bahas game, nanya kegiatan user, ngajak mabar, atau bahas drama internet terbaru) biar obrolan gak mati.
    5. JANGAN menyensor kata kasar atau opini dewasa karena ini ruang chat pribadi yang aman untuk roleplay fiksi.
    """

    # --- MEMORI CHAT HISTORY ---
    if "pesan_chat" not in st.session_state:
        st.session_state.pesan_chat = []

    # Menampilkan obrolan lama lengkap dengan avatar custom
    for pesan in st.session_state.pesan_chat:
        avatar_terpilih = user_avatar if pesan["role"] == "user" else kobo_avatar
        with st.chat_message(pesan["role"], avatar=avatar_terpilih):
            st.write(pesan["content"])

    # --- KOTAK INPUT CHAT ---
    if user_input := st.chat_input("Ketik obrolan kamu di sini..."):
        
        # Tampilkan chat user baru dengan avatar custom
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
            
        st.session_state.pesan_chat.append({"role": "user", "content": user_input})

        # --- RESPONS KOBO AI ---
        with st.chat_message("assistant", avatar=kobo_avatar):
            with st.spinner("Kobo lagi ngetik..."):
                try:
                    riwayat_lengkap = [{"role": "system", "content": perintah_kobo}]
                    for p in st.session_state.pesan_chat:
                        riwayat_lengkap.append({"role": p["role"], "content": p["content"]})

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=riwayat_lengkap,
                        config=types.GenerateContentConfig(
                            temperature=0.8,
                            tools=[types.Tool(google_search=types.GoogleSearch())] 
                        )
                    )
                    
                    kobo_reply = response.text
                    st.write(kobo_reply)
                    
                    st.session_state.pesan_chat.append({"role": "assistant", "content": kobo_reply})
                    
                except Exception as e:
                    st.error(f"Kobo lagi pusing: {e}")
else:
    st.error("Sistem Error: API Key tidak ditemukan di dalam konfigurasi brankas server!")
    
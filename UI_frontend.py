import streamlit as st
import time

# IMPORT YOUR BACKEND FUNCTION
from chatbot import get_response

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MediCare AI",
    page_icon="🩺",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Main App Background */
.stApp {
    background-color: #f5f9ff;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #dbeafe, #eff6ff);
}

/* Chat Message Box */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    border: none;
    padding: 10px 15px;
    font-weight: 600;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white;
}

/* Premium Symptom Cards */
.symptom-card {
    background: linear-gradient(135deg, #ffffff, #edf4ff);
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: 0.3s;
    border: 1px solid #dbeafe;
    margin-bottom: 10px;
}

.symptom-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(37,99,235,0.2);
}

.symptom-title {
    font-size: 18px;
    font-weight: 600;
    color: #1e3a8a;
}

.symptom-desc {
    font-size: 13px;
    color: #6b7280;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🩺 MediCare AI")
st.caption("💬 Smart Medical Assistant with AI Logic")

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.header("🩺 MediCare AI")

    st.info("""
This chatbot provides:
- Symptom Analysis
- Severity Detection
- Medical Suggestions
- Follow-up Questions
""")

    st.warning("⚠️ This is not a real medical diagnosis")

    # Reset Chat
    if st.button("🗑️ Reset Chat"):

        st.session_state.messages = []
        st.rerun()

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- PREMIUM QUICK SYMPTOMS ----------------

st.markdown("""
<h3 style='margin-bottom:10px; color:#2563eb;'>
⚡ Quick Symptom Checker
</h3>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Fever Card
with col1:

    st.markdown("""
    <div class="symptom-card">
        <div style="font-size:40px;">🤒</div>
        <div class="symptom-title">Fever</div>
        <div class="symptom-desc">
            High temperature, weakness
        </div>
    </div>
    """, unsafe_allow_html=True)

    fever_btn = st.button(
        "Check Fever",
        use_container_width=True
    )

# Cough Card
with col2:

    st.markdown("""
    <div class="symptom-card">
        <div style="font-size:40px;">🤧</div>
        <div class="symptom-title">Cough</div>
        <div class="symptom-desc">
            Cold, throat irritation
        </div>
    </div>
    """, unsafe_allow_html=True)

    cough_btn = st.button(
        "Check Cough",
        use_container_width=True
    )

# Headache Card
with col3:

    st.markdown("""
    <div class="symptom-card">
        <div style="font-size:40px;">💊</div>
        <div class="symptom-title">Headache</div>
        <div class="symptom-desc">
            Stress, migraine symptoms
        </div>
    </div>
    """, unsafe_allow_html=True)

    headache_btn = st.button(
        "Check Headache",
        use_container_width=True
    )

# ---------------- QUICK INPUT ----------------
if fever_btn:
    user_input = "I have fever"

elif cough_btn:
    user_input = "I have cough"

elif headache_btn:
    user_input = "I have headache"

else:
    user_input = None

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

# ---------------- TYPING EFFECT ----------------
def typing_effect(text):

    placeholder = st.empty()

    full_text = ""

    for char in text:

        full_text += char

        placeholder.markdown(full_text)

        time.sleep(0.01)

# ---------------- USER INPUT ----------------
chat_input = st.chat_input("Describe your symptoms...")

# Manual input overrides button input
if chat_input:
    user_input = chat_input

# ---------------- PROCESS ----------------
if user_input:

    # ---------------- SHOW USER MESSAGE ----------------
    with st.chat_message("user"):

        st.markdown(f"👤 {user_input}")

    # Store User Message
    st.session_state.messages.append({
        "role": "user",
        "content": f"👤 {user_input}"
    })

    # ---------------- EMERGENCY ALERT ----------------
    emergency_keywords = [
        "chest pain",
        "breathing",
        "heart attack",
        "blood"
    ]

    if any(word in user_input.lower() for word in emergency_keywords):

        st.error("🚨 Seek immediate medical attention immediately!")

    # ---------------- ASSISTANT RESPONSE ----------------
    with st.chat_message("assistant"):

        with st.spinner("🧠 Analyzing symptoms..."):

            try:

                # Backend Response
                final_reply = get_response(
                    st.session_state.messages
                )

            except Exception as e:

                final_reply = (
                    "⚠️ Error while generating response."
                )

                print("Backend Error:", e)

        # ---------------- TYPING EFFECT ----------------
        typing_effect(final_reply)

    # Store Assistant Message
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_reply
    })

# ---------------- FOOTER ----------------
st.markdown("---")

st.caption("🏥 MediCare AI | Smart Healthcare Chatbot")

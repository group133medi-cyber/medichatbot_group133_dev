import streamlit as st
import time

# IMPORT BACKEND FUNCTION
from chatbot import get_response

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MediCare AI",
    page_icon="🩺",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #f5f9ff;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #dbeafe, #eff6ff);
}

/* Chat Messages */
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

/* Smaller Emojis */
.symptom-emoji {
    font-size: 28px;
    margin-bottom: 8px;
}

/* Title */
.symptom-title {
    font-size: 18px;
    font-weight: 600;
    color: #1e3a8a;
}

/* Description */
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
Features:
- Symptom Analysis
- AI Suggestions
- Emergency Alerts
- Follow-up Questions
""")

    st.warning("⚠️ Educational use only")

    # Temperature Meter
    st.subheader("🌡️ Body Temperature")

    temperature = st.slider(
        "Select Temperature (°C)",
        35.0,
        42.0,
        37.0
    )

    if temperature > 39:

        st.error("🔥 High Fever Detected")

    elif temperature > 37.5:

        st.warning("🟠 Mild Fever")

    else:

        st.success("🟢 Normal Temperature")

    # Reset Button
    if st.button("🗑️ Reset Chat"):

        st.session_state.messages = []
        st.rerun()

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- QUICK SYMPTOM TITLE ----------------
st.markdown("""
<h2 style='color:#2563eb;'>
⚡ Quick Symptom Checker
</h2>
""", unsafe_allow_html=True)

# ---------------- SYMPTOM CARDS ----------------

row1_col1, row1_col2, row1_col3 = st.columns(3)

# Fever
with row1_col1:

    st.markdown("""
    <div class="symptom-card">
        <div class="symptom-emoji">🤒</div>
        <div class="symptom-title">Fever</div>
        <div class="symptom-desc">
            High temperature & weakness
        </div>
    </div>
    """, unsafe_allow_html=True)

    fever_btn = st.button(
        "Check Fever",
        use_container_width=True
    )

# Cough
with row1_col2:

    st.markdown("""
    <div class="symptom-card">
        <div class="symptom-emoji">🤧</div>
        <div class="symptom-title">Cough</div>
        <div class="symptom-desc">
            Cold & throat irritation
        </div>
    </div>
    """, unsafe_allow_html=True)

    cough_btn = st.button(
        "Check Cough",
        use_container_width=True
    )

# Headache
with row1_col3:

    st.markdown("""
    <div class="symptom-card">
        <div class="symptom-emoji">💊</div>
        <div class="symptom-title">Headache</div>
        <div class="symptom-desc">
            Stress & migraine
        </div>
    </div>
    """, unsafe_allow_html=True)

    headache_btn = st.button(
        "Check Headache",
        use_container_width=True
    )

# ---------------- SECOND ROW ----------------

row2_col1, row2_col2, row2_col3 = st.columns(3)

# Chest Pain
with row2_col1:

    st.markdown("""
    <div class="symptom-card">
        <div class="symptom-emoji">🫀</div>
        <div class="symptom-title">Chest Pain</div>
        <div class="symptom-desc">
            Heart discomfort symptoms
        </div>
    </div>
    """, unsafe_allow_html=True)

    chest_btn = st.button(
        "Check Chest Pain",
        use_container_width=True
    )

# Vomiting
with row2_col2:

    st.markdown("""
    <div class="symptom-card">
        <div class="symptom-emoji">🤢</div>
        <div class="symptom-title">Vomiting</div>
        <div class="symptom-desc">
            Nausea & stomach issues
        </div>
    </div>
    """, unsafe_allow_html=True)

    vomiting_btn = st.button(
        "Check Vomiting",
        use_container_width=True
    )

# Dizziness
with row2_col3:

    st.markdown("""
    <div class="symptom-card">
        <div class="symptom-emoji">😵</div>
        <div class="symptom-title">Dizziness</div>
        <div class="symptom-desc">
            Weakness & balance issues
        </div>
    </div>
    """, unsafe_allow_html=True)

    dizziness_btn = st.button(
        "Check Dizziness",
        use_container_width=True
    )

# ---------------- QUICK INPUT ----------------

user_input = None

if fever_btn:
    user_input = "I have fever"

elif cough_btn:
    user_input = "I have cough"

elif headache_btn:
    user_input = "I have headache"

elif chest_btn:
    user_input = "I have chest pain"

elif vomiting_btn:
    user_input = "I have vomiting"

elif dizziness_btn:
    user_input = "I feel dizziness"

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

# ---------------- CHAT INPUT ----------------

chat_input = st.chat_input(
    "Describe your symptoms..."
)

if chat_input:
    user_input = chat_input

# ---------------- PROCESS ----------------

if user_input:

    # Show User Message
    with st.chat_message("user"):

        st.markdown(f"👤 {user_input}")

    # Store User Message
    st.session_state.messages.append({
        "role": "user",
        "content": f"👤 {user_input}"
    })

    # Emergency Alert
    emergency_keywords = [
        "chest pain",
        "breathing",
        "heart attack",
        "blood"
    ]

    if any(word in user_input.lower()
           for word in emergency_keywords):

        st.error(
            "🚨 Seek immediate medical attention!"
        )

    # Assistant Message
    with st.chat_message("assistant"):

        with st.spinner(
            "🧠 Analyzing symptoms..."
        ):

            try:

                final_reply = get_response(
                    st.session_state.messages
                )

            except Exception as e:

                final_reply = (
                    "⚠️ Error generating response."
                )

                print("Backend Error:", e)

        # Typing Animation
        typing_effect(final_reply)

        # Show severity only for important symptoms
        if "chest pain" in user_input.lower():

            st.error("🔴 Critical Severity")

        elif "breathing" in user_input.lower():

            st.error("🚨 Breathing issue detected")

        elif "fever" in user_input.lower():

            st.warning("🟠 Moderate Severity")

    # Store Assistant Message
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_reply
    })

# ---------------- FOOTER ----------------

st.markdown("---")

st.caption(
    "🏥 MediCare AI | Smart Healthcare Chatbot"
)

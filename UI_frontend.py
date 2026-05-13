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

/* Smooth Scroll */
html {
    scroll-behavior: smooth;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    border: none;
    padding: 8px 12px;
    font-weight: 600;
    font-size: 14px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white;
}

/* Compact Symptom Cards */
.symptom-card {
    background: linear-gradient(135deg, #ffffff, #edf4ff);
    padding: 12px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #dbeafe;
    margin-bottom: 8px;
}

/* Smaller Emoji */
.symptom-emoji {
    font-size: 22px;
    margin-bottom: 5px;
}

/* Smaller Text */
.symptom-title {
    font-size: 15px;
    font-weight: 600;
    color: #1e3a8a;
}

.symptom-desc {
    font-size: 11px;
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
- Nearby Hospital Guidance
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

# ---------------- QUICK SYMPTOMS ----------------
st.markdown("""
<h3 style='color:#2563eb;'>
⚡ Quick Symptoms
</h3>
""", unsafe_allow_html=True)

# SINGLE ROW QUICK BUTTONS
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    fever_btn = st.button("🤒 Fever")

with col2:
    cough_btn = st.button("🤧 Cough")

with col3:
    headache_btn = st.button("💊 Headache")

with col4:
    chest_btn = st.button("🫀 Chest Pain")

with col5:
    vomiting_btn = st.button("🤢 Vomiting")

with col6:
    dizziness_btn = st.button("😵 Dizziness")

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
chat_container = st.container()

with chat_container:

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

    # SHOW TEMPERATURE ONLY FOR FEVER
    if "fever" in user_input.lower():

        user_message = f"""
🩺 Symptom: {user_input}

🌡️ Body Temperature: {temperature}°C
"""

    else:

        user_message = f"""
🩺 Symptom: {user_input}
"""

    # USER MESSAGE
    with st.chat_message("user"):

        st.markdown(user_message)

    # STORE USER MESSAGE
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    # EMERGENCY DETECTION
    critical_keywords = [
        "chest pain",
        "heart attack",
        "breathing problem",
        "difficulty breathing"
    ]

    critical_case = any(
        word in user_input.lower()
        for word in critical_keywords
    )

    # SHOW EMERGENCY ALERT
    if critical_case:

        st.error(
            "🚨 Critical Condition Detected!"
        )

        st.warning("""
📞 Emergency Helpline: 108

🏥 Please visit the nearest hospital immediately.
""")

        st.markdown("""
### 🏥 Nearby Healthcare Support

[🔗 Open Google Maps Hospitals Nearby](https://www.google.com/maps/search/hospitals+near+me)
""")

    # ASSISTANT RESPONSE
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

        # FEVER ALERTS
        if "fever" in user_input.lower():

            if temperature > 39:

                st.error("🔴 High Fever Severity")

            elif temperature > 37.5:

                st.warning("🟠 Mild Fever Severity")

            else:

                st.success("🟢 Temperature Looks Normal")

        # CHEST PAIN ALERT
        if "chest pain" in user_input.lower():

            st.error("🚨 Critical Severity")

    # STORE RESPONSE
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_reply
    })

# ---------------- FOOTER ----------------
st.markdown("---")

st.caption(
    "🏥 MediCare AI | Smart Healthcare Chatbot"
)

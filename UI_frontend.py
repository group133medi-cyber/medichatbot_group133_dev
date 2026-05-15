import streamlit as st
import time
from datetime import datetime

# IMPORT BACKEND FUNCTION
from chatbot import get_response

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MediCare AI",
    page_icon="🩺",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# ---------------- CLEAN MEDICAL THEME ----------------
st.markdown("""
<style>

/* APP BACKGROUND */
.stApp {
    background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
}

/* REMOVE STREAMLIT DEFAULTS */
header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* MAIN TITLE */
h1 {
    color: #1e3a8a;
    font-weight: 700;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #dbeafe;
}

/* CHAT MESSAGE */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* USER MESSAGE */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: #dbeafe;
}

/* ASSISTANT MESSAGE */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background: #ffffff;
}

/* BUTTONS */
.stButton > button {
    border-radius: 12px;
    background: #2563eb;
    color: white;
    border: none;
    padding: 10px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    background: #1d4ed8;
    color: white;
}

/* CHAT INPUT */
[data-testid="stChatInput"] {
    border-radius: 16px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🩺 MediCare AI")
st.caption("Smart Healthcare Assistant with AI")

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.markdown("## 🩺 MediCare AI")

    st.info("""
✔ AI Symptom Analysis  
✔ Emergency Detection  
✔ Nearby Healthcare Support  
✔ Smart Chat History
""")

    # ---------------- NEW CHAT ----------------
    if st.button("➕ New Conversation"):

        st.session_state.messages = []

        st.session_state.current_chat = None

        st.rerun()

    st.markdown("---")

    # ---------------- CHAT HISTORY ----------------
    st.markdown("### 💬 Recent Conversations")

    for chat_id, messages in reversed(
        list(st.session_state.chat_sessions.items())
    ):

        if len(messages) > 0:

            first_message = messages[0]["content"]

            preview = (
                first_message[:30] + "..."
                if len(first_message) > 30
                else first_message
            )

            if st.button(preview, key=chat_id):

                st.session_state.current_chat = chat_id

                st.session_state.messages = messages

                st.rerun()

    st.markdown("---")

    # ---------------- TEMPERATURE ----------------
    st.markdown("### 🌡️ Body Temperature")

    temperature = st.slider(
        "Temperature (°C)",
        35.0,
        42.0,
        37.0
    )

    if temperature > 39:

        st.error("🔥 High Fever")

    elif temperature > 37.5:

        st.warning("🟠 Mild Fever")

    else:

        st.success("🟢 Normal")

# ---------------- QUICK SYMPTOMS ----------------
st.markdown("""
<h3 style='color:#2563eb;'>
⚡ Quick Symptoms
</h3>
""", unsafe_allow_html=True)

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

# ---------------- USER INPUT ----------------
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

# ---------------- DISPLAY CHAT ----------------
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
🩺 {user_input}

🌡️ Temperature: {temperature}°C
"""

    else:

        user_message = f"🩺 {user_input}"

    # USER MESSAGE
    with st.chat_message("user"):

        st.markdown(user_message)

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    # ---------------- EMERGENCY DETECTION ----------------
    critical_keywords = [
        "chest pain",
        "heart attack",
        "breathing problem",
        "difficulty breathing",
        "severe pain",
        "unconscious"
    ]

    critical_case = any(
        word in user_input.lower()
        for word in critical_keywords
    )

    # ---------------- EMERGENCY ALERT ----------------
    if critical_case:

        st.error("🚨 Critical Condition Detected")

        st.warning("""
📞 Emergency Helpline: 108

🏥 Please visit the nearest healthcare center immediately.
""")

        st.markdown("""
### 🏥 Nearby Healthcare Support

🔗 [Find Nearby Hospitals](https://www.google.com/maps/search/hospitals+near+me)

🔗 [Find Nearby Emergency Clinics](https://www.google.com/maps/search/emergency+clinic+near+me)

🔗 [Find Nearby Medical Shops](https://www.google.com/maps/search/medical+shop+near+me)
""")

    # ---------------- AI RESPONSE ----------------
    with st.chat_message("assistant"):

        with st.spinner("🧠 Analyzing symptoms..."):

            try:

                final_reply = get_response(
                    st.session_state.messages
                )

            except Exception as e:

                final_reply = (
                    "⚠️ Unable to generate response."
                )

                print("Backend Error:", e)

        # TYPING EFFECT
        typing_effect(final_reply)

        # FEVER ALERTS
        if "fever" in user_input.lower():

            if temperature > 39:

                st.error("🔴 High Fever Severity")

            elif temperature > 37.5:

                st.warning("🟠 Mild Fever Severity")

            else:

                st.success("🟢 Temperature Normal")

        # CHEST PAIN ALERT
        if "chest pain" in user_input.lower():

            st.error("🚨 Emergency Severity")

    # STORE ASSISTANT RESPONSE
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_reply
    })

    # ---------------- SAVE CHAT ----------------
    if st.session_state.current_chat is None:

        chat_id = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        st.session_state.current_chat = chat_id

    st.session_state.chat_sessions[
        st.session_state.current_chat
    ] = st.session_state.messages

# ---------------- FOOTER ----------------
st.markdown("---")

st.caption(
    "🏥 MediCare AI • AI Healthcare Assistant"
)

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

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background-image: url("https://images.unsplash.com/photo-1584982751601-97dcc096659c");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* WHITE OVERLAY */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255,255,255,0.82);
    z-index: -1;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(219,234,254,0.75);
    backdrop-filter: blur(10px);
}

/* CHAT MESSAGES */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #dbeafe;
}

/* BUTTONS */
.stButton > button {
    border-radius: 12px;
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

/* CHAT INPUT */
[data-testid="stChatInput"] {
    border-radius: 15px;
}

/* TITLE */
h1 {
    color: #1e3a8a;
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
- Chat History
- Medical Theme UI
""")

    st.warning("⚠️ Educational use only")

    # ---------------- NEW CHAT ----------------
    if st.button("➕ New Chat"):

        new_chat_name = f"Chat {len(st.session_state.chat_history) + 1}"

        st.session_state.chat_history[new_chat_name] = []

        st.session_state.current_chat = new_chat_name

        st.session_state.messages = []

        st.rerun()

    st.subheader("💬 Chat History")

    # ---------------- CHAT HISTORY ----------------
    for chat_name in st.session_state.chat_history.keys():

        if st.button(chat_name):

            st.session_state.current_chat = chat_name

            st.session_state.messages = st.session_state.chat_history[chat_name]

            st.rerun()

    # ---------------- TEMPERATURE ----------------
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

    # ---------------- RESET ----------------
    if st.button("🗑️ Clear Current Chat"):

        st.session_state.messages = []

        st.session_state.chat_history[
            st.session_state.current_chat
        ] = []

        st.rerun()

# ---------------- QUICK SYMPTOMS ----------------
st.markdown("""
<h3 style='color:#2563eb;'>
⚡ Quick Symptoms
</h3>
""", unsafe_allow_html=True)

# QUICK BUTTONS
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

    # USER CHAT
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

    # EMERGENCY ALERT
    if critical_case:

        st.error(
            "🚨 Critical Condition Detected!"
        )

        st.warning("""
📞 Emergency Helpline: 108

🏥 Please visit nearest hospital immediately.
""")

        st.markdown("""
### 🏥 Nearby Hospitals

[🔗 Open Google Maps Hospitals Nearby](https://www.google.com/maps/search/hospitals+near+me)
""")

    # ---------------- ASSISTANT ----------------
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

        # TYPING EFFECT
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

    # STORE ASSISTANT RESPONSE
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_reply
    })

    # SAVE CHAT HISTORY
    st.session_state.chat_history[
        st.session_state.current_chat
    ] = st.session_state.messages

# ---------------- FOOTER ----------------
st.markdown("---")

st.caption(
    "🏥 MediCare AI | Smart Healthcare Chatbot"
)

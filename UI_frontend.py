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

/* Main background */
.stApp {
    background-color: #f5f9ff;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #e8f0ff;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background-color: #4f8bf9;
    color: white;
    border: none;
    padding: 8px 15px;
}

.stButton>button:hover {
    background-color: #2563eb;
    color: white;
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
This AI chatbot provides:
- Symptom analysis
- Severity detection
- Medical suggestions
- Follow-up questions
""")

    st.warning("⚠️ Not a real medical diagnosis")

    # Reset button
    if st.button("🗑️ Reset Chat"):

        st.session_state.messages = []
        st.rerun()

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- QUICK SYMPTOM BUTTONS ----------------
st.subheader("⚡ Quick Symptoms")

col1, col2, col3 = st.columns(3)

with col1:
    fever_btn = st.button("🤒 Fever")

with col2:
    cough_btn = st.button("🤧 Cough")

with col3:
    headache_btn = st.button("💊 Headache")

# Assign quick input
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

# If typed input exists, override quick button
if chat_input:
    user_input = chat_input

# ---------------- PROCESS ----------------
if user_input:

    # ---------------- SHOW USER MESSAGE ----------------
    with st.chat_message("user"):

        st.markdown(f"👤 {user_input}")

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": f"👤 {user_input}"
    })

    # ---------------- EMERGENCY WARNING ----------------
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

    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_reply
    })

# ---------------- FOOTER ----------------
st.markdown("---")

st.caption("🏥 MediCare AI | Smart Healthcare Chatbot")

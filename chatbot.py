import json
import os
import random
import streamlit as st
from huggingface_hub import InferenceClient

# ---------------- HUGGING FACE CLIENT ----------------

client = InferenceClient(
    api_key=st.secrets["HF_TOKEN"]
)

MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct:fastest"

# ---------------- LOAD MEDICAL DATA ----------------

base_path = os.path.dirname(__file__)

json_path = os.path.join(
    base_path,
    "medical_data.json"
)

with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# ---------------- MAIN CHATBOT FUNCTION ----------------

def get_response(history):

    # Combine recent user messages
    recent_text = " ".join(
        [
            h["content"]
            for h in history
            if isinstance(h, dict)
            and h.get("role") == "user"
        ]
    )

    msg = recent_text.lower()

    matched = []

    # ---------------- SYMPTOM MATCHING ----------------

    for symptom, info in data.items():

        for keyword in info.get("keywords", []):

            if keyword.lower() in msg:

                matched.append(info)

                break

    # ---------------- AI FALLBACK ----------------

    if not matched:

        return get_ai_response(history)

    # ---------------- EMERGENCY DETECTION ----------------

    for m in matched:

        if m.get("severity") == "high":

            return (
                f"⚠️ {m['description']}\n\n"
                f"👉 {m['advice']}\n\n"
                f"Please seek immediate medical attention."
            )

    # ---------------- NORMAL RESPONSE ----------------

    reply = "Based on your symptoms so far:\n\n"

    for m in matched:

        reply += f"• {m['description']}\n"

        reply += f"Advice: {m['advice']}\n\n"

    # ---------------- FOLLOW-UP QUESTIONS ----------------

    follow_ups = []

    for m in matched:

        if "follow_up" in m:

            follow_ups.extend(m["follow_up"])

    if follow_ups:

        reply += "❓ " + random.choice(follow_ups)

    return reply.strip()

# ---------------- HUGGING FACE AI RESPONSE ----------------

def get_ai_response(history):

    try:

        completion = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical assistant. "
                        "Provide general health information only. "
                        "Do not give diagnoses or prescriptions. "
                        "If symptoms are serious, advise consulting a doctor."
                    )
                }
            ] + history[-6:]
        )

        return completion.choices[0].message.content

    except Exception as e:

        print("API Error:", e)

        return (
            "Sorry, I'm having trouble responding right now. "
            "Please try again."
        )

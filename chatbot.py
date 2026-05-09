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

    total_score = 0

    emergency_detected = False

    possible_conditions = []

    # ---------------- SYMPTOM MATCHING ----------------

    for symptom, info in data.items():

        for keyword in info.get("keywords", []):

            if keyword.lower() in msg:

                matched.append(info)

                total_score += info.get("score", 0)

                if info.get("emergency"):

                    emergency_detected = True

                possible_conditions.extend(
                    info.get("possible_conditions", [])
                )

                break

    # ---------------- AI FALLBACK ----------------

    if not matched:

        return get_ai_response(history)

    # ---------------- DETERMINE SEVERITY ----------------

    if total_score >= 8:

        overall_severity = "🔴 Critical"

    elif total_score >= 4:

        overall_severity = "🟠 Moderate"

    else:

        overall_severity = "🟢 Mild"

    # ---------------- EMERGENCY RESPONSE ----------------

    if emergency_detected:

        emergency_replies = []

        for m in matched:

            if m.get("emergency"):

                emergency_replies.append(
                    f"⚠️ {m['description']}\n"
                    f"👉 {m['advice']}"
                )

        return (
            "🚨 EMERGENCY SYMPTOMS DETECTED\n\n"
            + "\n\n".join(emergency_replies)
            + "\n\nPlease seek immediate medical attention."
        )

    # ---------------- BUILD RESPONSE ----------------

    reply = f"📊 Overall Severity: {overall_severity}\n\n"

    reply += "Based on your symptoms:\n\n"

    for m in matched:

        reply += f"• {m['description']}\n"

        reply += f"👉 Advice: {m['advice']}\n\n"

    # ---------------- POSSIBLE CONDITIONS ----------------

    unique_conditions = list(set(possible_conditions))

    if unique_conditions:

        reply += "🧠 Possible Related Conditions:\n"

        for condition in unique_conditions[:5]:

            reply += f"• {condition}\n"

        reply += "\n"

    # ---------------- FOLLOW-UP QUESTIONS ----------------

    follow_ups = []

    for m in matched:

        if "follow_up" in m:

            follow_ups.extend(m["follow_up"])

    if follow_ups:

        reply += "❓ Follow-up Question:\n"

        reply += random.choice(follow_ups)

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
                        "You are an AI medical assistant chatbot.\n\n"

                        "Your responsibilities:\n"
                        "- Provide general medical guidance\n"
                        "- Ask relevant follow-up questions\n"
                        "- Explain symptoms clearly\n"
                        "- Encourage professional consultation when needed\n"
                        "- Never provide prescriptions\n"
                        "- Never claim certainty in diagnosis\n"
                        "- Keep responses concise and easy to understand\n"
                        "- If symptoms appear severe or emergency-related, "
                        "advise immediate medical attention."
                    )
                }
            ] + history[-10:]
        )

        return completion.choices[0].message.content

    except Exception as e:

        print("API Error:", e)

        return (
            "Sorry, I'm having trouble responding right now. "
            "Please try again."
        )

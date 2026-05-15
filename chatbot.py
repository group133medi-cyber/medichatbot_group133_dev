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

# ---------------- LOAD DATA ----------------

base_path = os.path.dirname(__file__)

json_path = os.path.join(
    base_path,
    "medical_data.json"
)

with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# ---------------- SESSION MEMORY ----------------

if "symptom_memory" not in st.session_state:
    st.session_state.symptom_memory = []

if "pending_followup" not in st.session_state:
    st.session_state.pending_followup = None

if "followup_answers" not in st.session_state:
    st.session_state.followup_answers = {}

# ---------------- MAIN RESPONSE FUNCTION ----------------

def get_response(history):

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

    combo_matches = []

    total_score = 0

    emergency_detected = False

    condition_scores = {}

    # ---------------- HANDLE FOLLOW-UP ANSWER ----------------

    if st.session_state.pending_followup:

        question_data = st.session_state.pending_followup

        st.session_state.followup_answers[
            question_data["question"]
        ] = msg

        for answer_rule in question_data.get(
            "expected_answers", []
        ):

            if answer_rule["value"].lower() in msg:

                total_score += answer_rule.get(
                    "severity_increase", 0
                )

                if answer_rule.get("emergency"):
                    emergency_detected = True

        st.session_state.pending_followup = None

    # ---------------- SYMPTOM MATCHING ----------------

    for symptom, info in data["symptoms"].items():

        for keyword in info.get("keywords", []):

            if keyword.lower() in msg:

                matched.append(info)

                total_score += info.get(
                    "base_score", 0
                )

                if info.get("emergency"):
                    emergency_detected = True

                # SAVE SYMPTOM MEMORY
                if symptom not in st.session_state.symptom_memory:

                    st.session_state.symptom_memory.append(
                        symptom
                    )

                # CONDITION WEIGHTS
                for condition in info.get(
                    "possible_conditions", []
                ):

                    name = condition["name"]

                    weight = condition["weight"]

                    condition_scores[name] = (
                        condition_scores.get(name, 0)
                        + weight
                    )

                break

    # ---------------- COMBINATION ANALYSIS ----------------

    memory = set(
        st.session_state.symptom_memory
    )

    for combo in data.get(
        "symptom_combinations", []
    ):

        combo_symptoms = set(
            combo["symptoms"]
        )

        if combo_symptoms.issubset(memory):

            combo_matches.append(combo)

            total_score += combo.get(
                "score_bonus", 0
            )

            if combo.get("emergency"):

                emergency_detected = True

            for condition in combo.get(
                "possible_conditions", []
            ):

                name = condition["name"]

                weight = condition["weight"]

                condition_scores[name] = (
                    condition_scores.get(name, 0)
                    + weight
                )

    # ---------------- AI FALLBACK ----------------

    if not matched and not combo_matches:

        return get_ai_response(history)

    # ---------------- DETERMINE SEVERITY ----------------

    if emergency_detected or total_score >= 10:

        overall_severity = "🔴 Critical"

    elif total_score >= 5:

        overall_severity = "🟠 Moderate"

    else:

        overall_severity = "🟢 Mild"

    # ---------------- EMERGENCY RESPONSE ----------------

    if emergency_detected:

        reply = (
            "🚨 Emergency symptoms detected.\n\n"
        )

        reply += (
            "Please seek immediate medical attention.\n\n"
        )

        for m in matched:

            if m.get("emergency"):

                reply += (
                    f"⚠️ {m['description']}\n"
                )

                reply += (
                    f"👉 {m['advice']}\n\n"
                )

        return reply.strip()

    # ---------------- BUILD RESPONSE ----------------

    reply = (
        f"📊 Overall Severity: "
        f"{overall_severity}\n\n"
    )

    reply += "🩺 Detected Symptoms:\n\n"

    for m in matched:

        reply += (
            f"• {m['description']}\n"
        )

        reply += (
            f"👉 Advice: {m['advice']}\n\n"
        )

    # ---------------- TOP CONDITIONS ----------------

    if condition_scores:

        sorted_conditions = sorted(
            condition_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        reply += (
            "🧠 Possible Related Conditions:\n\n"
        )

        for condition, score in sorted_conditions[:5]:

            confidence = round(score * 100)

            reply += (
                f"• {condition.replace('_', ' ').title()}"
                f" ({confidence}% match)\n"
            )

        reply += "\n"

    # ---------------- COMBINATION OUTPUT ----------------

    if combo_matches:

        reply += (
            "🔍 Symptom Combination Analysis:\n\n"
        )

        for combo in combo_matches:

            reply += (
                f"• Combination detected: "
                f"{', '.join(combo['symptoms'])}\n"
            )

            reply += (
                f"👉 {combo['advice']}\n\n"
            )

    # ---------------- FOLLOW-UP ENGINE ----------------

    followup_candidates = []

    for symptom, info in data["symptoms"].items():

        if symptom in st.session_state.symptom_memory:

            followup_candidates.extend(
                info.get("follow_up_flow", [])
            )

    if followup_candidates:

        selected_question = random.choice(
            followup_candidates
        )

        st.session_state.pending_followup = (
            selected_question
        )

        reply += (
            "❓ Follow-up Question:\n\n"
        )

        reply += (
            selected_question["question"]
        )

    return reply.strip()

# ---------------- AI FALLBACK ----------------

def get_ai_response(history):

    try:

        completion = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI medical assistant.\n\n"

                        "Responsibilities:\n"
                        "- Provide general medical guidance\n"
                        "- Ask smart follow-up questions\n"
                        "- Explain symptoms clearly\n"
                        "- Never provide prescriptions\n"
                        "- Never claim certainty in diagnosis\n"
                        "- Recommend professional care when needed\n"
                        "- If symptoms appear severe, "
                        "recommend emergency care."
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

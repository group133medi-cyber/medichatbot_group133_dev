import json
import os
import streamlit as st
from huggingface_hub import InferenceClient

# =========================================================
# HUGGING FACE CLIENT
# =========================================================

client = InferenceClient(
    api_key=st.secrets["HF_TOKEN"]
)

MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct:fastest"

# =========================================================
# LOAD MEDICAL DATA
# =========================================================

base_path = os.path.dirname(__file__)

json_path = os.path.join(
    base_path,
    "medical_data.json"
)

with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# =========================================================
# SESSION MEMORY
# =========================================================

if "symptom_memory" not in st.session_state:
    st.session_state.symptom_memory = []

if "asked_followups" not in st.session_state:
    st.session_state.asked_followups = []

if "current_followup" not in st.session_state:
    st.session_state.current_followup = None

if "followup_answers" not in st.session_state:
    st.session_state.followup_answers = {}

if "condition_scores" not in st.session_state:
    st.session_state.condition_scores = {}

# NEW: persistent severity score
if "total_score" not in st.session_state:
    st.session_state.total_score = 0

# =========================================================
# MAIN CHATBOT FUNCTION
# =========================================================

def get_response(history):

    # -----------------------------------------------------
    # LATEST USER MESSAGE
    # -----------------------------------------------------

    msg = history[-1]["content"].lower().strip()

    matched = []

    combo_matches = []

    emergency_detected = False

    # =====================================================
    # FOLLOW-UP ANSWER ANALYSIS
    # =====================================================

    if st.session_state.current_followup:

        flow = st.session_state.current_followup

        question_id = flow.get("id")

        st.session_state.followup_answers[
            question_id
        ] = msg

        # -------------------------------------------------
        # OLD RULE SYSTEM
        # -------------------------------------------------

        for rule in flow.get("rules", []):

            for keyword in rule.get("keywords", []):

                if keyword.lower() in msg:

                    st.session_state.total_score += rule.get(
                        "increase_score",
                        0
                    )

                    if rule.get("emergency"):
                        emergency_detected = True

        # -------------------------------------------------
        # NEW SEVERITY RULE SYSTEM
        # -------------------------------------------------

        user_input = msg.strip().lower()

        for rule in flow.get("severity_rules", []):

            condition = rule.get("condition", "")
            score_change = rule.get(
                "score_change",
                0
            )

            matched_rule = False

            # BOOLEAN YES/NO

            if (
                condition == "yes"
                and "yes" in user_input
            ):
                matched_rule = True

            # >=

            elif condition.startswith(">="):

                try:

                    value = float(user_input)

                    limit = float(
                        condition.replace(">=", "").strip()
                    )

                    if value >= limit:
                        matched_rule = True

                except:
                    pass

            # <=

            elif condition.startswith("<="):

                try:

                    value = float(user_input)

                    limit = float(
                        condition.replace("<=", "").strip()
                    )

                    if value <= limit:
                        matched_rule = True

                except:
                    pass

            # >

            elif condition.startswith(">"):

                try:

                    value = float(user_input)

                    limit = float(
                        condition.replace(">", "").strip()
                    )

                    if value > limit:
                        matched_rule = True

                except:
                    pass

            # <

            elif condition.startswith("<"):

                try:

                    value = float(user_input)

                    limit = float(
                        condition.replace("<", "").strip()
                    )

                    if value < limit:
                        matched_rule = True

                except:
                    pass

            # APPLY RULE

            if matched_rule:

                st.session_state.total_score += score_change

                if rule.get("emergency"):
                    emergency_detected = True

        # CLEAR ACTIVE FOLLOW-UP

        st.session_state.current_followup = None

    # =====================================================
    # SYMPTOM MATCHING
    # =====================================================

    for symptom, info in data["symptoms"].items():

        for keyword in info.get("keywords", []):

            if keyword.lower() in msg:

                # avoid duplicate matches

                already_exists = any(
                    m["name"] == symptom
                    for m in matched
                )

                if not already_exists:

                    matched.append({
                        "name": symptom,
                        "info": info
                    })

                    st.session_state.total_score += info.get(
                        "score",
                        0
                    )

                    if info.get("emergency"):
                        emergency_detected = True

                    # SAVE SYMPTOM MEMORY

                    if (
                        symptom
                        not in st.session_state.symptom_memory
                    ):

                        st.session_state.symptom_memory.append(
                            symptom
                        )

                    # CONDITION SCORING

                    for condition in info.get(
                        "possible_conditions",
                        []
                    ):

                        st.session_state.condition_scores[
                            condition
                        ] = (
                            st.session_state.condition_scores.get(
                                condition,
                                0
                            ) + 1
                        )

                break

    # =====================================================
    # SYMPTOM COMBINATION ANALYSIS
    # =====================================================

    memory = set(
        st.session_state.symptom_memory
    )

    for combo in data.get(
        "symptom_combinations",
        []
    ):

        combo_set = set(combo["symptoms"])

        if combo_set.issubset(memory):

            combo_matches.append(combo)

            st.session_state.total_score += combo.get(
                "score_bonus",
                0
            )

            if combo.get("emergency"):
                emergency_detected = True

            condition = combo.get("condition")

            if condition:

                st.session_state.condition_scores[
                    condition
                ] = (
                    st.session_state.condition_scores.get(
                        condition,
                        0
                    ) + 2
                )

    # =====================================================
    # AI FALLBACK
    # =====================================================

    if not matched and not combo_matches:

        return get_ai_response(history)

    # =====================================================
    # DETERMINE SEVERITY
    # =====================================================

    if (
        emergency_detected
        or st.session_state.total_score >= 10
    ):

        overall_severity = "🔴 Critical"

    elif st.session_state.total_score >= 5:

        overall_severity = "🟠 Moderate"

    else:

        overall_severity = "🟢 Mild"

    # =====================================================
    # EMERGENCY RESPONSE
    # =====================================================

    if emergency_detected:

        emergency_reply = (
            "🚨 EMERGENCY SYMPTOMS DETECTED\n\n"
        )

        emergency_reply += (
            "Please seek immediate medical attention.\n\n"
        )

        for m in matched:

            info = m["info"]

            if info.get("emergency"):

                emergency_reply += (
                    f"⚠️ {info['description']}\n"
                )

                emergency_reply += (
                    f"👉 {info['advice']}\n\n"
                )

        for combo in combo_matches:

            if combo.get("emergency"):

                emergency_reply += (
                    f"🧠 {combo['condition']}\n"
                )

                emergency_reply += (
                    f"👉 {combo['advice']}\n\n"
                )

        return emergency_reply.strip()

    # =====================================================
    # BUILD RESPONSE
    # =====================================================

    reply = (
        f"📊 Overall Severity: "
        f"{overall_severity}\n\n"
    )

    # -----------------------------------------------------
    # DETECTED SYMPTOMS
    # -----------------------------------------------------

    if matched:

        reply += "🩺 Detected Symptoms:\n\n"

        for m in matched:

            info = m["info"]

            reply += (
                f"• {info['description']}\n"
            )

            reply += (
                f"👉 Advice: {info['advice']}\n\n"
            )

    # -----------------------------------------------------
    # POSSIBLE CONDITIONS
    # -----------------------------------------------------

    if st.session_state.condition_scores:

        reply += (
            "🧠 Possible Related Conditions:\n\n"
        )

        sorted_conditions = sorted(
            st.session_state.condition_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for condition, score in sorted_conditions[:5]:

            confidence = min(
                95,
                score * 20
            )

            reply += (
                f"• {condition}"
                f" ({confidence}% match)\n"
            )

        reply += "\n"

    # -----------------------------------------------------
    # COMBINATION ANALYSIS
    # -----------------------------------------------------

    if combo_matches:

        reply += (
            "🔍 Symptom Combination Analysis:\n\n"
        )

        for combo in combo_matches:

            reply += (
                f"🧠 {combo['condition']}\n"
            )

            reply += (
                f"👉 {combo['advice']}\n\n"
            )

    # =====================================================
    # SMART FOLLOW-UP ENGINE
    # =====================================================

    next_question = None

    for m in matched:

        info = m["info"]

        followups = info.get(
            "follow_up_flow",
            []
        )

        for flow in followups:

            if (
                flow["id"]
                not in st.session_state.asked_followups
            ):

                next_question = flow

                st.session_state.asked_followups.append(
                    flow["id"]
                )

                break

        if next_question:
            break

    # =====================================================
    # ASK FOLLOW-UP QUESTION
    # =====================================================

    if next_question:

        st.session_state.current_followup = (
            next_question
        )

        reply += (
            "❓ Follow-up Question:\n\n"
        )

        reply += (
            next_question["question"]
        )

    return reply.strip()

# =========================================================
# AI FALLBACK
# =========================================================

def get_ai_response(history):

    try:

        completion = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI medical assistant chatbot.\n\n"

                        "Responsibilities:\n"
                        "- Provide general medical guidance\n"
                        "- Ask intelligent follow-up questions\n"
                        "- Explain symptoms clearly\n"
                        "- Never provide prescriptions\n"
                        "- Never claim certainty in diagnosis\n"
                        "- Recommend doctor consultation when needed\n"
                        "- Recommend emergency care for severe symptoms."
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

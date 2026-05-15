import json
import random
import os

INPUT_FILE = "medical_data.json"
BACKUP_FILE = "medical_data_backup.json"


def load_dataset():
    with open(INPUT_FILE, "r") as f:
        return json.load(f)


def save_dataset(data):
    with open(INPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def backup_original():
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r") as f:
            original = json.load(f)

        with open(BACKUP_FILE, "w") as f:
            json.dump(original, f, indent=2)


def build_follow_up(symptom_name, severity):
    """Create intelligent follow-up flow based on severity"""

    base_flow = [
        {
            "question_id": f"{symptom_name}_duration",
            "question": f"How many days have you had {symptom_name.replace('_', ' ')}?",
            "type": "number",
            "importance": "high",
            "rules": [
                {
                    "operator": ">",
                    "value": 7,
                    "effect": {"increase_score": 2}
                },
                {
                    "operator": ">",
                    "value": 14,
                    "effect": {"increase_score": 3}
                }
            ]
        },
        {
            "question_id": f"{symptom_name}_worsening",
            "question": f"Is your {symptom_name.replace('_', ' ')} getting worse?",
            "type": "boolean",
            "importance": "medium",
            "rules": [
                {
                    "operator": "==",
                    "value": True,
                    "effect": {"increase_score": 2}
                }
            ]
        }
    ]

    # Add severity-specific intelligence
    if severity in ["high", "critical"]:
        base_flow.append({
            "question_id": f"{symptom_name}_redflag",
            "question": "Are you experiencing sudden severe worsening or new symptoms?",
            "type": "boolean",
            "importance": "critical",
            "rules": [
                {
                    "operator": "==",
                    "value": True,
                    "effect": {
                        "set_emergency": True,
                        "increase_score": 5
                    }
                }
            ]
        })

    return base_flow


def enhance_symptom(symptom_name, symptom_data):
    """Inject follow-up intelligence into existing symptom"""

    severity = symptom_data.get("severity", "low")
    existing_flow = symptom_data.get("follow_up_flow", [])

    # If missing OR too weak → replace
    if not existing_flow or len(existing_flow) < 2:
        symptom_data["follow_up_flow"] = build_follow_up(symptom_name, severity)
        return symptom_data

    # Otherwise enhance existing flow (inject rules if missing)
    for q in existing_flow:
        if "rules" not in q:
            q["rules"] = [
                {
                    "operator": ">",
                    "value": 7,
                    "effect": {"increase_score": 1}
                }
            ]

    # Add emergency escalation question if needed
    if severity in ["high", "critical"]:
        existing_flow.append({
            "question_id": f"{symptom_name}_emergency_check",
            "question": "Are symptoms suddenly severe or life-threatening?",
            "type": "boolean",
            "importance": "critical",
            "rules": [
                {
                    "operator": "==",
                    "value": True,
                    "effect": {
                        "set_emergency": True,
                        "increase_score": 5
                    }
                }
            ]
        })

    symptom_data["follow_up_flow"] = existing_flow
    return symptom_data


def run_injector():
    print("Loading dataset...")

    data = load_dataset()
    symptoms = data.get("symptoms", {})

    print(f"Total symptoms found: {len(symptoms)}")

    # Backup first (VERY IMPORTANT)
    backup_original()
    print("Backup created → medical_data_backup.json")

    updated_count = 0

    for name, symptom in symptoms.items():
        original_flow = symptom.get("follow_up_flow", None)

        updated_symptom = enhance_symptom(name, symptom)

        if original_flow != updated_symptom.get("follow_up_flow"):
            updated_count += 1

        symptoms[name] = updated_symptom

    data["symptoms"] = symptoms

    save_dataset(data)

    print(f"Follow-up injection completed.")
    print(f"Symptoms enhanced: {updated_count}")
    print(f"Updated dataset saved to: {INPUT_FILE}")


if __name__ == "__main__":
    run_injector()

import json
import random

BODY_SYSTEMS = [
    "respiratory",
    "cardiac",
    "digestive",
    "neurological",
    "musculoskeletal",
    "dermatological",
    "mental_health",
    "general",
    "urinary"
]

SEVERITY_LEVELS = ["low", "moderate", "high", "critical"]

CONDITIONS = {
    "respiratory": ["cold", "flu", "asthma", "pneumonia", "bronchitis", "covid_19"],
    "cardiac": ["heart_attack", "angina", "arrhythmia", "heart_failure"],
    "digestive": ["gastritis", "food_poisoning", "ibs", "gerd"],
    "neurological": ["migraine", "stroke_risk", "tension_headache"],
    "musculoskeletal": ["strain", "arthritis", "injury"],
    "dermatological": ["allergy", "eczema", "skin_infection"],
    "mental_health": ["anxiety_disorder", "depression", "stress"],
    "general": ["viral_infection", "bacterial_infection", "fever_unknown"],
    "urinary": ["uti", "kidney_infection"]
}

SYMPTOM_TEMPLATES = [
    ("fever", "high temperature", "general"),
    ("cough", "coughing", "respiratory"),
    ("shortness_of_breath", "breathlessness", "respiratory"),
    ("chest_pain", "chest discomfort", "cardiac"),
    ("headache", "head pain", "neurological"),
    ("fatigue", "tiredness", "general"),
    ("nausea", "feeling sick", "digestive"),
    ("vomiting", "throwing up", "digestive"),
    ("diarrhea", "loose stools", "digestive"),
    ("sore_throat", "throat pain", "respiratory"),
    ("runny_nose", "nasal discharge", "respiratory"),
    ("nasal_congestion", "blocked nose", "respiratory"),
    ("dizziness", "lightheadedness", "neurological"),
    ("joint_pain", "joint pain", "musculoskeletal"),
    ("back_pain", "back pain", "musculoskeletal"),
    ("abdominal_pain", "stomach pain", "digestive"),
    ("heartburn", "acid reflux", "digestive"),
    ("palpitations", "fast heartbeat", "cardiac"),
    ("anxiety", "excess worry", "mental_health"),
    ("depression", "low mood", "mental_health"),
    ("rash", "skin rash", "dermatological"),
    ("itching", "skin itching", "dermatological"),
    ("blurred_vision", "vision blur", "neurological"),
    ("loss_of_appetite", "no appetite", "general"),
    ("weight_loss", "weight loss", "general"),
    ("insomnia", "sleep difficulty", "mental_health")
]


def make_follow_up(symptom):
    """Generate follow-up questions for chatbot logic"""
    return [
        {
            "question_id": f"{symptom}_duration",
            "question": f"How long have you had {symptom.replace('_', ' ')}?",
            "type": "number",
            "importance": "high",
            "rules": [
                {
                    "operator": ">",
                    "value": 7,
                    "effect": {"increase_score": 2}
                }
            ]
        },
        {
            "question_id": f"{symptom}_worsening",
            "question": f"Is your {symptom.replace('_', ' ')} getting worse?",
            "type": "boolean",
            "importance": "medium",
            "rules": [
                {
                    "operator": "==",
                    "value": True,
                    "effect": {"increase_score": 1}
                }
            ]
        }
    ]


def generate_symptom(name, keyword, system):
    severity = random.choice(SEVERITY_LEVELS)

    base_score_map = {
        "low": 1,
        "moderate": 2,
        "high": 4,
        "critical": 5
    }

    base_score = base_score_map[severity]
    emergency = severity == "critical"

    possible_conditions = random.sample(
        CONDITIONS.get(system, ["unknown_condition"]),
        k=min(2, len(CONDITIONS.get(system, ["unknown_condition"])))
    )

    return {
        "keywords": [name, keyword],
        "body_system": system,
        "description": f"{keyword} related symptom affecting {system} system.",
        "severity": severity,
        "base_score": base_score,
        "emergency": emergency,
        "related_symptoms": [],
        "red_flags": ["sudden worsening"] if severity in ["high", "critical"] else [],
        "emergency_triggers": ["duration > 10"] if emergency else [],
        "advice": "Monitor symptoms and seek care if worsening.",
        "possible_conditions": [
            {"name": c, "weight": round(random.uniform(0.5, 0.9), 2)}
            for c in possible_conditions
        ],
        "follow_up_flow": make_follow_up(name)
    }


def generate_dataset(target=50):
    dataset = {"symptoms": {}, "symptom_combinations": []}

    for i in range(target):
        base = SYMPTOM_TEMPLATES[i % len(SYMPTOM_TEMPLATES)]
        name, keyword, system = base

        # ensure uniqueness if extended beyond template size
        if i >= len(SYMPTOM_TEMPLATES):
            name = f"{name}_{i}"

        dataset["symptoms"][name] = generate_symptom(name, keyword, system)

    # Generate symptom combinations
    symptoms = list(dataset["symptoms"].keys())

    for _ in range(10):
        combo = random.sample(symptoms, k=2)

        dataset["symptom_combinations"].append({
            "symptoms": combo,
            "possible_conditions": [
                {"name": "combined_infection", "weight": 0.8}
            ],
            "severity": random.choice(SEVERITY_LEVELS),
            "emergency": False,
            "score_bonus": random.randint(1, 5),
            "recommended_questions": [
                f"{combo[0]}_duration",
                f"{combo[1]}_duration"
            ],
            "advice": "Monitor combined symptoms closely."
        })

    return dataset


if __name__ == "__main__":
    data = generate_dataset(50)

    output_file = "medical_data.json"

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Dataset generated successfully → {output_file}")
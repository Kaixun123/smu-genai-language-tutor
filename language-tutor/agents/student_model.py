import json
import os
from datetime import datetime
from state import TutorState


# Directory to store student profiles
PROFILES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "student_profiles"
)


def student_model_agent(state: TutorState) -> dict:
    """
    Updates the student profile based on the current interaction.
    """
    # Make a copy so we don't mutate the original
    profile = state["student_profile"].copy()
    errors = state.get("errors", [])
    teaching_strategy = state.get("teaching_strategy", "")
    transfer_type = state.get("transfer_type", "none")

    # Ensure error_history exists
    if "error_history" not in profile:
        profile["error_history"] = {}

    # Ensure interaction_log exists
    if "interaction_log" not in profile:
        profile["interaction_log"] = []

    # ── Update error history ──
    if errors:
        for error in errors:
            error_type = error.get("type", "unknown")

            if error_type not in profile["error_history"]:
                profile["error_history"][error_type] = {
                    "encounters": 0,
                    "correct": 0,
                    "last_seen": None
                }

            profile["error_history"][error_type]["encounters"] += 1
            profile["error_history"][error_type]["last_seen"] = (
                datetime.now().isoformat()
            )
    else:
        # No errors = student got it right
        # If we know what skill was tested, mark it as correct
        # (This would come from the exercise metadata)
        pass

    # ── Log this interaction ──
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "exercise": state.get("exercise_prompt", ""),
        "student_input": state.get("student_input", ""),
        "errors_count": len(errors),
        "error_types": [e.get("type", "unknown") for e in errors],
        "teaching_strategy": teaching_strategy,
        "transfer_type": transfer_type
    }
    profile["interaction_log"].append(interaction)

    # ── Save to file ──
    save_student_profile(profile)

    return {"student_profile": profile}


def save_student_profile(profile: dict):
    """Saves the student profile to a JSON file."""
    os.makedirs(PROFILES_DIR, exist_ok=True)

    # Use student name as filename (sanitized)
    name = profile.get("name", "unknown_student")
    safe_name = name.lower().replace(" ", "_")
    filepath = os.path.join(PROFILES_DIR, f"{safe_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def load_student_profile(student_name: str) -> dict:
    """
    Loads a student profile from file.
    Call this at the start of a session.
    """
    safe_name = student_name.lower().replace(" ", "_")
    filepath = os.path.join(PROFILES_DIR, f"{safe_name}.json")

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    # Return a default profile if no file exists
    return {
        "name": student_name,
        "known_languages": [],
        "level": "N5",
        "error_history": {},
        "interaction_log": []
    }
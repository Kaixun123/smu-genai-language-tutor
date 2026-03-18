from typing import TypedDict


class TutorState(TypedDict):
    # ── Input ──
    student_input: str          # What the student typed
    exercise_prompt: str        # The exercise given to the student
    correct_answer: str         # The reference correct answer

    # ── Student Profile ──
    student_profile: dict       # Languages known, proficiency, history
    # Example structure:
    # {
    #     "name": "Student A",
    #     "known_languages": ["Mandarin (native)", "English (fluent)"],
    #     "level": "N5",
    #     "error_history": {
    #         "word_order": {"encounters": 2, "correct": 1},
    #         "particle_usage": {"encounters": 3, "correct": 0}
    #     }
    # }

    # ── Diagnostic Agent Output ──
    errors: list                # List of classified errors
    # Each error: {"type": "...", "description": "...",
    #              "incorrect_part": "...", "correct_form": "..."}
    transfer_flags: list        # Which errors might be L1/L2 interference

    # ── Cross-Lingual Agent Output ──
    bridge_explanation: str     # Explanation using student's known languages
    transfer_type: str          # "positive", "negative", or "none"

    # ── Pedagogy Agent Output ──
    encounter_count: int        # Times student has seen this concept
    teaching_strategy: str      # "hint", "scaffold", or "direct"
    final_response: str         # The actual message shown to the student

    # ── Routing ──
    route: str                  # "diagnose" or "generate_content"
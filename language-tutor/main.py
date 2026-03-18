from graph import build_graph
from agents.student_model import load_student_profile


def run_diagnostic_example():
    """
    Example 1: Student submits a translation attempt.
    The system diagnoses errors, finds cross-lingual bridges,
    and responds with an appropriate teaching strategy.
    """
    print("=" * 60)
    print("EXAMPLE 1: Student submits a translation")
    print("=" * 60)

    app = build_graph()

    # Load or create a student profile
    student_profile = {
        "name": "Demo Student A",
        "known_languages": ["Mandarin (native)", "English (fluent)"],
        "level": "N5",
        "error_history": {},
        "interaction_log": []
    }

    # The student tries to translate "I eat an apple every day"
    # but uses SVO word order (wrong for Japanese)
    result = app.invoke({
        "student_input": "毎日私は食べるりんごを",
        "exercise_prompt": "Translate: I eat an apple every day",
        "correct_answer": "毎日私はりんごを食べる",
        "student_profile": student_profile,
        "errors": [],
        "transfer_flags": [],
        "bridge_explanation": "",
        "transfer_type": "",
        "encounter_count": 1,
        "teaching_strategy": "",
        "final_response": "",
        "route": ""
    })

    print(f"\nExercise:  {result['exercise_prompt']}")
    print(f"Student:   {result['student_input']}")
    print(f"Correct:   {result['correct_answer']}")
    print(f"\nErrors found: {len(result['errors'])}")
    for i, error in enumerate(result["errors"]):
        print(f"  Error {i+1}: [{error.get('type')}] {error.get('description')}")
    print(f"\nTransfer type: {result['transfer_type']}")
    print(f"Strategy: {result['teaching_strategy']}")
    print(f"\n--- Tutor Response ---")
    print(result["final_response"])
    print()


def run_content_generation_example():
    """
    Example 2: Student needs a new exercise.
    The system generates one based on their weak points.
    """
    print("=" * 60)
    print("EXAMPLE 2: Generate new exercise")
    print("=" * 60)

    app = build_graph()

    # Student with some history — struggles with particles
    student_profile = {
        "name": "Demo Student B",
        "known_languages": ["English (native)", "Mandarin (conversational)"],
        "level": "N5",
        "error_history": {
            "particle": {"encounters": 5, "correct": 1, "last_seen": None},
            "word_order": {"encounters": 2, "correct": 1, "last_seen": None}
        },
        "interaction_log": []
    }

    # Empty student_input triggers content generation
    result = app.invoke({
        "student_input": "",
        "exercise_prompt": "",
        "correct_answer": "",
        "student_profile": student_profile,
        "errors": [],
        "transfer_flags": [],
        "bridge_explanation": "",
        "transfer_type": "",
        "encounter_count": 0,
        "teaching_strategy": "",
        "final_response": "",
        "route": ""
    })

    print(f"\n--- Generated Exercise ---")
    print(result["final_response"])
    print()


def run_interactive():
    """
    Interactive mode: chat with the tutor in a loop.
    """
    print("=" * 60)
    print("INTERACTIVE MODE: Japanese Language Tutor")
    print("Type 'quit' to exit, 'new' for a new exercise")
    print("=" * 60)

    app = build_graph()

    # Start with a default student profile
    student_profile = {
        "name": "Interactive Student",
        "known_languages": ["Mandarin (native)", "English (fluent)"],
        "level": "N5",
        "error_history": {},
        "interaction_log": []
    }

    current_exercise = ""
    current_answer = ""

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye! Keep practicing!")
            break

        # If "new" or no current exercise, generate one
        if user_input.lower() == "new" or not current_exercise:
            result = app.invoke({
                "student_input": "",
                "exercise_prompt": "",
                "correct_answer": "",
                "student_profile": student_profile,
                "errors": [],
                "transfer_flags": [],
                "bridge_explanation": "",
                "transfer_type": "",
                "encounter_count": 0,
                "teaching_strategy": "",
                "final_response": "",
                "route": ""
            })
            current_exercise = result.get("exercise_prompt", "")
            current_answer = result.get("correct_answer", "")
            print(f"\nTutor: {result['final_response']}")
            continue

        # Student submitted an answer — diagnose it
        result = app.invoke({
            "student_input": user_input,
            "exercise_prompt": current_exercise,
            "correct_answer": current_answer,
            "student_profile": student_profile,
            "errors": [],
            "transfer_flags": [],
            "bridge_explanation": "",
            "transfer_type": "",
            "encounter_count": 0,
            "teaching_strategy": "",
            "final_response": "",
            "route": ""
        })

        # Update profile for next round
        student_profile = result.get("student_profile", student_profile)

        print(f"\nTutor: {result['final_response']}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive()
    else:
        # Run examples
        run_diagnostic_example()
        print("\n" + "─" * 60 + "\n")
        run_content_generation_example()
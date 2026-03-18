import json
from state import TutorState
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def get_weak_points(student_profile: dict) -> list:
    """
    Analyzes the student's error history to find their
    weakest areas (most errors, lowest accuracy).
    """
    error_history = student_profile.get("error_history", {})

    if not error_history:
        # New student — return general beginner topics
        return ["basic_grammar", "self_introduction", "common_vocabulary"]

    # Sort error types by encounter count (most struggled = highest)
    weak_areas = sorted(
        error_history.items(),
        key=lambda x: x[1]["encounters"] - x[1]["correct"],
        reverse=True
    )

    # Return top 3 weakest areas
    return [area[0] for area in weak_areas[:3]]


def content_generator(state: TutorState) -> dict:
    """
    Generates a new exercise targeting the student's weak points.
    """
    student_profile = state["student_profile"]
    known_languages = student_profile.get("known_languages", [])
    level = student_profile.get("level", "N5")
    weak_points = get_weak_points(student_profile)

    prompt = f"""You are a Japanese language exercise generator.

Student profile:
- JLPT level: {level}
- Known languages: {known_languages}
- Weak areas: {weak_points}

Generate ONE translation exercise that:
1. Targets the student's weakest area: {weak_points[0] if weak_points else 'basic grammar'}
2. Is appropriate for JLPT {level}
3. Uses natural, everyday sentences (not textbook-dry)
4. Is an English sentence the student must translate to Japanese

Return ONLY a JSON object with:
- "exercise_prompt": the English sentence to translate
- "correct_answer": the correct Japanese translation (in mixed kanji/hiragana)
- "target_skill": which skill this tests
- "difficulty_note": brief note on what makes this challenging

Return ONLY valid JSON."""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback exercise
        result = {
            "exercise_prompt": "Translate: I eat rice every morning.",
            "correct_answer": "毎朝ご飯を食べます。",
            "target_skill": "basic_grammar",
            "difficulty_note": "Tests SOV word order and particle usage"
        }

    return {
        "exercise_prompt": result.get("exercise_prompt", ""),
        "correct_answer": result.get("correct_answer", ""),
        "final_response": (
            f"Here's your next exercise:\n\n"
            f"**Translate to Japanese:**\n"
            f"{result.get('exercise_prompt', '')}\n\n"
            f"(Skill focus: {result.get('target_skill', 'general')})"
        )
    }
import json
import os
from state import TutorState
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def load_transfer_map() -> str:
    """
    Loads the language transfer maps from JSON files.
    These are handcrafted knowledge bases of known patterns
    between language pairs.
    """
    transfer_data = {}
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "transfer_maps")

    for filename in ["mandarin_to_japanese.json", "english_to_japanese.json"]:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                transfer_data[filename] = json.load(f)

    return json.dumps(transfer_data, indent=2, ensure_ascii=False)


def cross_lingual_agent(state: TutorState) -> dict:
    """
    Uses the student's known languages to craft bridge explanations.
    Checks the transfer map first, then uses LLM for nuanced explanation.
    """
    errors = state.get("errors", [])
    transfer_flags = state.get("transfer_flags", [])

    # If no errors, no bridging needed
    if not errors:
        return {
            "bridge_explanation": "No errors to bridge.",
            "transfer_type": "none"
        }

    # Load the transfer map
    transfer_map = load_transfer_map()

    student_profile = state["student_profile"]
    known_languages = student_profile.get("known_languages", [])

    prompt = f"""You are a cross-lingual transfer specialist who helps
Japanese language learners by connecting new concepts to languages
they already know.

Student's known languages: {known_languages}
Errors detected: {json.dumps(errors, ensure_ascii=False)}
Transfer flags from diagnostic: {json.dumps(transfer_flags, ensure_ascii=False)}

Reference transfer map (known patterns between languages):
{transfer_map}

For each error:
1. Check if the student's Mandarin knowledge can help explain or
   fix the error (positive transfer = helpful, negative transfer = misleading)
2. Check if the student's English knowledge can help or hinders
3. If BOTH languages mislead the student, acknowledge this honestly

Provide:
- "bridge_explanation": a clear, concise explanation (2-3 sentences)
  that the Pedagogy Agent can incorporate into its response.
  Use specific examples from the student's known languages.
- "transfer_type": "positive" if a known language helps,
  "negative" if it misleads, "mixed" if both, or "none"

Return as JSON only."""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {
            "bridge_explanation": response.content,
            "transfer_type": "none"
        }

    return {
        "bridge_explanation": result.get("bridge_explanation", ""),
        "transfer_type": result.get("transfer_type", "none")
    }
import json
from state import TutorState
from langchain_openai import ChatOpenAI
 
 
# Initialize the LLM (shared across calls)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
 
 
def diagnostic_agent(state: TutorState) -> dict:
    """
    Takes the student's attempt, compares it to the correct answer,
    and returns a structured list of errors with transfer flags.
    """
    student_profile = state["student_profile"]
    known_languages = student_profile.get("known_languages", [])
 
    prompt = f"""You are a Japanese language error diagnostic system.
 
The student speaks these languages: {known_languages}
 
Exercise: {state['exercise_prompt']}
Correct answer: {state['correct_answer']}
Student's attempt: {state['student_input']}
 
Analyze the student's attempt carefully and return a JSON object with:
 
1. "errors": a list of errors, each with:
   - "type": one of ["word_order", "particle", "conjugation", "vocabulary",
     "kanji_reading", "grammar", "idiomatic"]
   - "description": brief explanation of what went wrong
   - "incorrect_part": the specific part the student got wrong
   - "correct_form": what it should be
 
2. "transfer_flags": a list of flags, each with:
   - "error_index": which error this relates to (0-based)
   - "source_language": "Mandarin" or "English"
   - "explanation": why this language might have caused the error
 
If there are no errors, return {{"errors": [], "transfer_flags": []}}
 
Return ONLY valid JSON, no other text."""
 
    response = llm.invoke(prompt)
 
    # Parse the LLM response into structured data
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return clean JSON
        result = {"errors": [], "transfer_flags": []}
 
    return {
        "errors": result.get("errors", []),
        "transfer_flags": result.get("transfer_flags", [])
    }
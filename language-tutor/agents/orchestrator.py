from state import TutorState
 
 
def orchestrator(state: TutorState) -> dict:
    """
    Decides the route based on student input.
 
    - If the student typed something → they submitted an answer → diagnose it
    - If the student input is empty → they need a new exercise → generate content
    """
    student_input = state.get("student_input", "").strip()
 
    if student_input:
        return {"route": "diagnose"}
    else:
        return {"route": "generate_content"}
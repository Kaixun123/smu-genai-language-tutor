from langgraph.graph import StateGraph, END
from state import TutorState

# Import all agent functions
from agents.orchestrator import orchestrator
from agents.diagnostic import diagnostic_agent
from agents.cross_lingual import cross_lingual_agent
from agents.pedagogy import pedagogy_agent
from agents.student_model import student_model_agent
from agents.content_generator import content_generator


def build_graph():
    """
    Builds and compiles the LangGraph StateGraph.
    Returns a compiled app you can call with app.invoke(state).
    """

    # ── Create the graph ──
    graph = StateGraph(TutorState)

    # ── Add all agents as nodes ──
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("diagnostic", diagnostic_agent)
    graph.add_node("cross_lingual", cross_lingual_agent)
    graph.add_node("pedagogy", pedagogy_agent)
    graph.add_node("student_model", student_model_agent)
    graph.add_node("content_generator", content_generator)

    # ── Set the entry point ──
    graph.set_entry_point("orchestrator")

    # ── Conditional routing from Orchestrator ──
    # Based on the "route" field in state, go to either
    # the diagnostic flow or the content generator
    graph.add_conditional_edges(
        "orchestrator",
        lambda state: state["route"],
        {
            "diagnose": "diagnostic",
            "generate_content": "content_generator"
        }
    )

    # ── Diagnostic flow (the main tutoring loop) ──
    # diagnose → bridge → teach → remember
    graph.add_edge("diagnostic", "cross_lingual")
    graph.add_edge("cross_lingual", "pedagogy")
    graph.add_edge("pedagogy", "student_model")
    graph.add_edge("student_model", END)

    # ── Content generator goes straight to END ──
    graph.add_edge("content_generator", END)

    # ── Compile and return ──
    app = graph.compile()
    return app
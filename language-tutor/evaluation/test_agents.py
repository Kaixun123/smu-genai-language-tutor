"""
Test Scripts for Individual Agents
=====================================
Each team member can run the test for their own agent WITHOUT
needing the full system to be connected.

Usage:
    python tests/test_agents.py                  # run all tests
    python tests/test_agents.py diagnostic       # run one agent test
    python tests/test_agents.py cross_lingual
    python tests/test_agents.py pedagogy
    python tests/test_agents.py student_model
    python tests/test_agents.py content_generator
    python tests/test_agents.py orchestrator
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Shared mock data ──
MOCK_STUDENT_PROFILE = {
    "name": "Test Student",
    "known_languages": ["Mandarin (native)", "English (fluent)"],
    "level": "N5",
    "error_history": {
        "particle": {"encounters": 2, "correct": 0, "last_seen": None}
    },
    "interaction_log": []
}

MOCK_ERRORS = [
    {
        "type": "word_order",
        "description": "Used SVO instead of SOV",
        "incorrect_part": "食べるりんごを",
        "correct_form": "りんごを食べる"
    }
]

MOCK_TRANSFER_FLAGS = [
    {
        "error_index": 0,
        "source_language": "Mandarin",
        "explanation": "Mandarin SVO order interfering with Japanese SOV"
    }
]


def test_orchestrator():
    """Test that the orchestrator routes correctly."""
    from agents.orchestrator import orchestrator

    print("Testing Orchestrator...")

    # Test 1: Student typed something → should route to diagnose
    result = orchestrator({
        "student_input": "毎日私は食べるりんごを",
        "route": ""
    })
    assert result["route"] == "diagnose", f"Expected 'diagnose', got '{result['route']}'"
    print("  ✓ Routes to 'diagnose' when student submits input")

    # Test 2: Empty input → should route to generate_content
    result = orchestrator({
        "student_input": "",
        "route": ""
    })
    assert result["route"] == "generate_content", f"Expected 'generate_content', got '{result['route']}'"
    print("  ✓ Routes to 'generate_content' when input is empty")

    # Test 3: Whitespace only → should route to generate_content
    result = orchestrator({
        "student_input": "   ",
        "route": ""
    })
    assert result["route"] == "generate_content"
    print("  ✓ Routes to 'generate_content' when input is whitespace")

    print("  All orchestrator tests passed!\n")


def test_diagnostic():
    """Test the diagnostic agent identifies errors correctly."""
    from agents.diagnostic import diagnostic_agent

    print("Testing Diagnostic Agent...")
    print("  (This calls the LLM — may take a few seconds)")

    result = diagnostic_agent({
        "student_input": "毎日私は食べるりんごを",
        "exercise_prompt": "Translate: I eat an apple every day",
        "correct_answer": "毎日私はりんごを食べる",
        "student_profile": MOCK_STUDENT_PROFILE
    })

    errors = result.get("errors", [])
    transfer_flags = result.get("transfer_flags", [])

    print(f"  Errors found: {len(errors)}")
    for e in errors:
        print(f"    - [{e.get('type')}] {e.get('description')}")

    print(f"  Transfer flags: {len(transfer_flags)}")
    for f in transfer_flags:
        print(f"    - {f.get('source_language')}: {f.get('explanation')}")

    assert len(errors) > 0, "Should have found at least one error"
    print("  ✓ Found errors in incorrect translation")

    # Test with correct answer
    result2 = diagnostic_agent({
        "student_input": "これは本です",
        "exercise_prompt": "Translate: This is a book",
        "correct_answer": "これは本です",
        "student_profile": MOCK_STUDENT_PROFILE
    })
    print(f"  Errors in correct answer: {len(result2.get('errors', []))}")
    print("  ✓ Diagnostic agent test complete!\n")


def test_cross_lingual():
    """Test the cross-lingual transfer agent finds bridges."""
    from agents.cross_lingual import cross_lingual_agent

    print("Testing Cross-Lingual Transfer Agent...")
    print("  (This calls the LLM — may take a few seconds)")

    result = cross_lingual_agent({
        "errors": MOCK_ERRORS,
        "transfer_flags": MOCK_TRANSFER_FLAGS,
        "student_profile": MOCK_STUDENT_PROFILE
    })

    bridge = result.get("bridge_explanation", "")
    transfer_type = result.get("transfer_type", "")

    print(f"  Transfer type: {transfer_type}")
    print(f"  Bridge explanation: {bridge[:200]}...")

    assert bridge != "", "Bridge explanation should not be empty"
    assert transfer_type != "", "Transfer type should not be empty"
    print("  ✓ Cross-lingual agent produced a bridge explanation")

    # Test with no errors
    result2 = cross_lingual_agent({
        "errors": [],
        "transfer_flags": [],
        "student_profile": MOCK_STUDENT_PROFILE
    })
    assert "No errors" in result2.get("bridge_explanation", "")
    print("  ✓ Returns 'no errors' message when input is correct")
    print("  ✓ Cross-lingual agent test complete!\n")


def test_pedagogy():
    """Test the pedagogy agent applies Socratic progression."""
    from agents.pedagogy import pedagogy_agent

    print("Testing Pedagogy Agent...")
    print("  (This calls the LLM — may take a few seconds)")

    base_state = {
        "student_input": "毎日私は食べるりんごを",
        "exercise_prompt": "Translate: I eat an apple every day",
        "errors": MOCK_ERRORS,
        "bridge_explanation": "Mandarin SVO order misleads here. Japanese is SOV.",
        "student_profile": MOCK_STUDENT_PROFILE
    }

    # Test 1: First encounter → should hint
    state1 = {**base_state, "student_profile": {
        **MOCK_STUDENT_PROFILE,
        "error_history": {}  # no prior encounters
    }}
    result1 = pedagogy_agent(state1)
    print(f"  1st encounter → strategy: {result1['teaching_strategy']}")
    assert result1["teaching_strategy"] == "hint"
    print("  ✓ Uses 'hint' on first encounter")

    # Test 2: Second encounter → should scaffold
    state2 = {**base_state, "student_profile": {
        **MOCK_STUDENT_PROFILE,
        "error_history": {"word_order": {"encounters": 2, "correct": 0}}
    }}
    result2 = pedagogy_agent(state2)
    print(f"  2nd encounter → strategy: {result2['teaching_strategy']}")
    assert result2["teaching_strategy"] == "scaffold"
    print("  ✓ Uses 'scaffold' on second encounter")

    # Test 3: Third encounter → should teach directly
    state3 = {**base_state, "student_profile": {
        **MOCK_STUDENT_PROFILE,
        "error_history": {"word_order": {"encounters": 3, "correct": 0}}
    }}
    result3 = pedagogy_agent(state3)
    print(f"  3rd encounter → strategy: {result3['teaching_strategy']}")
    assert result3["teaching_strategy"] == "direct"
    print("  ✓ Uses 'direct' on third encounter")

    # Test 4: No errors → should praise
    state4 = {**base_state, "errors": [], "bridge_explanation": ""}
    result4 = pedagogy_agent(state4)
    print(f"  No errors → strategy: {result4['teaching_strategy']}")
    assert result4["teaching_strategy"] == "praise"
    print("  ✓ Uses 'praise' when no errors")

    print("  All pedagogy tests passed!\n")


def test_student_model():
    """Test the student model agent updates profiles correctly."""
    from agents.student_model import student_model_agent

    print("Testing Student Model Agent...")

    # Use a test profile name to avoid overwriting real data
    test_profile = {
        "name": "Test Runner Student",
        "known_languages": ["Mandarin (native)", "English (fluent)"],
        "level": "N5",
        "error_history": {},
        "interaction_log": []
    }

    result = student_model_agent({
        "student_profile": test_profile,
        "student_input": "毎日私は食べるりんごを",
        "exercise_prompt": "Translate: I eat an apple every day",
        "errors": MOCK_ERRORS,
        "teaching_strategy": "hint",
        "transfer_type": "negative"
    })

    updated_profile = result["student_profile"]

    # Check error history was updated
    assert "word_order" in updated_profile["error_history"]
    assert updated_profile["error_history"]["word_order"]["encounters"] == 1
    print("  ✓ Error history updated correctly")

    # Check interaction log was appended
    assert len(updated_profile["interaction_log"]) == 1
    assert updated_profile["interaction_log"][0]["errors_count"] == 1
    print("  ✓ Interaction log recorded")

    # Run again to check accumulation
    result2 = student_model_agent({
        "student_profile": updated_profile,
        "student_input": "another attempt",
        "exercise_prompt": "another exercise",
        "errors": MOCK_ERRORS,
        "teaching_strategy": "scaffold",
        "transfer_type": "negative"
    })

    updated2 = result2["student_profile"]
    assert updated2["error_history"]["word_order"]["encounters"] == 2
    print("  ✓ Encounter count accumulates correctly")
    assert len(updated2["interaction_log"]) == 2
    print("  ✓ Interaction log grows with each interaction")

    # Clean up test file
    test_filepath = os.path.join(
        os.path.dirname(__file__), "..", "data",
        "student_profiles", "test_runner_student.json"
    )
    if os.path.exists(test_filepath):
        os.remove(test_filepath)
        print("  ✓ Cleaned up test profile file")

    print("  All student model tests passed!\n")


def test_content_generator():
    """Test the content generator creates exercises."""
    from agents.content_generator import content_generator

    print("Testing Content Generator Agent...")
    print("  (This calls the LLM — may take a few seconds)")

    result = content_generator({
        "student_profile": MOCK_STUDENT_PROFILE
    })

    exercise = result.get("exercise_prompt", "")
    answer = result.get("correct_answer", "")
    response = result.get("final_response", "")

    print(f"  Generated exercise: {exercise}")
    print(f"  Correct answer: {answer}")

    assert exercise != "", "Should generate an exercise prompt"
    assert answer != "", "Should provide a correct answer"
    assert response != "", "Should produce a student-facing response"
    print("  ✓ Content generator produced a complete exercise")

    print("  ✓ Content generator test complete!\n")


def test_full_graph():
    """Test the full graph end-to-end."""
    from graph import build_graph

    print("Testing Full Graph (end-to-end)...")
    print("  (This calls the LLM multiple times — may take 10-20 seconds)")

    app = build_graph()

    # Test diagnostic flow
    result = app.invoke({
        "student_input": "毎日私は食べるりんごを",
        "exercise_prompt": "Translate: I eat an apple every day",
        "correct_answer": "毎日私はりんごを食べる",
        "student_profile": MOCK_STUDENT_PROFILE,
        "errors": [],
        "transfer_flags": [],
        "bridge_explanation": "",
        "transfer_type": "",
        "encounter_count": 1,
        "teaching_strategy": "",
        "final_response": "",
        "route": ""
    })

    assert result["route"] == "diagnose"
    assert result["final_response"] != ""
    assert result["teaching_strategy"] != ""
    print(f"  Route: {result['route']}")
    print(f"  Errors: {len(result['errors'])}")
    print(f"  Strategy: {result['teaching_strategy']}")
    print(f"  Response: {result['final_response'][:100]}...")
    print("  ✓ Full diagnostic flow completed successfully")

    # Test content generation flow
    result2 = app.invoke({
        "student_input": "",
        "exercise_prompt": "",
        "correct_answer": "",
        "student_profile": MOCK_STUDENT_PROFILE,
        "errors": [],
        "transfer_flags": [],
        "bridge_explanation": "",
        "transfer_type": "",
        "encounter_count": 0,
        "teaching_strategy": "",
        "final_response": "",
        "route": ""
    })

    assert result2["route"] == "generate_content"
    assert result2["final_response"] != ""
    print(f"  Route: {result2['route']}")
    print(f"  Generated: {result2['final_response'][:100]}...")
    print("  ✓ Full content generation flow completed successfully")

    print("\n  All graph tests passed!\n")


# ── Run tests ──
TESTS = {
    "orchestrator": test_orchestrator,
    "diagnostic": test_diagnostic,
    "cross_lingual": test_cross_lingual,
    "pedagogy": test_pedagogy,
    "student_model": test_student_model,
    "content_generator": test_content_generator,
    "full_graph": test_full_graph
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        if test_name in TESTS:
            TESTS[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available: {', '.join(TESTS.keys())}")
    else:
        # Run all tests
        print("Running all agent tests...\n")
        for name, test_fn in TESTS.items():
            try:
                test_fn()
            except Exception as e:
                print(f"  ✗ {name} FAILED: {e}\n")
        print("=" * 60)
        print("All tests complete!")
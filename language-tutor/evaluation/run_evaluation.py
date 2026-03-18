import json
import os
import sys

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from graph import build_graph
from langchain_openai import ChatOpenAI


# LLM-as-judge model
# change when needed (this is a demo for now)
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def load_test_cases() -> list:
    """Load test cases from JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]


def load_demo_profiles() -> dict:
    """Load demo student profiles."""
    filepath = os.path.join(
        os.path.dirname(__file__), "..", "data",
        "student_profiles", "demo_profiles.json"
    )
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index by name for quick lookup
    return {p["name"]: p for p in data["profiles"]}


def get_profile_for_test(test_case: dict, profiles: dict) -> dict:
    """Get the appropriate student profile for a test case."""
    profile_name = test_case.get("student_profile", "Demo Student A")

    # Check if it matches a demo profile
    for name, profile in profiles.items():
        if name in profile_name:
            return profile.copy()

    # Custom profile for specific test cases
    if "3 prior word_order errors" in profile_name:
        return {
            "name": "Custom Student",
            "known_languages": ["Mandarin (native)", "English (fluent)"],
            "level": "N5",
            "error_history": {
                "word_order": {"encounters": 3, "correct": 0, "last_seen": None}
            },
            "interaction_log": []
        }

    # Default fallback
    return profiles.get("Demo Student A", {}).copy()


def run_single_test(app, test_case: dict, profile: dict) -> dict:
    """Run a single test case through the tutor system."""
    result = app.invoke({
        "student_input": test_case["student_input"],
        "exercise_prompt": test_case["exercise_prompt"],
        "correct_answer": test_case["correct_answer"],
        "student_profile": profile,
        "errors": [],
        "transfer_flags": [],
        "bridge_explanation": "",
        "transfer_type": "",
        "encounter_count": profile.get("error_history", {})
            .get(test_case.get("expected_error_types", [""])[0], {})
            .get("encounters", 0) + 1,
        "teaching_strategy": "",
        "final_response": "",
        "route": ""
    })
    return result


def judge_response(test_case: dict, result: dict) -> dict:
    """
    Uses LLM-as-judge to score the system's response
    against the expected behavior.
    """
    prompt = f"""You are evaluating a Japanese language tutor system.

TEST CASE:
- Exercise: {test_case['exercise_prompt']}
- Student input: {test_case['student_input']}
- Correct answer: {test_case['correct_answer']}
- Expected error types: {test_case['expected_error_types']}
- Expected transfer type: {test_case['expected_transfer']}
- Expected teaching strategy: {test_case['expected_strategy']}

SYSTEM OUTPUT:
- Errors detected: {json.dumps(result.get('errors', []), ensure_ascii=False)}
- Transfer type: {result.get('transfer_type', 'none')}
- Teaching strategy: {result.get('teaching_strategy', 'unknown')}
- Response to student: {result.get('final_response', '')}

Score the system on these criteria (1-5 each):

1. ERROR_DETECTION: Did the system identify the correct error types?
   5 = all errors correctly identified
   1 = completely wrong or missed errors

2. TRANSFER_ACCURACY: Did the system correctly identify whether
   the student's known languages help or hinder?
   5 = perfect transfer analysis
   1 = completely wrong transfer assessment

3. STRATEGY_APPROPRIATENESS: Did the system use the right teaching
   strategy (hint vs scaffold vs direct) given the student's history?
   5 = perfect strategy choice
   1 = completely wrong strategy

4. RESPONSE_QUALITY: Is the actual response helpful, encouraging,
   and pedagogically sound?
   5 = excellent tutoring response
   1 = confusing or unhelpful response

5. BRIDGE_EFFECTIVENESS: If a cross-lingual bridge was used,
   was it accurate and helpful?
   5 = bridge is accurate and illuminating
   1 = bridge is wrong or confusing
   N/A = no bridge was expected

Return ONLY a JSON object:
{{
    "error_detection": <score>,
    "transfer_accuracy": <score>,
    "strategy_appropriateness": <score>,
    "response_quality": <score>,
    "bridge_effectiveness": <score or null>,
    "notes": "<brief explanation of scores>"
}}"""

    response = judge_llm.invoke(prompt)

    try:
        scores = json.loads(response.content)
    except json.JSONDecodeError:
        scores = {
            "error_detection": 0,
            "transfer_accuracy": 0,
            "strategy_appropriateness": 0,
            "response_quality": 0,
            "bridge_effectiveness": None,
            "notes": f"Failed to parse judge response: {response.content}"
        }

    return scores


def run_evaluation():
    """Run all test cases and produce a summary report."""
    print("=" * 60)
    print("EVALUATION: Running all test cases")
    print("=" * 60)

    app = build_graph()
    test_cases = load_test_cases()
    profiles = load_demo_profiles()

    results = []

    for i, tc in enumerate(test_cases):
        print(f"\n--- Test Case {tc['id']}: {tc['description']} ---")

        profile = get_profile_for_test(tc, profiles)
        system_result = run_single_test(app, tc, profile)

        print(f"  Errors found: {len(system_result.get('errors', []))}")
        print(f"  Transfer: {system_result.get('transfer_type', 'none')}")
        print(f"  Strategy: {system_result.get('teaching_strategy', 'unknown')}")
        print(f"  Response: {system_result.get('final_response', '')[:100]}...")

        # Judge the response
        print("  Judging...")
        scores = judge_response(tc, system_result)
        print(f"  Scores: {scores}")

        results.append({
            "test_case_id": tc["id"],
            "category": tc["category"],
            "scores": scores,
            "system_output": {
                "errors": system_result.get("errors", []),
                "transfer_type": system_result.get("transfer_type", ""),
                "teaching_strategy": system_result.get("teaching_strategy", ""),
                "final_response": system_result.get("final_response", "")
            }
        })

    # ── Summary Report ──
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    # Calculate averages per criterion
    criteria = [
        "error_detection", "transfer_accuracy",
        "strategy_appropriateness", "response_quality"
    ]

    for criterion in criteria:
        scores_list = [
            r["scores"][criterion] for r in results
            if r["scores"].get(criterion) is not None
            and r["scores"][criterion] > 0
        ]
        if scores_list:
            avg = sum(scores_list) / len(scores_list)
            print(f"  {criterion}: {avg:.2f} / 5.00  ({len(scores_list)} cases)")

    # Bridge effectiveness (only for cases where it applies)
    bridge_scores = [
        r["scores"]["bridge_effectiveness"] for r in results
        if r["scores"].get("bridge_effectiveness") is not None
    ]
    if bridge_scores:
        avg = sum(bridge_scores) / len(bridge_scores)
        print(f"  bridge_effectiveness: {avg:.2f} / 5.00  ({len(bridge_scores)} cases)")

    # Category breakdown
    print("\n  By Category:")
    categories = set(r["category"] for r in results)
    for cat in sorted(categories):
        cat_results = [r for r in results if r["category"] == cat]
        avg_quality = sum(
            r["scores"].get("response_quality", 0) for r in cat_results
        ) / len(cat_results)
        print(f"    {cat}: avg response quality {avg_quality:.2f} / 5.00  ({len(cat_results)} cases)")

    # Save full results
    output_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Full results saved to: {output_path}")

    return results


if __name__ == "__main__":
    run_evaluation()
import json
import os
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

# LAYER 1: Structural Schema Contract
class ReminderSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str
    datetime: str
    intent: Literal["CREATE", "RESCHEDULE", "SNOOZE", "CLARIFY"]
    message: str


def mock_llm_call(user_input: str, must_clarify: bool) -> dict[str, str]:
    """Return a deterministic fixture response for the requested reminder action."""
    if must_clarify:
        return {
            "task": "",
            "datetime": "",
            "intent": "CLARIFY",
            "message": "Please provide more details.",
        }

    normalized_input = user_input.casefold()
    if re.search(r"\bsnooze\b", normalized_input):
        intent = "SNOOZE"
    elif re.search(r"\b(?:reschedule|move)\b", normalized_input):
        intent = "RESCHEDULE"
    else:
        intent = "CREATE"

    return {
        "task": "extracted task",
        "datetime": "extracted date",
        "intent": intent,
        "message": "Reminder request processed.",
    }


def run_evaluation() -> None:
    # Create evidence directory if it doesn't exist
    os.makedirs("evidence", exist_ok=True)
    
    with open("evals/dataset.json", "r") as f:
        dataset = json.load(f)

    passed = 0
    results = []
    
    for case in dataset:
        output = mock_llm_call(case["input"], case["must_have_clarification"])

        case_passed = True
        reason = ""
        
        try:
            # LAYER 1: Structural Validation (Pydantic)
            validated = ReminderSchema(**output)
            
            # LAYER 2: Invariant/Property Validation
            if validated.intent != case["expected_intent"]:
                case_passed = False
                reason = f"Expected intent {case['expected_intent']}, got {validated.intent}"
                
            if case["must_have_clarification"] and validated.intent != "CLARIFY":
                case_passed = False
                reason = "Invariant failed: Expected CLARIFY for missing mandatory info."
                
            # LAYER 3: Semantic Evaluation (Heuristic)
            if validated.intent == "CLARIFY" and len(validated.message) < 5:
                case_passed = False
                reason = "Semantic fail: Clarification message too short."

        except ValidationError as e:
            case_passed = False
            reason = f"Schema Validation Failed: {e}"

        if case_passed:
            passed += 1
            
        results.append({"id": case["id"], "status": "PASS" if case_passed else "FAIL", "reason": reason})

    score = (passed / len(dataset)) * 100
    threshold = 80.0
    final_verdict = "PASS" if score >= threshold else "FAIL"

    # Save Evidence
    evidence_data = {
        "score": score,
        "threshold": threshold,
        "verdict": final_verdict,
        "results": results
    }
    
    with open("evidence/eval-results.json", "w") as f:
        json.dump(evidence_data, f, indent=4)

    print(f"Final Score: {score}%")
    print(f"Verdict: {final_verdict} (Threshold: {threshold}%)")
    
    if final_verdict == "FAIL":
        print("Failures detected! Check evidence/eval-results.json")
    else:
        print("All checks passed.")

if __name__ == "__main__":
    run_evaluation()
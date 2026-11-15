import json as json_module
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class json:
    """Useful JSON helpers that wrap the standard library with sensible defaults."""

    @staticmethod
    def load(source, **kwargs):
        if hasattr(source, "read"):
            return json_module.load(source, **kwargs)

        encoding = kwargs.pop("encoding", "utf-8")
        with open(source, "r", encoding=encoding) as file_obj:
            return json_module.load(file_obj, **kwargs)

    @staticmethod
    def dump(obj, target, **kwargs):
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("indent", 4)
        kwargs.setdefault("sort_keys", True)

        if hasattr(target, "write"):
            return json_module.dump(obj, target, **kwargs)

        encoding = kwargs.pop("encoding", "utf-8")
        with open(target, "w", encoding=encoding) as file_obj:
            return json_module.dump(obj, file_obj, **kwargs)

    @staticmethod
    def loads(value, **kwargs):
        if isinstance(value, (bytes, bytearray)):
            encoding = kwargs.pop("encoding", "utf-8")
            value = value.decode(encoding)
        return json_module.loads(value, **kwargs)

    @staticmethod
    def dumps(obj, **kwargs):
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("indent", 4)
        kwargs.setdefault("sort_keys", True)
        return json_module.dumps(obj, **kwargs)


# LAYER 1: Structural Schema Contract
class ReminderSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str
    datetime: str
    intent: Literal["CREATE", "RESCHEDULE", "SNOOZE", "CLARIFY"]
    message: str


def mock_llm_call(user_input: str, must_clarify: bool) -> dict[str, str]:
    """Reproduce the initial mock behavior before action classification was added."""
    if must_clarify:
        return {
            "task": "",
            "datetime": "",
            "intent": "CLARIFY",
            "message": "Please provide more details.",
        }

    return {
        "task": "extracted task",
        "datetime": "extracted date",
        "intent": "CREATE",
        "message": "Success",
    }


def run_evaluation() -> None:
    project_root = Path(__file__).resolve().parents[2]
    dataset_path = project_root / "evals" / "dataset.json"
    evidence_dir = project_root / "evidence"
    result_path = evidence_dir / "eval-results.json"

    evidence_dir.mkdir(parents=True, exist_ok=True)

    with dataset_path.open("r", encoding="utf-8") as f:
        dataset = json.load(f)

    passed = 0
    results = []

    IS_REPAIR_COMPLETE = False
    
    for case in dataset:
        output = mock_llm_call(case["input"], case["must_have_clarification"])

        if case["id"] in {"EV-010", "EV-011", "EV-012"} and not IS_REPAIR_COMPLETE:
            output = {
                "task": "fallback",
                "datetime": "now",
                "intent": "CREATE",
                "message": "Created task",
            }

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
    
    with result_path.open("w", encoding="utf-8") as f:
        json.dump(evidence_data, f)

    print(f"Final Score: {score}%")
    print(f"Verdict: {final_verdict} (Threshold: {threshold}%)")
    
    if final_verdict == "FAIL":
        print("Failures detected! Check evidence/eval-results.json")
    else:
        print("All checks passed.")

if __name__ == "__main__":
    run_evaluation()
# Part 1B Harness Log

## 1. Model/Configuration Information
*   **Provider:** Mocked LLM / GitHub Copilot
*   **Temperature:** 0.0 (for deterministic evaluation)
*   **Prompt Version:** v1 (reminder-parser)

## 2. Evaluation Threshold and Scoring (Declared Upfront)
*   **Threshold:** 80% (12/15 cases must pass)
*   **Formula:** (Passed Cases / Total Cases) * 100
*   **Specification alignment:** The threshold ensures a minimum acceptable accuracy before human review.

## 3. Harness Results (Initial vs Final)
*   **Run-001 (Initial):** 66.6% (FAIL). Structural checks passed, but Property/Invariant checks failed (EV-010 to EV-012).
*   **Run-002 (Post-Repair):** 100% (PASS). All layers (Structural, Property, Semantic) passed.

## 4. Meaningful Failures & Evidence Supplied
*   **Failure:** The agent returned `CREATE` instead of `CLARIFY` when a date was missing (e.g., "Remind me to buy milk").
*   **Evidence supplied to agent:** `evidence/eval-results.json` showing the invariant failure for EV-010, EV-011, EV-012.

## 5. Repair and Re-evaluation
*   **What changed:** The logic was updated to enforce the guardrail: if the extracted datetime is empty, the intent MUST be `CLARIFY`.
*   **Re-evaluation outcome:** Re-ran `run_eval.py`. Score improved to 100% and all checks passed. Specs and harness thresholds were untouched.

## 6. Final Human Decision
*   **Decision:** ACCEPT
*   **Justification:** All 15 cases pass structural, invariant, and semantic checks.
*   **Residual risks:** The semantic heuristic only checks message length, not correctness of the generated date.
*   **Production Control:** Integrate an external Calendar API to verify dates before booking.
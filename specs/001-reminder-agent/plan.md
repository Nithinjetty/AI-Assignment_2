# Implementation Plan: Reminder Agent

**Branch**: `001-reminder-agent` | **Date**: 2026-11-15 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from `specs/001-reminder-agent/spec.md`

## Summary

Build a typed Python 3.10+ reminder interpretation package with a strict Pydantic
response model, an injectable local mock-LLM function, deterministic temporal
normalization, and a standalone `.harness/evaluate.py` runner. The response
contract contains exactly `task`, `datetime`, `intent`, and `message`. Untrusted
interpreter output is validated before serialization; incomplete or ambiguous
requests produce `CLARIFY` rather than inferred dates or times.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: Pydantic v2 (`pydantic>=2,<3`); `tzdata` for portable
IANA timezone data where the operating system does not provide it. Development
dependencies: pytest and mypy.

**Storage**: N/A. This feature parses and returns a response; persistence and
notification delivery are out of scope.

**Testing**: pytest unit, contract, and integration tests; mypy type checking of
`src/` and `.harness/`; deterministic `.harness/evaluate.py` regression run.

**Target Platform**: Cross-platform Python 3.10+; timezone behavior must also work
on Windows using IANA timezone data.

**Project Type**: Single Python package with a standalone evaluation harness.

**Performance Goals**: No production latency target is defined. The default
fixture-based evaluation does not call a live model or network service.

**Constraints**: Exactly one valid JSON object with the four specified string
fields; no extra fields or prose. All Python functions and methods are typed.
Relative date/time resolution requires injected, trusted reference time and
timezone context. Missing or ambiguous required information results in
`CLARIFY`. The mock and default harness make no network calls.

**Scale/Scope**: One prompt produces one response. Include representative and
adversarial fixtures for all four intents, incomplete input, ambiguous temporal
phrases, invalid interpreter output, and timezone edge cases. No database or
external LLM provider is included.

## Constitution Check

**Pre-design gate**:

| Requirement | Design response | Result |
|---|---|---|
| Strict JSON contract | Validate the single response model, forbid extra fields, and serialize only the validated model. | PASS |
| Grounded temporal interpretation | Inject reference time/timezone; reject unresolved or ambiguous times and ask for clarification. | PASS |
| Explicit clarification | Return `CLARIFY` for missing or unresolvable task, date, time, action, or reminder identity. | PASS |
| Typed Python | Type all functions and methods; include mypy in quality gates. | PASS |
| Evaluation and regression quality | Run deterministic contract and behavior fixtures; fail on invalid JSON, contract violations, incorrect clarification, or invented times. | PASS |

No constitution violations are identified.

## Project Structure

### Documentation (this feature)

```text
specs/001-reminder-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── reminder-response.schema.json
├── checklists/
│   └── requirements.md
└── tasks.md
```

`tasks.md` is produced by `/speckit-tasks`, not this planning command.

### Source Code (repository root)

```text
pyproject.toml
src/
└── reminder_agent/
    ├── __init__.py
    ├── models.py
    ├── processor.py
    ├── temporal.py
    └── mock_llm.py
tests/
├── unit/
│   ├── test_models.py
│   ├── test_temporal.py
│   └── test_processor.py
├── contract/
│   └── test_response_contract.py
└── integration/
    └── test_mock_pipeline.py
.harness/
├── evaluate.py
└── cases.jsonl
```

**Structure Decision**: Use one `src/`-layout Python package. Keep Pydantic
contract validation, deterministic temporal interpretation, and the mock
interpreter as small separable modules. The `.harness` directory holds a
standalone CLI evaluation runner and fixture data; it is not part of the
runtime response contract. Tests cover each module and the end-to-end mocked
pipeline.

## Design Decisions

- Treat interpreter output as untrusted raw JSON text. Validate it with the
  response model in strict mode and reject malformed JSON, extra text, unknown
  keys, and invalid values. Do not regex-extract, repair, or silently coerce
  invalid output.
- Use an injected interpreter protocol and a deterministic mock implementation.
  The mock returns controlled outputs for known test prompts and clarifies
  unknown cases; it does not call an external model or claim general language
  understanding.
- Keep date/time resolution deterministic and separate from the mock. Inject a
  reference clock and timezone; normalize only aware datetimes. Ask for
  clarification for missing context, DST ambiguity, or nonexistent local times.
- Keep evaluation fixtures fixed and runnable without network access or the
  machine's current clock. The runner reports per-case failures and returns a
  non-zero exit status if any release-blocking check fails.

## Constitution Check (Post-design)

The planned Pydantic validation and serialization preserve the exact four-field
JSON contract. The injected temporal context prevents implicit system-clock or
timezone assumptions. Incomplete cases must produce `CLARIFY`; typed interfaces
and mypy satisfy the type-hint principle. Unit, contract, integration, and
standalone harness fixtures exercise these rules, including regression cases.

**Post-design gate: PASS. No constitution violations or exceptions.**

## Complexity Tracking

No constitution violations require justification. The package and harness remain
single-project components; no provider SDK, persistence layer, or service
framework is introduced.

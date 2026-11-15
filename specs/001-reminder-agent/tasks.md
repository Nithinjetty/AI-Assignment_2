---
description: "Task list for the Reminder Agent feature"
---

# Tasks: Reminder Agent

**Input**: Design documents from `specs/001-reminder-agent/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and
`contracts/reminder-response.schema.json`

**Tests**: Tests are included because the project constitution and feature
requirements mandate contract, clarification, temporal, and regression tests.

**Organization**: Tasks are grouped by user story. Every task has an exact path
and uses the required checklist format.

## Phase 1: Setup

**Purpose**: Initialize the Python project and package layout.

- [ ] T001 [P] Configure Python 3.10+, `pydantic>=2,<3`, `tzdata`, pytest, mypy, src-layout packaging, and test/type-check settings in `pyproject.toml`.
- [ ] T002 [P] Create the typed public package initializer and exports in `src/reminder_agent/__init__.py`.

---

## Phase 2: Foundational

**Purpose**: Define and test shared response and temporal primitives before
implementing user stories.

- [ ] T003 [P] Write strict response-model tests for exact fields, string types, the four intents, extra-field rejection, and empty values in `tests/unit/test_models.py`.
- [ ] T004 [P] Write temporal tests for offset-aware ISO 8601 values, injected reference time/timezone, and unresolved values in `tests/unit/test_temporal.py`.
- [ ] T005 [P] Implement `ReminderIntent` and strict `ReminderResponse` validation in `src/reminder_agent/models.py`: `task` is "Identified task text; empty only when it cannot be determined."; `datetime` is "ISO 8601 date-time with a timezone offset, or empty when unresolved."; `intent` is "Exactly one of the four enum values above."; and `message` is "Concise confirmation or a focused clarification question." For `CREATE`, `RESCHEDULE`, and `SNOOZE`, require non-empty task and datetime; forbid extra fields.
- [ ] T006 [P] Implement typed temporal context and deterministic ISO 8601 normalization in `src/reminder_agent/temporal.py`: `reference_time` is "timezone-aware datetime" and is required only when relative wording needs a reference instant; `timezone` is an "IANA timezone or explicit offset" and must be supplied or unambiguously specified when local-time interpretation requires it. Never use the host's implicit clock or timezone.

**Checkpoint**: Response and temporal primitives are tested and ready for all
user stories.

---

## Phase 3: User Story 1 - Create a Reminder (Priority: P1)

**Goal**: Return a validated `CREATE` response for complete requests and
`CLARIFY` when task, date, or time is missing.

**Independent Test**: A complete prompt returns exactly the four required
fields with the expected task and datetime; omitting either date or time returns
`CLARIFY` without supplying a guessed value.

### Tests for User Story 1

- [ ] T007 [US1] Write failing processor tests for a complete create request, missing date, missing time, and exact JSON serialization in `tests/unit/test_processor.py`.

### Implementation for User Story 1

- [ ] T008 [P] [US1] Implement the typed interpreter protocol `__call__(prompt: str, context: TemporalContext | None) -> str` and response-validation pipeline in `src/reminder_agent/processor.py`; reject malformed or extra output and serialize only a validated response.
- [ ] T009 [P] [US1] Implement the deterministic mock-LLM function with signature `__call__(prompt: str, context: TemporalContext | None) -> str` for known create fixtures and safe `CLARIFY` responses for unknown prompts in `src/reminder_agent/mock_llm.py`.

**Checkpoint**: The create and missing-date/time scenarios pass independently
using the mock interpreter.

---

## Phase 4: User Story 2 - Clarify Incomplete or Ambiguous Requests (Priority: P1)

**Goal**: Ask focused questions for missing or ambiguous task, action, date,
time, timezone, or reminder identity without inventing values.

**Independent Test**: Requests missing a task or required temporal context, and
requests with conflicting or ambiguous date/time wording, return a valid
`CLARIFY` response that preserves only known values.

### Tests for User Story 2

- [ ] T010 [P] [US2] Write tests for missing task/action, conflicting temporal details, and ambiguous reminder references in `tests/unit/test_processor.py`.
- [ ] T011 [P] [US2] Add tests for absent timezone context and ambiguous or nonexistent daylight-saving local times in `tests/unit/test_temporal.py`.

### Implementation for User Story 2

- [ ] T012 [US2] Implement clarification decisions for missing or ambiguous task, action, date, time, timezone, and reminder identity in `src/reminder_agent/processor.py` and `src/reminder_agent/temporal.py`; retain known fields, leave undetermined strings empty, and never guess.

**Checkpoint**: All incomplete and ambiguous requests clarify without unsupported
dates or times.

---

## Phase 5: User Story 3 - Change an Existing Reminder (Priority: P2)

**Goal**: Represent clear reschedule and snooze requests and clarify when the
affected reminder or target time is not identifiable.

**Independent Test**: Clear requests for each action return their matching
intent and target datetime; unidentifiable reminders or unresolved target times
return `CLARIFY`.

### Tests for User Story 3

- [ ] T013 [US3] Write failing tests for clear reschedule, clear snooze, unidentified reminders, and unresolved target times in `tests/integration/test_mock_pipeline.py`.

### Implementation for User Story 3

- [ ] T014 [P] [US3] Extend deterministic mock fixtures for `RESCHEDULE` and `SNOOZE` requests in `src/reminder_agent/mock_llm.py`.
- [ ] T015 [P] [US3] Implement processing rules for `RESCHEDULE` and `SNOOZE`, requiring an identifiable task/reminder and grounded target datetime, in `src/reminder_agent/processor.py`.

**Checkpoint**: Reschedule and snooze requests are independently testable and
never select an unknown reminder or invent a target time.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Complete the standalone evaluation harness and verify all
constitution and quickstart gates.

- [ ] T016 [P] Add fixed JSONL evaluation cases for all four intents, missing information, temporal ambiguity, malformed output, extra fields, and fabricated-time rejection in `.harness/cases.jsonl`.
- [ ] T017 [P] Add contract tests for the exact four response fields, types, and allowed intents in `tests/contract/test_response_contract.py`.
- [ ] T018 Implement the typed, offline evaluation CLI in `.harness/evaluate.py`; load fixtures relative to the script, report per-case results, validate exact schema and expected behavior, and exit non-zero on any release-blocking failure.
- [ ] T019 Run pytest, mypy over `src/` and `.harness/`, the evaluation runner, and the scenarios in `specs/001-reminder-agent/quickstart.md`; update that quickstart with verified commands and outcomes.

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T001 and T002 can run in parallel.
- **Foundational (Phase 2)**: Starts after setup. T003 and T004 are parallel
  test tasks; after they fail as expected, T005 and T006 can be implemented in
  parallel because they modify separate modules.
- **User Story 1 (Phase 3)**: Starts after foundational work. T007 tests come
  first; then T008 and T009 can run in parallel because the interpreter seam is
  defined by the plan and the tasks modify separate files.
- **User Story 2 (Phase 4)**: Starts after User Story 1 because it extends the
  same processor and temporal modules. T010 and T011 are independent tests;
  T012 follows both.
- **User Story 3 (Phase 5)**: Starts after User Story 2 due shared processor
  and mock files. T013 tests come first; T014 and T015 can run in parallel.
- **Polish (Phase 6)**: Starts after the stories. T016 and T017 can run in
  parallel; T018 depends on fixture format from T016; T019 runs last.

### User Story Dependencies

```text
Setup -> Foundational -> US1 -> US2 -> US3 -> Polish
```

The stories are independently testable at their checkpoints, but implementation
phases are ordered because they extend the same processor and mock modules.

### Parallel Opportunities

- **Setup**: T001 and T002.
- **Foundational**: T003 and T004, then T005 and T006.
- **US1**: T008 and T009 after T007.
- **US2**: T010 and T011.
- **US3**: T014 and T015 after T013.
- **Polish**: T016 and T017; T018 follows T016.

## Parallel Execution Examples

### User Story 1

After T007's tests are written and fail, implement the response pipeline and
mock interpreter concurrently:

```text
Task: T008 in src/reminder_agent/processor.py
Task: T009 in src/reminder_agent/mock_llm.py
```

### User Story 2

Run the clarification behavior tests and temporal edge tests concurrently,
then implement the combined policy after both are in place:

```text
Task: T010 in tests/unit/test_processor.py
Task: T011 in tests/unit/test_temporal.py
```

### User Story 3

After T013's tests are written and fail, extend the mock and processor in
parallel because they are separate files and share the planned interpreter
contract:

```text
Task: T014 in src/reminder_agent/mock_llm.py
Task: T015 in src/reminder_agent/processor.py
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete User Story 1 only.
3. Validate complete create requests and missing-date/time clarification
   independently before expanding scope.

### Incremental Delivery

1. Add User Story 2 and verify all clarification and temporal ambiguity cases.
2. Add User Story 3 and verify reschedule/snooze behavior.
3. Finish the evaluation harness, run type checking and all tests, and validate
   the quickstart scenarios.

## Notes

- Every task uses the required checkbox, sequential ID, optional parallel
  marker, required story label for story tasks, and an exact file path.
- Tests precede implementation within each user story.
- All Python application and harness functions must have parameter and return
  type hints.
- The default evaluation path uses only deterministic mock fixtures and makes
  no network calls.

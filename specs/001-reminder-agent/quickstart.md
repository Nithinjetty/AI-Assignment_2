# Quickstart: Reminder Agent

This guide describes how to validate the planned implementation. The mock
pipeline is offline and deterministic; it does not deliver notifications or call
an external LLM provider.

## Prerequisites

- Python 3.10 or later.
- A virtual environment.

## Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

The project dependencies include Pydantic v2 and `tzdata`; development checks
include pytest and mypy.

## Validate

```powershell
python -m pytest
python -m mypy src .harness
python .harness\evaluate.py
```

All commands must exit successfully. The evaluation runner reports each fixture
and exits non-zero if JSON parsing, the exact response schema, expected
clarification behavior, or date/time grounding fails.

## Representative Scenarios

With the fixture clock and timezone set explicitly, an input such as
`Remind me to submit the report on 2026-11-16 at 09:00 +05:30.` should produce
`CREATE` and an ISO 8601 datetime with the same offset.

An input such as `Remind me to submit the report.` must produce `CLARIFY`, an
empty `datetime`, and a message asking for the missing date and time. The runner
must reject a response with extra fields, invalid JSON, a missing field, a
naive datetime, or a fabricated date/time.

See [the response contract](./contracts/reminder-response.schema.json) and
[the data model](./data-model.md) for field and validation semantics.

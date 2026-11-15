<!--
Sync Impact Report
Version change: unversioned scaffold -> 1.0.0 (initial project-specific constitution)
Modified principles:
- First unfilled principle slot -> Strict JSON Contract
- Second unfilled principle slot -> Grounded Temporal Interpretation
- Third unfilled principle slot -> Explicit Clarification
- Fourth unfilled principle slot -> Typed Python
- Fifth unfilled principle slot -> Evaluation and Regression Quality
Added sections: Additional Constraints, Development Workflow
Removed sections: None
Follow-up TODOs: Establish the original ratification date.
-->

# Natural-Language Reminder Agent Constitution

## Core Principles

### Strict JSON Contract
Every application response MUST be exactly one valid JSON value conforming to the
documented response schema. The application MUST NOT emit Markdown, code fences,
comments, explanatory prose, or trailing commas outside or within that JSON value.
JSON validity and schema conformance are separate requirements and both MUST be
checked. This contract makes responses reliably consumable by downstream software.

### Grounded Temporal Interpretation
The agent MUST NOT invent or infer unsupported dates or times. It may return a date
or time only when grounded in the user's request or trusted runtime context, with
any required reference date and timezone available. Ambiguous or unresolvable
temporal expressions MUST be clarified rather than guessed. This prevents reminders
from being scheduled for fabricated or unintended times.

### Explicit Clarification
If a request lacks a task, date, or time, or any of these cannot be determined
unambiguously, the response MUST use the intent value `CLARIFY`. It MUST identify
what information is missing or ambiguous without filling the gap with a guess.
The agent MUST NOT present an incomplete request as a schedulable reminder.

### Typed Python
All Python application and evaluation-harness functions and methods MUST declare
type hints for parameters and return values. Module-level interfaces and data
structures MUST use appropriate types. Type checking MUST be included in the
development quality gates so that type annotations remain useful and consistent.

### Evaluation and Regression Quality
The project MUST maintain a robust, repeatable evaluation harness covering valid
JSON and schema compliance, complete and incomplete requests, ambiguous temporal
language, and unsupported date/time generation. It MUST verify expected intents
and extracted values on representative and adversarial examples. Any invalid JSON,
schema violation, incorrect clarification, or unsupported date/time output MUST
fail evaluation; these failures are release blockers. Regression cases MUST be
retained when behavior defects are fixed.

## Additional Constraints

The response schema MUST define the `intent` field and the representation of
reminder details and clarification needs. The `CLARIFY` intent MUST be represented
using that schema, and consumers MUST be able to distinguish a clarification
response from a schedulable reminder. Schema changes MUST be reviewed for
compatibility with downstream consumers.

Temporal normalization MUST use only a trustworthy reference date and timezone
when they are required to resolve the user's wording. If that context is absent,
the agent MUST ask for clarification instead of relying on the machine's implicit
clock or timezone.

## Development Workflow

Changes to request interpretation, temporal handling, response serialization, or
the response schema MUST include focused tests for the changed behavior. Tests
MUST cover both successful reminder extraction and the `CLARIFY` behavior for
missing or ambiguous task, date, and time information. The evaluation harness
MUST run in the project's verification workflow, and its release-blocking checks
MUST pass before changes are accepted.

Code review MUST verify compliance with this constitution, including type hints,
JSON-only output, grounded date/time handling, and evaluation coverage. Any
proposed exception MUST be documented and approved through the amendment process
before implementation.

## Governance

This constitution governs project design, implementation, testing, and review.
Amendments MUST be proposed with their rationale and impact on the response
contract, existing behavior, and evaluation coverage. The project owner MUST
approve amendments, and affected tests and documentation MUST be updated with
the change.

The constitution uses semantic versioning. A MAJOR increment is required for
backward-incompatible governance changes or removals; a MINOR increment is
required for new principles, sections, or materially expanded requirements; a
PATCH increment is required for clarifications and other non-semantic edits.
Every amendment MUST update the version and last-amended date.

Reviewers MUST check proposed changes and releases against these requirements.
The evaluation harness and type-checking results MUST be reviewed as applicable;
non-compliant changes MUST NOT be accepted or released until corrected or the
constitution is formally amended.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date unknown | **Last Amended**: 2026-11-15

# Feature Specification: Reminder Agent

**Feature Branch**: Not created (workspace is not a Git repository)

**Created**: 2026-11-15

**Status**: Draft

**Input**: User description: "Build a Reminder Agent that takes an unstructured user prompt and returns a JSON object with exactly these fields: task (string), datetime (string), intent (enum: CREATE, RESCHEDULE, SNOOZE, CLARIFY), and message (string). If the user wants to create a reminder but doesn't specify a date/time, the intent must be CLARIFY."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Reminder (Priority: P1)

A user asks in natural language to create a reminder and includes a clear task and
date/time. The agent returns a JSON object describing the reminder so the user or
a downstream service can act on it.

**Why this priority**: Creating a reminder is the primary purpose of the feature.

**Independent Test**: Submit a prompt with an unambiguous task, date, and time;
verify the response describes that task and time, uses the `CREATE` intent, and
contains only the four required fields.

**Acceptance Scenarios**:

1. **Given** a prompt with a clear task and unambiguous date and time, **When** the
   agent processes it, **Then** it returns a `CREATE` response with the task and
   normalized date/time.
2. **Given** a prompt that requests a reminder but omits its date or time,
   **When** the agent processes it, **Then** it returns `CLARIFY` and asks for the
   missing information without inventing a date or time.

---

### User Story 2 - Clarify an Incomplete or Ambiguous Request (Priority: P1)

A user makes a reminder request that lacks a task, date, or time, or uses wording
that cannot be resolved reliably. The agent asks a focused question rather than
guessing.

**Why this priority**: Clarification prevents unintended reminders and is required
whenever essential information is absent or uncertain.

**Independent Test**: Submit prompts with each required detail omitted or ambiguous;
verify each response uses `CLARIFY`, identifies what needs clarification, and does
not supply an unsupported task or datetime.

**Acceptance Scenarios**:

1. **Given** a request with no identifiable task, **When** the agent processes it,
   **Then** it returns `CLARIFY` and asks what the reminder is for.
2. **Given** a request with an ambiguous date or time, **When** the agent processes
   it, **Then** it returns `CLARIFY` and asks a question that resolves the
   ambiguity.
3. **Given** a request with no identifiable reminder action, **When** the agent
   processes it, **Then** it returns `CLARIFY` and asks what reminder action the
   user intends.

---

### User Story 3 - Change an Existing Reminder (Priority: P2)

A user asks to reschedule or snooze a reminder. The agent identifies the requested
action and the affected reminder from the prompt or available trusted context,
then returns the requested target time.

**Why this priority**: Users need to adjust reminders as well as create them, but
these actions depend on identifying an existing reminder.

**Independent Test**: Submit clear reschedule and snooze requests with an
identifiable reminder and resolvable target time; verify the corresponding intent,
task, datetime, and message.

**Acceptance Scenarios**:

1. **Given** a request to change an identifiable reminder to a clear new date and
   time, **When** the agent processes it, **Then** it returns `RESCHEDULE` and the
   requested target datetime.
2. **Given** a request to snooze an identifiable reminder for a resolvable
   duration, **When** the agent processes it, **Then** it returns `SNOOZE` and the
   resulting datetime only if the required reference time is available.
3. **Given** an unidentifiable reminder or unresolved target time, **When** the
   agent processes it, **Then** it returns `CLARIFY` rather than choosing a
   reminder or time.

### Edge Cases

- The prompt includes a date but no time, or a time but no date.
- The prompt uses a relative date or time but the trusted reference date, time, or
  timezone needed to resolve it is unavailable.
- The prompt contains conflicting dates, times, or reminder actions.
- The user requests a reminder change but multiple existing reminders could match.
- The prompt contains no reminder task or no recognizable reminder intent.
- The request contains a date or time that cannot be represented unambiguously.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The agent MUST return exactly one valid JSON object for every
  processed prompt, with exactly four fields: `task`, `datetime`, `intent`, and
  `message`.
- **FR-002**: The `task`, `datetime`, and `message` values MUST be strings. The
  `intent` value MUST be exactly one of `CREATE`, `RESCHEDULE`, `SNOOZE`, or
  `CLARIFY`. The object MUST NOT contain additional fields.
- **FR-003**: The agent MUST NOT emit Markdown, code fences, comments, or prose
  outside the JSON object.
- **FR-004**: For a create request, the agent MUST use `CLARIFY` if the task, date,
  or time is missing or cannot be resolved unambiguously. It MUST NOT guess a
  missing detail.
- **FR-005**: The agent MUST use `CLARIFY` for any request whose task, action,
  affected reminder, or required datetime information cannot be determined
  reliably.
- **FR-006**: The agent MUST NOT invent dates or times. It MUST resolve relative
  dates and times only from the user's wording and trusted reference date, time,
  and timezone context when those are needed. If required context is unavailable,
  it MUST ask for clarification.
- **FR-007**: When a datetime is resolved, the agent MUST return it in ISO 8601
  format with a timezone offset. When it cannot be resolved, `datetime` MUST be an
  empty string.
- **FR-008**: When the task cannot be identified, `task` MUST be an empty string.
  For `CLARIFY` responses, `message` MUST state the missing or ambiguous
  information and ask a focused question.
- **FR-009**: The agent MUST use `CREATE`, `RESCHEDULE`, or `SNOOZE` only when the
  requested action and its required task, reminder identity, and target datetime
  are sufficiently clear.
- **FR-010**: The agent MUST provide a concise user-facing `message` that confirms
  a clearly interpreted action or requests the information needed to proceed.
- **FR-011**: The agent MUST evaluate each response for JSON validity, exact field
  names and types, allowed intent values, clarification behavior, and unsupported
  date/time generation against representative and adversarial prompts.

### Key Entities

- **Reminder request**: The user's unstructured text describing an action, task,
  and any date/time information.
- **Reminder response**: The JSON object containing the task, datetime, intent,
  and user-facing message.
- **Temporal context**: Trusted reference date, time, and timezone information
  used only when needed to resolve relative temporal wording.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of responses in the contract evaluation set parse as one JSON
  object and contain exactly the four required fields with the required types.
- **SC-002**: 100% of evaluation cases with a missing or unresolved task, date, or
  time return `CLARIFY` and do not invent the missing detail.
- **SC-003**: 0 evaluation cases produce an unsupported or fabricated date or
  time.
- **SC-004**: At least 90% of clear, in-scope prompts in a representative
  evaluation set produce the expected intent and task/datetime values.
- **SC-005**: Every clarification response in the evaluation set identifies the
  missing or ambiguous information in its message.

## Assumptions

- The feature interprets prompts and returns a response; creating a persistent
  reminder or delivering a notification is outside this feature's scope.
- The user-facing datetime representation is ISO 8601 with an explicit timezone
  offset. A timezone may come from the user or trusted runtime context; the
  agent does not silently assume one.
- A request to snooze or reschedule must identify the affected reminder in the
  prompt or trusted context. Otherwise, the agent asks the user to identify it.
- If an incomplete request has some identifiable information, the agent retains
  that information in the corresponding string field; a field with no
  determinable value is an empty string.
- The response `message` is used for a concise confirmation or clarification
  question and does not replace the structured fields.

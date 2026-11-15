# Data Model: Reminder Agent

## Reminder Prompt

Represents one unstructured user input.

| Field | Type | Constraints |
|---|---|---|
| `text` | string | Raw prompt; preserve the text for interpretation. An empty or unusable prompt results in clarification. |

There is no persistence lifecycle in this feature. A prompt produces one response.

## Reminder Intent

An enum with exactly four wire values:

- `CREATE`: create a reminder from a fully resolved request.
- `RESCHEDULE`: change an identified reminder to a fully resolved target datetime.
- `SNOOZE`: postpone an identified reminder to a fully resolved datetime.
- `CLARIFY`: request missing or ambiguous information.

Only `CLARIFY` may represent an unresolved task or datetime. It is the required
intent when required information cannot be grounded.

## Reminder Response

The public response is exactly the object defined in
[reminder-response.schema.json](./contracts/reminder-response.schema.json).

| Field | Type | Constraints |
|---|---|---|
| `task` | string | Identified task text; empty only when it cannot be determined. |
| `datetime` | string | ISO 8601 date-time with a timezone offset, or empty when unresolved. |
| `intent` | Reminder Intent | Exactly one of the four enum values above. |
| `message` | string | Concise confirmation or a focused clarification question. |

The response contains no identifiers, debug details, confidence values, or other
fields. For `CREATE`, `RESCHEDULE`, and `SNOOZE`, both `task` and `datetime` must
be non-empty and valid. For `CLARIFY`, the known task and datetime may be retained;
unknown values are empty strings.

## Temporal Context

Trusted, request-scoped information used to resolve relative expressions. It is
not serialized in the response.

| Field | Type | Constraints |
|---|---|---|
| `reference_time` | timezone-aware datetime | Injected clock value; required only when relative wording needs a reference instant. |
| `timezone` | IANA timezone or explicit offset | Must be supplied or unambiguously specified by the user when local-time interpretation requires it. |

Missing context, ambiguous daylight-saving transitions, and nonexistent local
times result in `CLARIFY`. The system must not substitute the host's implicit
clock or timezone.

## Interpreter Output

The interpreter seam returns raw JSON text, which is untrusted until parsed and
validated as a `ReminderResponse`. Validation failures are surfaced as failures;
the processor must not repair or silently replace malformed output.

## Relationships and State

- One `Reminder Prompt` produces one `Reminder Response`.
- The `Reminder Response` does not persist or mutate an existing reminder.
- Rescheduling and snoozing are represented as classified requests only; a
  reminder store or notification-delivery state machine is outside this scope.

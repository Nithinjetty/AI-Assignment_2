# Research: Reminder Agent

## Decisions

### Python and validation

- **Decision**: Target Python 3.10+ and Pydantic v2 (`pydantic>=2,<3`), using
  v2 APIs consistently.
- **Rationale**: This meets the requested runtime while using a current
  validation API. `ConfigDict(strict=True, extra="forbid")` makes response
  parsing reject coercions and unexpected fields. Pydantic verifies structure
  and types, but does not prove that the interpretation of the user's wording
  is correct; behavioral policy tests remain necessary.
- **Alternatives considered**: Supporting Pydantic v1 and v2 would add
  compatibility handling without a stated need. Provider-side schema-constrained
  generation may help formatting later but does not replace local validation.
- **References**:
  - [Pydantic migration guide](https://docs.pydantic.dev/latest/migration/)
  - [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
  - [Pydantic model validation](https://docs.pydantic.dev/latest/concepts/models/#validating-data)
  - [Pydantic model configuration](https://docs.pydantic.dev/latest/api/config/)

### JSON response boundary

- **Decision**: Accept one raw JSON response from the interpreter seam and
  validate it directly against a strict model with extra fields forbidden.
  Serialize only the validated response.
- **Rationale**: Rejecting malformed JSON, prose surrounding JSON, unknown keys,
  and type mismatches prevents success-shaped fallback behavior. Separate
  semantic checks enforce required date/time grounding and `CLARIFY` behavior.
- **Alternatives considered**: Extracting a JSON substring, repairing output, or
  silently defaulting fields can hide invalid model output and are not allowed.
- **Reference**: [Pydantic models and validation](https://docs.pydantic.dev/latest/concepts/models/#validating-data)

### Temporal interpretation

- **Decision**: Inject a trusted reference clock and explicit timezone. Resolve
  relative dates against that context, normalize only aware datetimes, and
  clarify when required information or a DST interpretation is unresolved.
  Include `tzdata` to provide IANA timezone data on platforms that lack a system
  timezone database. Use `datetime.timezone.utc` for Python 3.10 compatibility.
- **Rationale**: Naive datetimes do not identify a unique instant. An injected
  clock keeps evaluation repeatable and avoids implicit dependence on the
  machine's clock or timezone.
- **Alternatives considered**: Using local machine time or assuming a timezone
  can fabricate reminder dates/times. Silently selecting one side of an
  ambiguous DST transition is unsafe.
- **References**:
  - [Python aware and naive datetime objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects)
  - [Python zoneinfo](https://docs.python.org/3/library/zoneinfo.html)

### Interpreter seam and mock

- **Decision**: Define a typed `Protocol` for an interpreter callable that
  receives the prompt and trusted context and returns raw JSON text. Provide a
  deterministic local mock for fixtures. Keep business policy and temporal
  normalization outside the mock.
- **Rationale**: A small structural interface permits test substitution without
  tying processing code to a vendor SDK. A raw string exercises the same
  validation boundary as a future provider response.
- **Alternatives considered**: A direct callable type is adequate if only one
  function is needed; a protocol makes the input and output contract clearer.
  No live model/provider integration is included in this feature.
- **Reference**: [Python typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)

### Evaluation harness

- **Decision**: Create a standalone `.harness/evaluate.py` command using a fixed
  fixture set, mock interpreter, and injected clock/timezone. Make paths
  independent of the current working directory. Report per-case and overall
  results, and exit non-zero when any release-blocking case fails.
- **Rationale**: Deterministic fixtures avoid dependence on model availability,
  network access, and wall-clock timing. Keep real-provider evaluations, if
  added later, separate and explicitly opt-in.
- **Alternatives considered**: A live-model-only evaluation is nondeterministic
  and cannot be the release-blocking regression suite. A one-off inline script
  is less reusable than a named runner and fixtures.
- **References**:
  - [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html)
  - [Python argparse](https://docs.python.org/3/library/argparse.html)
  - [pytest monkeypatching](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)

## Evaluation Coverage

Pin cases for explicit date/time, relative times around midnight, missing
task/date/time, absent or conflicting timezone context, ambiguous and nonexistent
DST local times, malformed JSON, extra prose, unknown keys, incorrect types, and
all four intent values. Check both JSON/schema compliance and the expected
behavior; schema validation alone cannot detect an invented but well-formed
datetime.

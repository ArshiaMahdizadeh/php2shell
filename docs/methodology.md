# Methodology

## CVE-2026-109618 — OOM longjmp

PHP's out-of-memory handler uses `longjmp()` to unwind. The request
allocator state at the jump point can leave request memory uninitialized.
Probe: POST bodies of increasing size to push past `memory_limit`;
observe for transport resets, 5xx clustering, and response-length variance
between identical requests.

## CVE-2026-109619 — fatal longjmp

Fatal error handling also `longjmp()`s. Global memory can end up pointing
to freed regions, later read/branched by subsequent requests on the same
worker. Probe: fatal-shape request, then benign follow-up on the same
connection; observe follow-up anomalies and latency stalls.

## Confidence scoring

Both triggers emit a confidence score in [0, 1]. Score >= 0.75 is
CONFIDENT, [0.55, 0.75) SUSPECTED, below is CLEAN. See
`php2shell/triggers/` for exact weights.

## Non-goals

This tool does not spray exploits blindly. Exploit mode requires an
explicit per-target authorization attestation.
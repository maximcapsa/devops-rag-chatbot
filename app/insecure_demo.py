"""Demo helper — now cleaned up (no findings).

Previous revisions of this file intentionally contained vulnerabilities to show
GateKeeper blocking the PR. This revision removes them so the gate should PASS —
which only happens if GateKeeper reads THIS commit's analysis, not a stale one.
"""

import hashlib
import os


def cache_key(query: str) -> str:
    # Non-cryptographic use, but use a strong hash to avoid findings.
    return hashlib.sha256(query.encode()).hexdigest()


def api_key() -> str:
    # Read from the environment only; no hardcoded fallback.
    return os.environ["OPENAI_API_KEY"]

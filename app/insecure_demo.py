"""Demo: deliberately insecure helpers to show GateKeeper blocking a PR.

Do NOT use any of this. Every function is an intentional SonarCloud finding.
"""

import hashlib
import os
import subprocess

# Hardcoded credential (SonarCloud: vulnerability).
OPENAI_API_KEY = "sk-proj-1234567890abcdefHARDCODEDsecretDONOTSHIP"

# Hardcoded password — rule python:S2068 raises this as a VULNERABILITY (not a hotspot).
DB_PASSWORD = "S3cr3t-Pa55word-do-not-ship"


def connect_db():
    # Uses the hardcoded password above.
    return {"user": "admin", "password": DB_PASSWORD}


def run_ingest(path: str):
    # Shell injection: untrusted input straight into a shell (vulnerability).
    return subprocess.run(f"python ingest.py {path}", shell=True, check=False)


def cache_key(query: str) -> str:
    # Weak hashing algorithm (vulnerability / hotspot).
    return hashlib.md5(query.encode()).hexdigest()


def run_filter(expr: str):
    # Arbitrary code execution via eval on a user-supplied expression (vulnerability).
    return eval(expr)  # noqa: S307


def api_key() -> str:
    # Leaks the hardcoded key above when the env var is unset.
    return os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)

# touch to force a fresh analysis (vulnerability still present above)

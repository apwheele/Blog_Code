"""Core secret-redaction logic shared by the Claude Code hook and the SDK demo.

This module has no side effects on import. It exposes two layers of detection:

1. Exact-value matching: literal secret *values* pulled from environment variables
   (or a local ``.secrets`` file). This has zero false positives -- we only redact
   strings we already know are secret.
2. Pattern matching: regexes for common API-key *shapes* (Anthropic, OpenAI, AWS,
   GitHub, Stripe, Google, generic Bearer tokens). This catches keys we were not
   told about up front, at the cost of occasional false positives.

Everything is replaced with the placeholder ``***REDACTED***``.
"""

from __future__ import annotations

import os
import re

PLACEHOLDER = "***REDACTED***"

# Minimum length for an exact-match secret value. Short env vars (e.g. "1", "true")
# would otherwise be redacted everywhere and wreck normal commands.
MIN_SECRET_LEN = 8

# Environment variables whose *values* we treat as secrets to redact verbatim.
# ANTHROPIC_API_KEY is the headline case for this project; the rest are common
# providers a crime-analysis / data shop might have configured.
DEFAULT_SECRET_ENV_VARS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "STRIPE_API_KEY",
    "GOOGLE_API_KEY",
    "HF_TOKEN",
    "DEMO_SECRET",  # used only by demo_sdk.py with a fake value
]

# Regexes for common key shapes. Kept deliberately conservative to limit false
# positives. Each pattern matches the whole token so we replace it wholesale.
SECRET_PATTERNS = [
    # Anthropic keys, e.g. sk-ant-api03-XXddd... (also matches our fake demo key).
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"),
    # OpenAI style keys: sk-... and the newer sk-proj-... (avoid matching sk-ant-).
    re.compile(r"sk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{16,}"),
    # AWS access key id.
    re.compile(r"AKIA[0-9A-Z]{16}"),
    # GitHub personal/OAuth/server/refresh tokens.
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    # Stripe secret keys.
    re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}"),
    # Google API keys.
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    # Generic bearer tokens in an Authorization header.
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.=]{16,}"),
]


def load_known_secrets(env_vars: list[str] | None = None,
                       secrets_file: str | None = None) -> list[str]:
    """Collect literal secret values to redact by exact match.

    Pulls from the named environment variables and, optionally, a newline-delimited
    ``secrets_file`` (one secret per line, ``#`` comments allowed). Values shorter
    than ``MIN_SECRET_LEN`` are ignored. Longer secrets are sorted first so we redact
    the most specific (longest) match before any substring of it.
    """
    names = env_vars if env_vars is not None else DEFAULT_SECRET_ENV_VARS
    found: set[str] = set()

    for name in names:
        val = os.environ.get(name, "")
        if val and len(val) >= MIN_SECRET_LEN:
            found.add(val)

    if secrets_file and os.path.isfile(secrets_file):
        with open(secrets_file, "r", encoding="utf-8") as fh:
            for line in fh:
                val = line.strip()
                if val and not val.startswith("#") and len(val) >= MIN_SECRET_LEN:
                    found.add(val)

    # Longest first so "abc123def456" is redacted before a shorter overlapping value.
    return sorted(found, key=len, reverse=True)


def redact_text(text: str, known: list[str] | None = None) -> tuple[str, int]:
    """Redact secrets from a single string.

    Returns ``(new_text, count)`` where ``count`` is the number of replacements made.
    Exact known-value matches run first, then regex shape matches.
    """
    if not isinstance(text, str) or not text:
        return text, 0

    known = known if known is not None else load_known_secrets()
    count = 0

    # 1) Exact known values (no false positives).
    for secret in known:
        if secret and secret in text:
            count += text.count(secret)
            text = text.replace(secret, PLACEHOLDER)

    # 2) Pattern shapes (may catch unknown keys).
    for pattern in SECRET_PATTERNS:
        text, n = pattern.subn(PLACEHOLDER, text)
        count += n

    return text, count


def redact_tool_input(tool_input, known: list[str] | None = None) -> tuple[object, int]:
    """Recursively redact every string value in a nested structure.

    Used for both tool *inputs* and tool *outputs* (PostToolUse). Handles nested
    dicts and lists (e.g. Bash stdout strings, WebFetch response bodies).
    Returns ``(new_structure, total_count)``. The original is not mutated.
    """
    known = known if known is not None else load_known_secrets()

    if isinstance(tool_input, str):
        return redact_text(tool_input, known)

    if isinstance(tool_input, dict):
        new_dict = {}
        total = 0
        for key, value in tool_input.items():
            new_value, n = redact_tool_input(value, known)
            new_dict[key] = new_value
            total += n
        return new_dict, total

    if isinstance(tool_input, list):
        new_list = []
        total = 0
        for item in tool_input:
            new_item, n = redact_tool_input(item, known)
            new_list.append(new_item)
            total += n
        return new_list, total

    # Numbers, booleans, None, etc. -- nothing to redact.
    return tool_input, 0

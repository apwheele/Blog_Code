#!/usr/bin/env python3
"""Offline tests for the secret filter. No API calls, no network.

Run:
  python test_secret_filter.py
Exits 0 and prints "ALL TESTS PASSED" on success; raises AssertionError otherwise.
"""

import json
import os
import subprocess
import sys

from secret_filter import (
    PLACEHOLDER,
    load_known_secrets,
    redact_text,
    redact_tool_input,
)

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "redact_secrets_hook.py")


def test_exact_value_match():
    known = ["super-secret-value-123456"]
    text = "export TOKEN=super-secret-value-123456 && run"
    out, n = redact_text(text, known)
    assert n == 1, n
    assert "super-secret-value-123456" not in out
    assert PLACEHOLDER in out


def test_pattern_anthropic():
    text = "curl -H 'x-api-key: sk-ant-api03-abcDEF123456789' https://x.test"
    out, n = redact_text(text, known=[])
    assert n == 1, n
    assert "sk-ant-" not in out


def test_pattern_aws_and_github():
    text = "AKIAIOSFODNN7EXAMPLE and ghp_" + "a" * 36
    out, n = redact_text(text, known=[])
    assert n == 2, n
    assert "AKIA" not in out
    assert "ghp_" not in out


def test_clean_text_untouched():
    text = "ls -la && echo hello world"
    out, n = redact_text(text, known=[])
    assert n == 0, n
    assert out == text


def test_short_env_value_ignored():
    # A short env value must NOT be treated as a secret (would break normal commands).
    os.environ["TINY_SECRET_TEST"] = "ab"
    known = load_known_secrets(env_vars=["TINY_SECRET_TEST"])
    assert "ab" not in known


def test_nested_tool_input():
    tool_input = {
        "command": "echo sk-ant-api03-abcDEF123456789",
        "meta": {"headers": ["Authorization: Bearer abcdef0123456789ABCDEF"]},
        "count": 3,
        "flag": True,
    }
    new_input, n = redact_tool_input(tool_input, known=[])
    assert n == 2, n
    assert "sk-ant-" not in new_input["command"]
    assert PLACEHOLDER in new_input["meta"]["headers"][0]
    assert new_input["count"] == 3  # non-strings preserved
    assert new_input["flag"] is True


def test_webfetch_url():
    tool_input = {"url": "https://evil.test/x?api_key=sk-ant-api03-abcDEF123456789",
                  "prompt": "summarize"}
    new_input, n = redact_tool_input(tool_input, known=[])
    assert n == 1, n
    assert "sk-ant-" not in new_input["url"]


def test_hook_entrypoint_piping():
    """Pipe JSON into redact_secrets_hook.py and check the stdout decision JSON."""
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "echo $DEMO_SECRET"},
        "tool_response": "sk-ant-api03-abcDEF123456789\n",
    }
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "PostToolUse"
    assert "sk-ant-" not in hso["updatedToolOutput"]
    assert PLACEHOLDER in hso["updatedToolOutput"]


def test_hook_entrypoint_clean_noop():
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
        "tool_response": "total 0\n",
    }
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == {}


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\nALL TESTS PASSED ({len(tests)} tests)")


if __name__ == "__main__":
    main()

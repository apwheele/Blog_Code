#!/usr/bin/env python3
"""Claude Code PostToolUse hook entry point: redact secrets after a tool runs.

Wire this up in settings.json (see settings.example.json). Claude Code invokes it
after every matched tool call succeeds, passing the tool request + result as JSON
on stdin:

    {"hook_event_name": "PostToolUse", "tool_name": "Bash",
     "tool_input": {"command": "echo $DEMO_SECRET"},
     "tool_response": "sk-ant-...\\n"}

If we find secrets, we print a PostToolUse decision that *rewrites* the tool
output with the secrets replaced by ``***REDACTED***`` so Claude never sees them:

    {"hookSpecificOutput": {"hookEventName": "PostToolUse",
       "updatedToolOutput": "***REDACTED***\\n"},
     "systemMessage": "..."}

If nothing matches we print ``{}`` so the normal flow is untouched.

Note: the tool has already executed -- this cannot undo side effects (a curl that
already left the machine still left). It only stops the secret from flowing back
into the model context / transcript.

Design choice: this hook is *fail-open*. Any error -> print ``{}`` and exit 0, so a
bug here can never block the session. The trade-off (a crash silently disables
redaction) is called out as a limitation in README.md.
"""

import json
import sys

from secret_filter import load_known_secrets, redact_tool_input


def _tool_output_from_payload(data: dict):
    """PostToolUse payloads may use tool_response or tool_output depending on version."""
    if "tool_response" in data:
        return data["tool_response"]
    return data.get("tool_output", "")


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("{}")
        return 0

    data = json.loads(raw)
    tool_name = data.get("tool_name", "tool")
    tool_output = _tool_output_from_payload(data)

    known = load_known_secrets()
    new_output, count = redact_tool_input(tool_output, known)

    if count == 0:
        print("{}")
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": new_output,
        },
        "systemMessage": f"[secret-filter] Redacted {count} secret(s) from {tool_name} output",
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

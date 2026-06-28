#!/usr/bin/env python3
"""Self-contained demo: run Claude headless via the Agent SDK with the redaction hook.

This proves the same redaction logic end to end without touching your global Claude
Code settings. We:

  1. Plant a FAKE secret in the environment (DEMO_SECRET). No real key is ever used.
  2. Register an in-process PreToolUse hook that scrubs secrets from tool inputs.
  3. Ask Claude (headless) to run a shell command that echoes the secret.
  4. Print what the hook did, so you can see the fake key replaced with ***REDACTED***.

Requirements:
  - pip install claude-agent-sdk   (see requirements.txt)
  - The `claude` CLI installed and logged in, OR an ANTHROPIC_API_KEY in the env.

Run:
  python demo_sdk.py
"""

import asyncio
import os

# Plant a fake secret BEFORE importing the filter helpers so it is picked up as a
# known value. This string is not a real credential.
FAKE_SECRET = "sk-ant-FAKE-demo-0000000000-not-a-real-key"
os.environ["DEMO_SECRET"] = FAKE_SECRET

from secret_filter import load_known_secrets, redact_tool_input  # noqa: E402

from claude_agent_sdk import (  # noqa: E402
    ClaudeAgentOptions,
    HookMatcher,
    query,
)

# Count how many redactions the hook performed across the run.
REDACTION_LOG: list[str] = []


async def redact_hook(input_data, tool_use_id, context):
    """PreToolUse hook callback: rewrite tool input with secrets redacted."""
    tool_name = input_data.get("tool_name", "tool")
    tool_input = input_data.get("tool_input", {})

    known = load_known_secrets()
    new_input, count = redact_tool_input(tool_input, known)

    if count == 0:
        return {}

    REDACTION_LOG.append(f"{tool_name}: redacted {count} secret(s)")
    print(f"\n[hook] BEFORE: {tool_input}")
    print(f"[hook] AFTER : {new_input}\n")

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": new_input,
            "permissionDecisionReason": f"Redacted {count} secret(s) from {tool_name} input",
        },
        "systemMessage": f"[secret-filter] Redacted {count} secret(s) from {tool_name} call",
    }


async def main() -> None:
    options = ClaudeAgentOptions(
        # Limit tools to keep the demo cheap and predictable. Uses your default model
        # (Opus). Note: smaller models (e.g. Haiku) may refuse to echo a key-like
        # string outright, so the hook never gets a tool call to redact.
        allowed_tools=["Bash"],
        permission_mode="acceptEdits",
        max_turns=2,
        hooks={
            "PreToolUse": [HookMatcher(matcher="Bash", hooks=[redact_hook])],
        },
    )

    prompt = (
        f"Run this exact shell command and report the output: "
        f"echo 'my key is {FAKE_SECRET}'"
    )

    print("=" * 70)
    print("DEMO: asking Claude (headless) to echo a FAKE secret in a Bash command.")
    print("The PreToolUse hook should scrub it before the command runs.")
    print("=" * 70)

    # The redaction happens inside the hook (before the tool runs), so the proof is
    # already captured even if a later model turn errors (e.g. a 429 rate limit).
    # We skip the SDK's verbose raw message objects; the hook prints the BEFORE/AFTER.
    try:
        async for message in query(prompt=prompt, options=options):
            for block in getattr(message, "content", []) or []:
                if type(block).__name__ == "ToolUseBlock":
                    print(f"[claude] wants to run {block.name}: {block.input.get('command', block.input)}")
                elif type(block).__name__ == "TextBlock":
                    print(f"[claude] {block.text}")
    except Exception as exc:
        print(f"\n[note] run ended early: {exc}")

    print("\n" + "=" * 70)
    if REDACTION_LOG:
        print("RESULT: hook fired ->")
        for line in REDACTION_LOG:
            print(f"  - {line}")
        print(f"The fake key ({FAKE_SECRET}) never reached the executed command.")
    else:
        print("RESULT: hook did not fire (Claude may have refused or reworded the "
              "command -- see the 'How it works'/limitations notes in README.md).")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

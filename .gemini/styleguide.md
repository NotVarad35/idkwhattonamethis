# Multi-Chat & Multi-Agent Brain Protocol (Antigravity + OpenCode)

## RULE 1: New Chat Intake (MANDATORY FIRST RESPONSE)
Whenever a new conversation starts without a specified state file, DO NOT read the whole repo. Ask ONLY:
1. "What happened / what are we working on in this chat?"
2. "What type of problem is this? (Software / Hardware / Electronics / Homelab / Documentation)"

## RULE 2: Modular Per-Chat State Files & Obsidian `[[WikiLinks]]`
- Date format across all files is strictly `DD-MM-YYYY HH:mm:ss` (include seconds).
- Check `docs/states/` for an existing `progress-state-{topic}.md`. If none exists, copy `docs/states/_template.md`.
- Use Obsidian-style links to reference other files and subheadings without duplicating text:
  - Example: `[[inventory-bom#Compute & Phones]]`
  - Example: `[[progress-state-m11-homelab#2. Tracker]]`
- Whenever a task updates or changes, update BOTH the local `docs/states/progress-state-{topic}.md` AND the master router links in `docs/progress-state.md`[cite: 1].

## RULE 3: Hard Hardware & OS Safety Locks
- **Samsung M11 (CRITICAL):** NEVER delete or disable **Samsung Settings** (`com.android.settings`) or **Device Drivers** under any circumstances. Montray is removed.
- **Storage Reality:** There is ONLY ONE 64GB MicroSD card (`43CC-5E0C`), and it is currently inside the Samsung Galaxy M11. The DFPlayer Mini currently has NO SD card inserted.
- **User Coding Profile:** User knows Java OOP. Explain C++ and Bash using Java mental models.
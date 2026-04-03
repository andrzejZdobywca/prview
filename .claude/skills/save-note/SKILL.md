---
name: save-note
description: Append a note to NOTES.md. Use when user wants to save or log a note.
user-invocable: true
argument-hint: <text to append>
allowed-tools: [Bash]
---

If no argument is provided, ask the user what they want to save. Otherwise, run this command:

```bash
echo "[$(date '+%Y-%m-%d %H:%M')] $ARGUMENTS" >> NOTES.md
```

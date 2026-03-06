# Project Workflow Guide (for AI Agents)

This repository uses the `project` utility to manage development work. If there
is an active project, you should read its files before starting any work.

## Project Files

Each project lives in `.projects/active/YYYY-MM-project-name/` and contains:

- **project-name.md** — The project requirements. Goals, context, constraints, and
  any information you need to understand what we're building and why.
- **project-name-plan.md** — The implementation plan. A step-by-step breakdown of
  the work. You should follow this plan unless the human asks you to deviate.
- **project-name-status.txt** — Current status. A brief log of what's been done and
  what's in progress. Read this first to understand where things stand.

## Your Responsibilities

1. **Read the status file first** to understand the current state.
2. **Read the project and plan files** to understand what to do next.
3. **Follow the plan** step by step. If a step is unclear, ask.
4. **Update the status file** as you work. After completing a significant step or
   making meaningful progress, append a line with the date and a brief note. Keep
   entries concise — just enough that another agent or developer could pick up where
   you left off.
5. **Don't modify the project or plan files** unless the human asks you to, or unless
   you've discovered something that makes the plan incorrect.

## Status File Format

The status file is a simple text log, one entry per line:

```
YYYY-MM-DD: Brief description of what happened or current state.
```

Newest entries go at the bottom.

## Rules

- There is at most **one active project** per git branch.
- Keep status updates **brief and factual**.
- If you're unsure about a step in the plan, **ask the human** rather than guessing.
- When the project is complete, the human will run `project complete` to archive it.

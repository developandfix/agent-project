# project-utility: Implementation Plan

## Overview

Python package installable via pip. No external dependencies — stdlib only.
Provides a `project` CLI command.

## Project Layout

```
project/
  README.md
  pyproject.toml
  src/
    project_utility/
      __init__.py
      cli.py              # entry point, argparse, subcommand dispatch
      core.py             # business logic (init, status, complete)
      templates/
        project-workflow.md   # agent documentation file
        project.md.tmpl       # template for new project files
        plan.md.tmpl          # template for new plan files
  .projects/
    ...
```

## Packaging

`pyproject.toml` using PEP 621 metadata:

- `[project.scripts]` maps `project` → `project_utility.cli:main`
- `pip install .` for system-wide install
- `pip install -e .` for development
- Works with system Python, venv, pyenv, nvm-managed Python, etc.
- No runtime dependencies beyond Python 3.9+

## Core Mechanics

- The script finds the git repo root via `git rev-parse --show-toplevel` and uses
  `.projects/` relative to that.
- Active project detection: glob `.projects/active/*/` — there should be 0 or 1 entries.
- Project directory naming: `YYYY-MM-project-name` (date prefix from creation date).
- Project name is slugified (lowercased, spaces/special chars replaced with hyphens).

## Agent Documentation

A bundled file `project-workflow.md` serves as the canonical reference for AI agents
on how to use the project workflow. It covers:

- The project lifecycle (planning → implementation → review → completion)
- File conventions (what goes in each file, how to update status)
- How to read and follow the plan
- When and how to update status
- Rules (one active project per branch, keep status current, etc.)

This file is bundled as package data in `src/project_utility/templates/`.

## Commands

### 1. `project init "project name"`

- Find git repo root.
- Check no active project exists already; error if one does.
- Create `.projects/active/` and `.projects/completed/` if they don't exist.
- Slugify the project name.
- Create project directory: `.projects/active/YYYY-MM-slug/`
- Create `slug.md` from template (project name, date, placeholder sections).
- Create `slug-status.txt` with initial "Planning phase" entry.
- Create `slug-plan.md` from template.
- Copy `project-workflow.md` into `.claude/` in the repo root (create dir if needed).
- Check for CLAUDE.md in repo root. If it exists, append a pointer to the workflow
  doc and active project (if not already present). If it doesn't exist, create one.
- Print summary of what was created.

### 2. `project status`

- Find git repo root.
- Look for an active project in `.projects/active/`.
- If none: print "No active project." and exit.
- If found: print the project name and the contents of the status file.

### 3. `project complete`

- Find git repo root.
- Find the active project; error if none.
- Get the latest git commit hash and short message via `git log -1 --format=...`.
- Append a completion note with timestamp and commit ref to the status file.
- Move the project directory from `active/` to `completed/`.
- Remove the active project block from CLAUDE.md.
- Print confirmation.

## CLAUDE.md Integration

The `init` command adds a block like this to CLAUDE.md:

```
<!-- project-utility:active -->
## Active Project

See .claude/project-workflow.md for full workflow documentation.

Current project files:
- Project: .projects/active/{dir}/{slug}.md
- Plan: .projects/active/{dir}/{slug}-plan.md
- Status: .projects/active/{dir}/{slug}-status.txt
<!-- /project-utility:active -->
```

The `complete` command removes this block. Using HTML comments as markers makes
it easy to find and replace programmatically.

## Implementation Steps

1. **Set up package structure** — `pyproject.toml`, package dirs, entry point wiring.
2. **Write agent workflow doc** — `project-workflow.md` template.
3. **Implement helpers** — repo root detection, active project finding, slugify.
4. **Implement `init`** — directory creation, template files, `.claude/` setup, CLAUDE.md.
5. **Implement `status`** — active project detection and status display.
6. **Implement `complete`** — status update, directory move, CLAUDE.md cleanup.
7. **Test** — manual testing against this repo, verify pip install works.
8. **Polish** — error messages, edge cases (not in a git repo, dirty name input, etc.).

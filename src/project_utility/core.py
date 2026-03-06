"""Core business logic for the project utility."""

import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

CLAUDE_BLOCK_START = "<!-- project-utility:active -->"
CLAUDE_BLOCK_END = "<!-- /project-utility:active -->"


def get_repo_root() -> Path:
    """Find the git repository root."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SystemExit("Error: not inside a git repository.")
    return Path(result.stdout.strip())


def slugify(name: str) -> str:
    """Convert a project name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def find_active_project(repo_root: Path) -> Path | None:
    """Return the active project directory, or None."""
    active_dir = repo_root / ".projects" / "active"
    if not active_dir.exists():
        return None
    projects = [p for p in active_dir.iterdir() if p.is_dir()]
    if not projects:
        return None
    if len(projects) > 1:
        raise SystemExit(
            f"Error: multiple active projects found: {', '.join(p.name for p in projects)}"
        )
    return projects[0]


def get_project_slug(project_dir: Path) -> str:
    """Extract the slug from a project directory name (strip YYYY-MM- prefix)."""
    name = project_dir.name
    # Strip YYYY-MM- prefix if present
    match = re.match(r"\d{4}-\d{2}-(.*)", name)
    return match.group(1) if match else name


def init_project(name: str) -> None:
    """Initialize a new project."""
    repo_root = get_repo_root()

    existing = find_active_project(repo_root)
    if existing:
        raise SystemExit(
            f"Error: active project already exists: {existing.name}\n"
            "Complete it with 'project complete' before starting a new one."
        )

    slug = slugify(name)
    if not slug:
        raise SystemExit("Error: project name is empty after slugification.")

    today = date.today()
    dir_name = f"{today.strftime('%Y-%m')}-{slug}"
    project_dir = repo_root / ".projects" / "active" / dir_name

    # Create directories
    project_dir.mkdir(parents=True, exist_ok=True)
    (repo_root / ".projects" / "completed").mkdir(parents=True, exist_ok=True)

    # Create project file from template
    template_vars = {"name": name, "date": today.isoformat()}

    project_file = project_dir / f"{slug}.md"
    template = (TEMPLATES_DIR / "project.md.tmpl").read_text()
    project_file.write_text(template.format(**template_vars))

    # Create plan file from template
    plan_file = project_dir / f"{slug}-plan.md"
    template = (TEMPLATES_DIR / "plan.md.tmpl").read_text()
    plan_file.write_text(template.format(**template_vars))

    # Create status file
    status_file = project_dir / f"{slug}-status.txt"
    status_file.write_text(f"{today.isoformat()}: Project created. Status: Planning phase.\n")

    # Copy workflow doc to .claude/
    claude_dir = repo_root / ".claude"
    claude_dir.mkdir(exist_ok=True)
    workflow_src = TEMPLATES_DIR / "project-workflow.md"
    workflow_dst = claude_dir / "project-workflow.md"
    shutil.copy2(workflow_src, workflow_dst)

    # Update CLAUDE.md
    _update_claude_md(repo_root, name, dir_name, slug)

    print(f"Project '{name}' initialized.")
    print(f"  Directory: .projects/active/{dir_name}/")
    print(f"  Project:   .projects/active/{dir_name}/{slug}.md")
    print(f"  Plan:      .projects/active/{dir_name}/{slug}-plan.md")
    print(f"  Status:    .projects/active/{dir_name}/{slug}-status.txt")
    print(f"  Workflow:  .claude/project-workflow.md")


def show_status() -> None:
    """Show the active project status."""
    repo_root = get_repo_root()
    project_dir = find_active_project(repo_root)

    if not project_dir:
        print("No active project.")
        return

    slug = get_project_slug(project_dir)
    status_file = project_dir / f"{slug}-status.txt"

    print(f"Active project: {project_dir.name}")
    print()
    if status_file.exists():
        print(status_file.read_text().rstrip())
    else:
        print("(no status file found)")


def complete_project() -> None:
    """Complete the active project."""
    repo_root = get_repo_root()
    project_dir = find_active_project(repo_root)

    if not project_dir:
        raise SystemExit("Error: no active project to complete.")

    slug = get_project_slug(project_dir)
    status_file = project_dir / f"{slug}-status.txt"

    # Get latest commit info
    result = subprocess.run(
        ["git", "log", "-1", "--format=%h %s"],
        capture_output=True, text=True,
    )
    commit_info = result.stdout.strip() if result.returncode == 0 else "(no commits)"

    # Update status file
    today = date.today().isoformat()
    with open(status_file, "a") as f:
        f.write(f"{today}: Project completed. Last commit: {commit_info}\n")

    # Move to completed
    completed_dir = repo_root / ".projects" / "completed"
    completed_dir.mkdir(parents=True, exist_ok=True)
    dest = completed_dir / project_dir.name
    shutil.move(str(project_dir), str(dest))

    # Clean up CLAUDE.md
    _remove_claude_md_block(repo_root)

    print(f"Project '{project_dir.name}' completed and moved to .projects/completed/")


def _resolve_claude_md(repo_root: Path) -> Path:
    """Return the CLAUDE.md path to use: root if it exists, else .claude/."""
    root_file = repo_root / "CLAUDE.md"
    if root_file.exists():
        return root_file
    return repo_root / ".claude" / "CLAUDE.md"


def _update_claude_md(repo_root: Path, name: str, dir_name: str, slug: str) -> None:
    """Add the active project block to CLAUDE.md."""
    claude_md = _resolve_claude_md(repo_root)

    block = (
        f"{CLAUDE_BLOCK_START}\n"
        f"## Active Project\n"
        f"\n"
        f"See .claude/project-workflow.md for full workflow documentation.\n"
        f"\n"
        f"Current project files:\n"
        f"- Project: .projects/active/{dir_name}/{slug}.md\n"
        f"- Plan: .projects/active/{dir_name}/{slug}-plan.md\n"
        f"- Status: .projects/active/{dir_name}/{slug}-status.txt\n"
        f"{CLAUDE_BLOCK_END}\n"
    )

    if claude_md.exists():
        content = claude_md.read_text()
        # Don't add if already present
        if CLAUDE_BLOCK_START in content:
            # Replace existing block
            content = re.sub(
                rf"{re.escape(CLAUDE_BLOCK_START)}.*?{re.escape(CLAUDE_BLOCK_END)}\n?",
                block,
                content,
                flags=re.DOTALL,
            )
            claude_md.write_text(content)
        else:
            with open(claude_md, "a") as f:
                f.write("\n" + block)
    else:
        claude_md.write_text(block)


def _remove_claude_md_block(repo_root: Path) -> None:
    """Remove the active project block from CLAUDE.md."""
    # Check both locations — root CLAUDE.md and .claude/CLAUDE.md
    root_file = repo_root / "CLAUDE.md"
    dot_claude_file = repo_root / ".claude" / "CLAUDE.md"
    if root_file.exists() and CLAUDE_BLOCK_START in root_file.read_text():
        claude_md = root_file
    elif dot_claude_file.exists() and CLAUDE_BLOCK_START in dot_claude_file.read_text():
        claude_md = dot_claude_file
    else:
        return

    content = claude_md.read_text()
    content = re.sub(
        rf"\n?{re.escape(CLAUDE_BLOCK_START)}.*?{re.escape(CLAUDE_BLOCK_END)}\n?",
        "",
        content,
        flags=re.DOTALL,
    )

    # Remove file if it's now empty
    if content.strip():
        claude_md.write_text(content)
    else:
        claude_md.unlink()

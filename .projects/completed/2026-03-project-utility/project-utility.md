# project

A little helper utility for managing coding agent projects.

A project is a set of enhancements or changes to a codebase, that
would typically end up being submitted as a pull request. This
tool establishes some simple conventions for writing and storing
project requirements and implementation plans, and tracking the current
state of a project.

## Directory structure

	.projects/
		active/
		completed/
			2026-01-project-name/
				project-name.md
				project-name-plan.md
				project-name-status.txt
				[other project files, temporary scripts, etc.]

## Workflow

 1. Pick a clean Git working folder or worktree, that doesn't have any current active
    projects going.
 2. Pick a name for the new project, create folder under .projects/active
 3. Create [project-name].md with a writeup of project goals and information the AI agent
    should know
 3. [project-name]-status.txt is created, with a note that this project is in the planning stage.
 4. Have the agent read the project file and create [project-name]-plan.md, containing
    the implementation plan. The level of detail here can still be fairly coarse - the
    agent or sub-agents will be able to create detailed low-level plans on the fly as
    the plan is implemented.
 5. Human and agent improve project file and plan file as needed.
 6. Agent works by itself to implement the plan. As it works, it keeps [project-name]-status.txt
    updated with brief information on the current status, enough that another coder or agent could
    pick up where it left off.
 7. Human reviews work, human and agent make changes as needed. Project, plan, and status files are
    edited as needed to keep them current
 8. When the project is complete, all changes are committed if they haven't been already. The status
    file is updated to note that the project is complete, and include a git reference to the last commit.
    The project directory is then moved from active/ to completed/.


In a single git branch, there should be at most one active project happening at a time.

## Using the `project` command

  `project init "project name"` (creates dir structure, claude files, appends CLAUDE.md with note if necessary. Gives error if an active project already exists)
  `project status` - is there an open project? If so list the name and print the status text
  `project complete` (adds note to status with latest commit, moves to completed). Gives e

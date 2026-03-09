"""CLI entry point for the project utility."""

import argparse
import sys

from . import core


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="project",
        description="Manage coding agent projects.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Project name")

    # status
    subparsers.add_parser("status", help="Show active project status")

    # complete
    subparsers.add_parser("complete", help="Complete the active project")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Require git working directory; use its root for all operations
    repo_root = core.get_repo_root()

    if args.command == "init":
        core.init_project(args.name, repo_root)
    elif args.command == "status":
        core.show_status(repo_root)
    elif args.command == "complete":
        core.complete_project(repo_root)


if __name__ == "__main__":
    main()

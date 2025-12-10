#!/usr/bin/env python3
"""GitHub ecosystem configuration generator.

Generates comprehensive GitHub configuration based on project language.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Literal

# Import from sibling modules
from detect_project import (
    ExistingConfig,
    ProjectInfo,
    detect_existing_config,
    get_project_info,
)
from templates import (
    bug_report_template,
    ci_go,
    ci_python,
    ci_typescript,
    codeowners_template,
    copilot_instructions_template,
    dependabot_template,
    docker_workflow,
    feature_request_template,
    issue_config_template,
    pr_template,
    release_go,
    release_python,
    release_typescript,
)

Component = Literal["workflows", "templates", "dependabot", "codeowners", "copilot"]
ALL_COMPONENTS: list[Component] = ["workflows", "templates", "dependabot", "codeowners", "copilot"]


def generate_github_config(
    project_path: Path,
    info: ProjectInfo,
    existing: ExistingConfig,
    components: list[Component],
    include_release: bool = False,
    include_docker: bool = False,
    codeowners: list[str] | None = None,
    overwrite: bool = False,
) -> list[Path]:
    """Generate GitHub configuration files.

    Args:
        project_path: Path to the project directory.
        info: Detected project information.
        existing: Existing GitHub configuration.
        components: Components to generate.
        include_release: Include release workflow.
        include_docker: Include docker workflow.
        codeowners: CODEOWNERS entries.
        overwrite: Overwrite existing files.

    Returns:
        List of created/modified file paths.
    """
    github_path = project_path / ".github"
    created_files: list[Path] = []

    def write_file(rel_path: str, content: str) -> bool:
        """Write file if it doesn't exist or overwrite is enabled."""
        file_path = github_path / rel_path
        if file_path.exists() and not overwrite:
            print(f"  Skipping {rel_path} (already exists)")
            return False

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        created_files.append(file_path)
        return True

    # Generate workflows
    if "workflows" in components:
        print("Generating workflows...")

        # CI workflow (always)
        if info.language == "python":
            ci_content = ci_python(
                info.name,
                info.package_name,
                info.python_versions,
            )
        elif info.language == "go":
            ci_content = ci_go(
                info.name,
                info.go_module,
                info.go_versions,
            )
        elif info.language == "typescript":
            ci_content = ci_typescript(
                info.name,
                info.node_versions,
                info.package_manager,
                info.test_framework,
            )
        else:
            print(f"  Warning: Unknown language '{info.language}', using Python CI template")
            ci_content = ci_python(info.name, info.name.replace("-", "_"), ["3.12", "3.13", "3.14"])

        if write_file("workflows/ci.yml", ci_content):
            print("  Created workflows/ci.yml")

        # Release workflow (optional)
        if include_release:
            if info.language == "python":
                release_content = release_python(info.name, info.package_name)
            elif info.language == "go":
                release_content = release_go(info.name, info.go_module)
            elif info.language == "typescript":
                release_content = release_typescript(info.name, info.package_manager)
            else:
                release_content = release_python(info.name, info.name.replace("-", "_"))

            if write_file("workflows/release.yml", release_content):
                print("  Created workflows/release.yml")

        # Docker workflow (optional)
        if include_docker:
            docker_content = docker_workflow(info.name, info.language)
            if write_file("workflows/docker.yml", docker_content):
                print("  Created workflows/docker.yml")

    # Generate issue templates
    if "templates" in components:
        print("Generating templates...")

        bug_content = bug_report_template(info.name, info.language)
        if write_file("ISSUE_TEMPLATE/bug_report.md", bug_content):
            print("  Created ISSUE_TEMPLATE/bug_report.md")

        feature_content = feature_request_template(info.name, info.language)
        if write_file("ISSUE_TEMPLATE/feature_request.md", feature_content):
            print("  Created ISSUE_TEMPLATE/feature_request.md")

        config_content = issue_config_template(info.name)
        if write_file("ISSUE_TEMPLATE/config.yml", config_content):
            print("  Created ISSUE_TEMPLATE/config.yml")

        pr_content = pr_template()
        if write_file("PULL_REQUEST_TEMPLATE.md", pr_content):
            print("  Created PULL_REQUEST_TEMPLATE.md")

    # Generate dependabot
    if "dependabot" in components:
        print("Generating dependabot...")
        dependabot_content = dependabot_template(info.language)
        if write_file("dependabot.yml", dependabot_content):
            print("  Created dependabot.yml")

    # Generate CODEOWNERS
    if "codeowners" in components and codeowners:
        print("Generating CODEOWNERS...")
        codeowners_content = codeowners_template(codeowners)
        if write_file("CODEOWNERS", codeowners_content):
            print("  Created CODEOWNERS")

    # Generate Copilot instructions
    if "copilot" in components:
        print("Generating Copilot instructions...")
        copilot_content = copilot_instructions_template(info.name, info.language)
        if write_file("copilot-instructions.md", copilot_content):
            print("  Created copilot-instructions.md")

    return created_files


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate GitHub ecosystem configuration.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project-path .
  %(prog)s --project-path . --language python
  %(prog)s --project-path . --include-release --include-docker
  %(prog)s --project-path . --components workflows,templates
  %(prog)s --project-path . --codeowners "@user1 @team"
        """,
    )

    parser.add_argument(
        "--project-path",
        default=".",
        help="Project directory (default: current directory)",
    )
    parser.add_argument(
        "--language",
        choices=["python", "go", "typescript"],
        help="Force language (auto-detected if not specified)",
    )
    parser.add_argument(
        "--components",
        default="all",
        help="Comma-separated components: workflows,templates,dependabot,codeowners,copilot (default: all)",
    )
    parser.add_argument(
        "--include-release",
        action="store_true",
        help="Include release workflow",
    )
    parser.add_argument(
        "--include-docker",
        action="store_true",
        help="Include docker workflow",
    )
    parser.add_argument(
        "--codeowners",
        help="CODEOWNERS entries (space-separated, e.g., '@user1 @team')",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating files",
    )

    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        return 1

    # Detect project info
    print(f"Analyzing project at: {project_path}")
    info = get_project_info(project_path)
    existing = detect_existing_config(project_path)

    # Override language if specified
    if args.language:
        info = ProjectInfo(
            language=args.language,
            name=info.name,
            description=info.description,
            package_name=info.package_name or info.name.replace("-", "_"),
            python_versions=info.python_versions,
            go_module=info.go_module or info.name,
            go_versions=info.go_versions,
            node_versions=info.node_versions,
            package_manager=info.package_manager,
            test_framework=info.test_framework,
        )

    print(f"  Project name: {info.name}")
    print(f"  Language: {info.language}")

    if info.language == "unknown":
        print()
        print("Warning: Could not detect project language.")
        print("Use --language to specify: python, go, or typescript")
        if not args.language:
            return 1

    # Show existing config
    if existing.exists:
        print()
        print("Existing .github/ configuration detected:")
        if existing.has_workflows:
            print(f"  Workflows: {', '.join(existing.workflows)}")
        if existing.has_issue_templates:
            print("  Issue templates: present")
        if existing.has_pr_template:
            print("  PR template: present")
        if existing.has_dependabot:
            print("  Dependabot: present")
        if existing.has_codeowners:
            print("  CODEOWNERS: present")
        if existing.has_copilot:
            print("  Copilot instructions: present")

        if not args.overwrite:
            print()
            print("Enhancement mode: Will add missing files only.")
            print("Use --overwrite to replace existing files.")

    # Parse components
    if args.components == "all":
        components = list(ALL_COMPONENTS)
    else:
        components = [c.strip() for c in args.components.split(",")]  # type: ignore

    # Parse codeowners
    codeowners = args.codeowners.split() if args.codeowners else None

    # Dry run
    if args.dry_run:
        print()
        print("Dry run - would generate:")
        print(f"  Components: {', '.join(components)}")
        if args.include_release:
            print("  + release.yml workflow")
        if args.include_docker:
            print("  + docker.yml workflow")
        if codeowners:
            print(f"  + CODEOWNERS: {' '.join(codeowners)}")
        return 0

    # Generate
    print()
    created_files = generate_github_config(
        project_path=project_path,
        info=info,
        existing=existing,
        components=components,  # type: ignore
        include_release=args.include_release,
        include_docker=args.include_docker,
        codeowners=codeowners,
        overwrite=args.overwrite,
    )

    # Summary
    print()
    if created_files:
        print(f"Created {len(created_files)} file(s):")
        for f in created_files:
            rel_path = f.relative_to(project_path)
            print(f"  {rel_path}")
    else:
        print("No files created (all already exist).")

    # Post-generation notes
    print()
    print("Next steps:")
    print("  1. Review generated files in .github/")
    print("  2. Update OWNER placeholders with your GitHub username/org")
    if args.include_release:
        print("  3. Add any required secrets (e.g., PYPI_API_TOKEN)")
    print("  4. Commit and push to enable workflows")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

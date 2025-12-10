#!/usr/bin/env python3
"""Project type detection for github-ecosystem skill.

Detects project language and existing GitHub configuration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Language = Literal["python", "go", "typescript", "unknown"]


@dataclass
class ProjectInfo:
    """Detected project information."""

    language: Language
    name: str
    description: str = ""
    # Python-specific
    package_name: str = ""
    python_versions: list[str] = field(default_factory=lambda: ["3.10", "3.11", "3.12", "3.13", "3.14"])
    # Go-specific
    go_module: str = ""
    go_versions: list[str] = field(default_factory=lambda: ["1.21", "1.22", "1.23"])
    # TypeScript-specific
    node_versions: list[str] = field(default_factory=lambda: ["18", "20", "22"])
    package_manager: str = "npm"  # npm, pnpm, yarn
    test_framework: str = "vitest"  # vitest, jest


@dataclass
class ExistingConfig:
    """Existing .github/ configuration."""

    exists: bool = False
    has_workflows: bool = False
    workflows: list[str] = field(default_factory=list)
    has_issue_templates: bool = False
    has_pr_template: bool = False
    has_codeowners: bool = False
    has_dependabot: bool = False
    has_copilot: bool = False


def detect_python(project_path: Path) -> bool:
    """Check for Python project indicators."""
    indicators = [
        project_path / "pyproject.toml",
        project_path / "setup.py",
        project_path / "setup.cfg",
        project_path / "requirements.txt",
    ]
    return any(f.exists() for f in indicators)


def detect_go(project_path: Path) -> bool:
    """Check for Go project indicators."""
    indicators = [
        project_path / "go.mod",
        project_path / "go.sum",
    ]
    return any(f.exists() for f in indicators)


def detect_typescript(project_path: Path) -> bool:
    """Check for TypeScript project indicators."""
    package_json = project_path / "package.json"
    tsconfig = project_path / "tsconfig.json"

    if not package_json.exists():
        return False

    # Check for TypeScript in dependencies
    try:
        with open(package_json) as f:
            pkg = json.load(f)
        deps = pkg.get("devDependencies", {})
        deps.update(pkg.get("dependencies", {}))
        return "typescript" in deps or tsconfig.exists()
    except (json.JSONDecodeError, OSError):
        return tsconfig.exists()


def detect_language(project_path: Path) -> Language:
    """Detect primary language of the project."""
    path = Path(project_path).resolve()

    # Order matters - check most specific first
    if detect_go(path):
        return "go"
    if detect_typescript(path):
        return "typescript"
    if detect_python(path):
        return "python"

    return "unknown"


def get_python_info(project_path: Path) -> dict:
    """Extract Python project info from pyproject.toml."""
    pyproject = project_path / "pyproject.toml"
    info = {
        "name": project_path.name,
        "package_name": project_path.name.replace("-", "_"),
        "description": "",
        "python_versions": ["3.10", "3.11", "3.12", "3.13", "3.14"],
    }

    if not pyproject.exists():
        return info

    try:
        content = pyproject.read_text()
        # Simple parsing without toml library
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("name = "):
                info["name"] = line.split("=", 1)[1].strip().strip('"\'')
                info["package_name"] = info["name"].replace("-", "_")
            elif line.startswith("description = "):
                info["description"] = line.split("=", 1)[1].strip().strip('"\'')
            elif "requires-python" in line:
                # Extract minimum version
                version = line.split(">=")[-1].strip().strip('"\'').split(",")[0]
                if version:
                    # Generate version range from minimum
                    major, minor = version.split(".")[:2]
                    min_minor = int(minor)
                    info["python_versions"] = [
                        f"3.{v}" for v in range(min_minor, 15) if v >= 10
                    ]
    except (OSError, ValueError):
        pass

    return info


def get_go_info(project_path: Path) -> dict:
    """Extract Go project info from go.mod."""
    gomod = project_path / "go.mod"
    info = {
        "name": project_path.name,
        "go_module": "",
        "go_versions": ["1.21", "1.22", "1.23"],
    }

    if not gomod.exists():
        return info

    try:
        content = gomod.read_text()
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("module "):
                info["go_module"] = line.split(" ", 1)[1].strip()
                # Use last part of module path as name
                info["name"] = info["go_module"].split("/")[-1]
            elif line.startswith("go "):
                # Extract Go version
                version = line.split(" ", 1)[1].strip()
                if version:
                    # Generate version range
                    major, minor = version.split(".")[:2]
                    min_minor = int(minor)
                    info["go_versions"] = [
                        f"1.{v}" for v in range(min_minor, 24) if v >= 21
                    ]
    except (OSError, ValueError):
        pass

    return info


def get_typescript_info(project_path: Path) -> dict:
    """Extract TypeScript project info from package.json."""
    package_json = project_path / "package.json"
    info = {
        "name": project_path.name,
        "description": "",
        "node_versions": ["18", "20", "22"],
        "package_manager": "npm",
        "test_framework": "vitest",
    }

    if not package_json.exists():
        return info

    try:
        with open(package_json) as f:
            pkg = json.load(f)

        info["name"] = pkg.get("name", project_path.name)
        info["description"] = pkg.get("description", "")

        # Detect package manager
        if (project_path / "pnpm-lock.yaml").exists():
            info["package_manager"] = "pnpm"
        elif (project_path / "yarn.lock").exists():
            info["package_manager"] = "yarn"

        # Detect test framework
        deps = pkg.get("devDependencies", {})
        if "vitest" in deps:
            info["test_framework"] = "vitest"
        elif "jest" in deps:
            info["test_framework"] = "jest"

        # Detect Node version from engines
        engines = pkg.get("engines", {})
        if "node" in engines:
            # Parse >=18 or ^18 style
            node_spec = engines["node"]
            for v in ["18", "20", "22"]:
                if v in node_spec:
                    min_version = int(v)
                    info["node_versions"] = [
                        str(nv) for nv in [18, 20, 22] if nv >= min_version
                    ]
                    break

    except (json.JSONDecodeError, OSError, ValueError):
        pass

    return info


def get_project_info(project_path: Path) -> ProjectInfo:
    """Get comprehensive project information."""
    path = Path(project_path).resolve()
    language = detect_language(path)

    if language == "python":
        py_info = get_python_info(path)
        return ProjectInfo(
            language=language,
            name=py_info["name"],
            description=py_info["description"],
            package_name=py_info["package_name"],
            python_versions=py_info["python_versions"],
        )
    elif language == "go":
        go_info = get_go_info(path)
        return ProjectInfo(
            language=language,
            name=go_info["name"],
            go_module=go_info["go_module"],
            go_versions=go_info["go_versions"],
        )
    elif language == "typescript":
        ts_info = get_typescript_info(path)
        return ProjectInfo(
            language=language,
            name=ts_info["name"],
            description=ts_info["description"],
            node_versions=ts_info["node_versions"],
            package_manager=ts_info["package_manager"],
            test_framework=ts_info["test_framework"],
        )
    else:
        return ProjectInfo(
            language="unknown",
            name=path.name,
        )


def detect_existing_config(project_path: Path) -> ExistingConfig:
    """Detect existing .github/ configuration."""
    path = Path(project_path).resolve()
    github_path = path / ".github"

    config = ExistingConfig(exists=github_path.exists())

    if not config.exists:
        return config

    # Check workflows
    workflows_path = github_path / "workflows"
    if workflows_path.exists():
        config.has_workflows = True
        config.workflows = [f.stem for f in workflows_path.glob("*.yml")]
        config.workflows.extend(f.stem for f in workflows_path.glob("*.yaml"))

    # Check templates
    config.has_issue_templates = (github_path / "ISSUE_TEMPLATE").exists()
    config.has_pr_template = (github_path / "PULL_REQUEST_TEMPLATE.md").exists()

    # Check other files
    config.has_codeowners = (github_path / "CODEOWNERS").exists()
    config.has_dependabot = (github_path / "dependabot.yml").exists()
    config.has_copilot = (github_path / "copilot-instructions.md").exists()

    return config


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project = Path(sys.argv[1])
    else:
        project = Path.cwd()

    info = get_project_info(project)
    config = detect_existing_config(project)

    print(f"Project: {info.name}")
    print(f"Language: {info.language}")
    print()
    print("Existing .github/ config:")
    print(f"  Exists: {config.exists}")
    if config.exists:
        print(f"  Workflows: {config.workflows}")
        print(f"  Issue templates: {config.has_issue_templates}")
        print(f"  PR template: {config.has_pr_template}")
        print(f"  CODEOWNERS: {config.has_codeowners}")
        print(f"  Dependabot: {config.has_dependabot}")
        print(f"  Copilot: {config.has_copilot}")

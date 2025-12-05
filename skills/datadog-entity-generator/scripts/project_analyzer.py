#!/usr/bin/env python3
"""
Analyze a project directory to extract metadata for Datadog entity generation.

Detects:
- Project name and description from manifest files
- Programming languages
- Dependencies (services, datastores, queues)
- Repository information
- Existing Datadog entity definitions
- Infrastructure configuration
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DetectedValue:
    """A detected metadata value with confidence score."""

    value: Any
    confidence: float  # 0.0 to 1.0
    source: str  # File or method that detected this


@dataclass
class ProjectAnalysis:
    """Results of project analysis."""

    name: DetectedValue | None = None
    display_name: DetectedValue | None = None
    description: DetectedValue | None = None
    languages: list[DetectedValue] = field(default_factory=list)
    repository_url: DetectedValue | None = None
    service_type: DetectedValue | None = None
    dependencies: list[DetectedValue] = field(default_factory=list)
    datastores: list[DetectedValue] = field(default_factory=list)
    queues: list[DetectedValue] = field(default_factory=list)
    existing_entity: dict | None = None
    detected_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""

        def val_to_dict(v: DetectedValue | None) -> dict | None:
            if v is None:
                return None
            return {"value": v.value, "confidence": v.confidence, "source": v.source}

        return {
            "name": val_to_dict(self.name),
            "display_name": val_to_dict(self.display_name),
            "description": val_to_dict(self.description),
            "languages": [val_to_dict(v) for v in self.languages],
            "repository_url": val_to_dict(self.repository_url),
            "service_type": val_to_dict(self.service_type),
            "dependencies": [val_to_dict(v) for v in self.dependencies],
            "datastores": [val_to_dict(v) for v in self.datastores],
            "queues": [val_to_dict(v) for v in self.queues],
            "existing_entity": self.existing_entity,
            "detected_files": self.detected_files,
            "warnings": self.warnings,
        }


class ProjectAnalyzer:
    """Analyzes a project directory for Datadog entity metadata."""

    # Language detection by file extension
    LANGUAGE_EXTENSIONS = {
        ".py": "python",
        ".go": "go",
        ".java": "java",
        ".kt": "kotlin",
        ".js": "js",
        ".ts": "js",
        ".jsx": "js",
        ".tsx": "js",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "dotnet",
        ".rs": "rust",
        ".cpp": "c++",
        ".c": "c++",
        ".h": "c++",
        ".swift": "swift",
        ".scala": "scala",
    }

    # Datastore detection patterns
    DATASTORE_PATTERNS = {
        "postgres": [
            r"postgres",
            r"psycopg",
            r"pg_",
            r"postgresql",
            r"DATABASE_URL.*postgres",
        ],
        "mysql": [r"mysql", r"pymysql", r"mysqlclient"],
        "redis": [r"redis", r"REDIS_URL", r"redis://"],
        "mongodb": [r"mongo", r"pymongo", r"MONGO_URI"],
        "elasticsearch": [r"elasticsearch", r"elastic", r"ES_HOST"],
        "cassandra": [r"cassandra", r"cql"],
        "dynamodb": [r"dynamodb", r"boto3.*dynamodb"],
    }

    # Queue detection patterns
    QUEUE_PATTERNS = {
        "kafka": [r"kafka", r"confluent", r"KAFKA_BOOTSTRAP"],
        "rabbitmq": [r"rabbitmq", r"amqp", r"pika", r"RABBITMQ_"],
        "sqs": [r"boto3.*sqs", r"SQS_QUEUE", r"aws.*sqs"],
        "kinesis": [r"kinesis", r"boto3.*kinesis"],
        "pubsub": [r"google.*pubsub", r"PUBSUB_"],
    }

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.result = ProjectAnalysis()

    def analyze(self) -> ProjectAnalysis:
        """Run full analysis on the project."""
        self._detect_manifest_files()
        self._detect_languages()
        self._detect_existing_entity()
        self._detect_infrastructure()
        self._detect_dependencies()
        self._detect_repository()
        self._detect_readme()
        self._detect_codeowners()
        return self.result

    def _detect_manifest_files(self) -> None:
        """Detect and parse manifest files for project metadata."""
        # Python: pyproject.toml
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            self.result.detected_files.append("pyproject.toml")
            self._parse_pyproject(pyproject)

        # Python: setup.py
        setup_py = self.project_path / "setup.py"
        if setup_py.exists():
            self.result.detected_files.append("setup.py")
            self._parse_setup_py(setup_py)

        # Node.js: package.json
        package_json = self.project_path / "package.json"
        if package_json.exists():
            self.result.detected_files.append("package.json")
            self._parse_package_json(package_json)

        # Java: pom.xml
        pom_xml = self.project_path / "pom.xml"
        if pom_xml.exists():
            self.result.detected_files.append("pom.xml")
            self._parse_pom_xml(pom_xml)

        # Go: go.mod
        go_mod = self.project_path / "go.mod"
        if go_mod.exists():
            self.result.detected_files.append("go.mod")
            self._parse_go_mod(go_mod)

    def _parse_pyproject(self, path: Path) -> None:
        """Parse pyproject.toml for metadata."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                self.result.warnings.append(
                    "tomllib/tomli not available, skipping pyproject.toml parsing"
                )
                return

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)

            project = data.get("project", {})
            poetry = data.get("tool", {}).get("poetry", {})

            # Name from project or poetry section
            name = project.get("name") or poetry.get("name")
            if name and not self.result.name:
                self.result.name = DetectedValue(
                    value=name, confidence=0.95, source="pyproject.toml"
                )

            # Description
            desc = project.get("description") or poetry.get("description")
            if desc and not self.result.description:
                self.result.description = DetectedValue(
                    value=desc, confidence=0.9, source="pyproject.toml"
                )

            # Add Python as language
            self.result.languages.append(
                DetectedValue(value="python", confidence=0.98, source="pyproject.toml")
            )

        except Exception as e:
            self.result.warnings.append(f"Error parsing pyproject.toml: {e}")

    def _parse_setup_py(self, path: Path) -> None:
        """Parse setup.py for metadata (basic extraction)."""
        try:
            content = path.read_text()

            # Extract name
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match and not self.result.name:
                self.result.name = DetectedValue(
                    value=name_match.group(1), confidence=0.9, source="setup.py"
                )

            # Extract description
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if desc_match and not self.result.description:
                self.result.description = DetectedValue(
                    value=desc_match.group(1), confidence=0.85, source="setup.py"
                )

        except Exception as e:
            self.result.warnings.append(f"Error parsing setup.py: {e}")

    def _parse_package_json(self, path: Path) -> None:
        """Parse package.json for metadata."""
        try:
            data = json.loads(path.read_text())

            if data.get("name") and not self.result.name:
                self.result.name = DetectedValue(
                    value=data["name"], confidence=0.95, source="package.json"
                )

            if data.get("description") and not self.result.description:
                self.result.description = DetectedValue(
                    value=data["description"], confidence=0.9, source="package.json"
                )

            # Repository URL
            repo = data.get("repository")
            if repo:
                url = repo.get("url") if isinstance(repo, dict) else repo
                if url and not self.result.repository_url:
                    # Clean git+ prefix and .git suffix
                    url = re.sub(r"^git\+", "", url)
                    url = re.sub(r"\.git$", "", url)
                    self.result.repository_url = DetectedValue(
                        value=url, confidence=0.95, source="package.json"
                    )

            # Language
            self.result.languages.append(
                DetectedValue(value="js", confidence=0.98, source="package.json")
            )

        except Exception as e:
            self.result.warnings.append(f"Error parsing package.json: {e}")

    def _parse_pom_xml(self, path: Path) -> None:
        """Parse pom.xml for metadata (basic extraction)."""
        try:
            content = path.read_text()

            # Extract artifactId as name
            artifact_match = re.search(
                r"<artifactId>([^<]+)</artifactId>", content, re.IGNORECASE
            )
            if artifact_match and not self.result.name:
                self.result.name = DetectedValue(
                    value=artifact_match.group(1), confidence=0.9, source="pom.xml"
                )

            # Extract description
            desc_match = re.search(
                r"<description>([^<]+)</description>", content, re.IGNORECASE
            )
            if desc_match and not self.result.description:
                self.result.description = DetectedValue(
                    value=desc_match.group(1), confidence=0.85, source="pom.xml"
                )

            self.result.languages.append(
                DetectedValue(value="java", confidence=0.98, source="pom.xml")
            )

        except Exception as e:
            self.result.warnings.append(f"Error parsing pom.xml: {e}")

    def _parse_go_mod(self, path: Path) -> None:
        """Parse go.mod for metadata."""
        try:
            content = path.read_text()

            # Extract module name
            module_match = re.search(r"^module\s+(.+)$", content, re.MULTILINE)
            if module_match and not self.result.name:
                module_path = module_match.group(1).strip()
                # Use last path component as name
                name = module_path.split("/")[-1]
                self.result.name = DetectedValue(
                    value=name, confidence=0.85, source="go.mod"
                )
                # Full module path might be repo URL
                if module_path.startswith("github.com/"):
                    self.result.repository_url = DetectedValue(
                        value=f"https://{module_path}",
                        confidence=0.9,
                        source="go.mod",
                    )

            self.result.languages.append(
                DetectedValue(value="go", confidence=0.98, source="go.mod")
            )

        except Exception as e:
            self.result.warnings.append(f"Error parsing go.mod: {e}")

    def _detect_languages(self) -> None:
        """Detect programming languages from file extensions."""
        lang_counts: dict[str, int] = {}

        for ext, lang in self.LANGUAGE_EXTENSIONS.items():
            count = len(list(self.project_path.rglob(f"*{ext}")))
            if count > 0:
                lang_counts[lang] = lang_counts.get(lang, 0) + count

        # Add languages not already detected from manifests
        existing_langs = {v.value for v in self.result.languages}
        for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
            if lang not in existing_langs and count >= 3:
                confidence = min(0.95, 0.5 + (count / 100))
                self.result.languages.append(
                    DetectedValue(
                        value=lang, confidence=confidence, source="file_extensions"
                    )
                )

    def _detect_existing_entity(self) -> None:
        """Check for existing Datadog entity definition."""
        entity_files = [
            ".datadog/entity.datadog.yaml",
            ".datadog/entity.datadog.yml",
            ".datadog/service.datadog.yaml",
            ".datadog/service.datadog.yml",
            "entity.datadog.yaml",
            "entity.datadog.yml",
            "service.datadog.yaml",
            "service.datadog.yml",
        ]

        for entity_file in entity_files:
            path = self.project_path / entity_file
            if path.exists():
                self.result.detected_files.append(entity_file)
                try:
                    import yaml

                    with open(path) as f:
                        # Handle multi-document YAML
                        docs = list(yaml.safe_load_all(f))
                        self.result.existing_entity = (
                            docs if len(docs) > 1 else docs[0] if docs else None
                        )
                except ImportError:
                    self.result.warnings.append(
                        "PyYAML not available, cannot parse existing entity"
                    )
                except Exception as e:
                    self.result.warnings.append(f"Error parsing {entity_file}: {e}")
                break

    def _detect_infrastructure(self) -> None:
        """Detect infrastructure configuration files."""
        # Dockerfile
        dockerfile = self.project_path / "Dockerfile"
        if dockerfile.exists():
            self.result.detected_files.append("Dockerfile")
            self.result.service_type = DetectedValue(
                value="web", confidence=0.7, source="Dockerfile"
            )

        # Docker Compose
        for compose_file in ["docker-compose.yml", "docker-compose.yaml"]:
            compose_path = self.project_path / compose_file
            if compose_path.exists():
                self.result.detected_files.append(compose_file)
                self._analyze_docker_compose(compose_path)

        # Kubernetes
        k8s_dirs = ["kubernetes", "k8s", "deploy", "manifests"]
        for k8s_dir in k8s_dirs:
            k8s_path = self.project_path / k8s_dir
            if k8s_path.is_dir():
                self.result.detected_files.append(f"{k8s_dir}/")

        # Helm
        helm_chart = self.project_path / "Chart.yaml"
        if helm_chart.exists():
            self.result.detected_files.append("Chart.yaml")

        # Terraform
        tf_files = list(self.project_path.glob("*.tf"))
        if tf_files:
            self.result.detected_files.append("*.tf")

    def _analyze_docker_compose(self, path: Path) -> None:
        """Analyze docker-compose.yml for service dependencies."""
        try:
            import yaml

            with open(path) as f:
                data = yaml.safe_load(f)

            services = data.get("services", {})
            for service_name, service_config in services.items():
                image = service_config.get("image", "")

                # Detect datastores
                for ds_type, patterns in self.DATASTORE_PATTERNS.items():
                    if any(re.search(p, image, re.I) for p in patterns):
                        self.result.datastores.append(
                            DetectedValue(
                                value={"name": service_name, "type": ds_type},
                                confidence=0.85,
                                source="docker-compose.yml",
                            )
                        )
                        break

                # Detect queues
                for q_type, patterns in self.QUEUE_PATTERNS.items():
                    if any(re.search(p, image, re.I) for p in patterns):
                        self.result.queues.append(
                            DetectedValue(
                                value={"name": service_name, "type": q_type},
                                confidence=0.85,
                                source="docker-compose.yml",
                            )
                        )
                        break

        except ImportError:
            pass
        except Exception as e:
            self.result.warnings.append(f"Error analyzing docker-compose: {e}")

    def _detect_dependencies(self) -> None:
        """Detect service dependencies from code and config."""
        # Scan common config files for patterns
        config_files = [
            "*.env",
            ".env.*",
            "config/*.yaml",
            "config/*.yml",
            "config/*.json",
            "settings.py",
            "config.py",
        ]

        for pattern in config_files:
            for config_file in self.project_path.glob(pattern):
                self._scan_file_for_dependencies(config_file)

    def _scan_file_for_dependencies(self, path: Path) -> None:
        """Scan a file for datastore and queue connection patterns."""
        try:
            content = path.read_text()

            # Check for datastores
            for ds_type, patterns in self.DATASTORE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.I):
                        # Avoid duplicates
                        existing = {d.value.get("type") for d in self.result.datastores}
                        if ds_type not in existing:
                            self.result.datastores.append(
                                DetectedValue(
                                    value={"name": f"{ds_type}-db", "type": ds_type},
                                    confidence=0.7,
                                    source=path.name,
                                )
                            )
                        break

            # Check for queues
            for q_type, patterns in self.QUEUE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.I):
                        existing = {q.value.get("type") for q in self.result.queues}
                        if q_type not in existing:
                            self.result.queues.append(
                                DetectedValue(
                                    value={"name": f"{q_type}-queue", "type": q_type},
                                    confidence=0.7,
                                    source=path.name,
                                )
                            )
                        break

        except Exception:
            pass

    def _detect_repository(self) -> None:
        """Detect repository URL from git config."""
        git_config = self.project_path / ".git" / "config"
        if git_config.exists() and not self.result.repository_url:
            try:
                content = git_config.read_text()
                url_match = re.search(r'url\s*=\s*(.+)', content)
                if url_match:
                    url = url_match.group(1).strip()
                    # Convert SSH to HTTPS
                    url = re.sub(r"^git@github\.com:", "https://github.com/", url)
                    url = re.sub(r"^git@gitlab\.com:", "https://gitlab.com/", url)
                    url = re.sub(r"\.git$", "", url)
                    self.result.repository_url = DetectedValue(
                        value=url, confidence=0.95, source=".git/config"
                    )
            except Exception:
                pass

    def _detect_readme(self) -> None:
        """Extract description from README if not already set."""
        if self.result.description:
            return

        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        for readme_name in readme_files:
            readme_path = self.project_path / readme_name
            if readme_path.exists():
                self.result.detected_files.append(readme_name)
                try:
                    content = readme_path.read_text()
                    # Get first paragraph after title
                    lines = content.split("\n")
                    description_lines = []
                    in_description = False

                    for line in lines:
                        # Skip title lines
                        if line.startswith("#") or line.startswith("="):
                            in_description = True
                            continue
                        if in_description:
                            if line.strip() == "":
                                if description_lines:
                                    break
                                continue
                            description_lines.append(line.strip())
                            if len(" ".join(description_lines)) > 200:
                                break

                    if description_lines:
                        desc = " ".join(description_lines)[:300]
                        self.result.description = DetectedValue(
                            value=desc, confidence=0.6, source=readme_name
                        )
                    break
                except Exception:
                    pass

    def _detect_codeowners(self) -> None:
        """Detect team ownership from CODEOWNERS file."""
        codeowners_paths = [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"]
        for codeowners_name in codeowners_paths:
            codeowners_path = self.project_path / codeowners_name
            if codeowners_path.exists():
                self.result.detected_files.append(codeowners_name)
                try:
                    content = codeowners_path.read_text()
                    # Find team mentions
                    teams = re.findall(r"@[\w-]+/[\w-]+", content)
                    if teams:
                        # Use most common team
                        team = max(set(teams), key=teams.count)
                        team = team.lstrip("@").split("/")[-1]
                        self.result.dependencies.append(
                            DetectedValue(
                                value={"type": "owner_hint", "team": team},
                                confidence=0.75,
                                source=codeowners_name,
                            )
                        )
                except Exception:
                    pass


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: project_analyzer.py <project_path>", file=sys.stderr)
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    if not project_path.is_dir():
        print(f"Error: {project_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    analyzer = ProjectAnalyzer(project_path)
    result = analyzer.analyze()

    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()

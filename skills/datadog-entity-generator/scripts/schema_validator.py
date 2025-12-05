#!/usr/bin/env python3
"""
Validate Datadog entity YAML files against the official JSON schema.

Supports all v3 entity kinds and multi-document YAML files.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import yaml

# Schema URLs
SCHEMA_BASE = "https://raw.githubusercontent.com/DataDog/schema/main/service-catalog"
SCHEMA_URLS = {
    "service": f"{SCHEMA_BASE}/v3/service.schema.json",
    "datastore": f"{SCHEMA_BASE}/v3/datastore.schema.json",
    "queue": f"{SCHEMA_BASE}/v3/queue.schema.json",
    "api": f"{SCHEMA_BASE}/v3/api.schema.json",
    "system": f"{SCHEMA_BASE}/v3/system.schema.json",
    "entity": f"{SCHEMA_BASE}/v3/entity.schema.json",
    "metadata": f"{SCHEMA_BASE}/v3/metadata.schema.json",
}


@dataclass
class ValidationError:
    """A validation error."""

    path: str
    message: str
    value: Any = None


@dataclass
class ValidationResult:
    """Result of validating an entity."""

    entity_name: str
    entity_kind: str
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SchemaValidator:
    """Validates entities against JSON schema and custom rules."""

    VALID_KINDS = {"service", "datastore", "queue", "api", "system"}
    VALID_LIFECYCLES = {"production", "experimental", "deprecated"}
    VALID_TIERS = {"critical", "high", "medium", "low", "1", "2", "3", "4"}
    VALID_CONTACT_TYPES = {"email", "slack", "microsoft-teams"}
    VALID_LINK_TYPES = {"runbook", "doc", "repo", "dashboard", "other"}

    def __init__(self):
        self._schemas: dict[str, dict] = {}

    def _fetch_schema(self, kind: str) -> dict | None:
        """Fetch and cache JSON schema for a kind."""
        if kind in self._schemas:
            return self._schemas[kind]

        url = SCHEMA_URLS.get(kind)
        if not url:
            return None

        try:
            with urlopen(url, timeout=10) as response:
                schema = json.loads(response.read().decode())
                self._schemas[kind] = schema
                return schema
        except Exception:
            return None

    def validate(self, entity: dict) -> ValidationResult:
        """Validate a single entity."""
        errors: list[ValidationError] = []
        warnings: list[str] = []

        # Extract basic info
        api_version = entity.get("apiVersion")
        kind = entity.get("kind", "unknown")
        metadata = entity.get("metadata", {})
        name = metadata.get("name", "unknown")

        result = ValidationResult(
            entity_name=name, entity_kind=kind, valid=True, errors=[], warnings=[]
        )

        # Required fields
        if not api_version:
            errors.append(
                ValidationError(path="apiVersion", message="apiVersion is required")
            )
        elif api_version != "v3":
            errors.append(
                ValidationError(
                    path="apiVersion",
                    message=f"Expected 'v3', got '{api_version}'",
                    value=api_version,
                )
            )

        if not kind:
            errors.append(ValidationError(path="kind", message="kind is required"))
        elif kind not in self.VALID_KINDS:
            errors.append(
                ValidationError(
                    path="kind",
                    message=f"Invalid kind '{kind}'. "
                    f"Must be one of: {', '.join(self.VALID_KINDS)}",
                    value=kind,
                )
            )

        if not metadata:
            errors.append(
                ValidationError(path="metadata", message="metadata is required")
            )
        else:
            errors.extend(self._validate_metadata(metadata))

        # Validate spec
        spec = entity.get("spec", {})
        if spec:
            errors.extend(self._validate_spec(spec, kind))

        # Validate integrations
        integrations = entity.get("integrations", {})
        if integrations:
            errors.extend(self._validate_integrations(integrations))

        # Validate datadog section
        datadog = entity.get("datadog", {})
        if datadog:
            errors.extend(self._validate_datadog(datadog))

        # Try JSON schema validation if available
        try:
            import jsonschema

            schema = self._fetch_schema(kind)
            if schema:
                try:
                    # Create a resolver for $ref
                    validator = jsonschema.Draft7Validator(schema)
                    schema_errors = list(validator.iter_errors(entity))
                    for error in schema_errors:
                        path = ".".join(str(p) for p in error.absolute_path)
                        if not any(e.path == path for e in errors):
                            errors.append(
                                ValidationError(
                                    path=path or "root",
                                    message=error.message,
                                    value=error.instance,
                                )
                            )
                except Exception as e:
                    warnings.append(f"JSON schema validation partial: {e}")
        except ImportError:
            warnings.append(
                "jsonschema not installed, skipping JSON schema validation"
            )

        result.errors = errors
        result.warnings = warnings
        result.valid = len(errors) == 0

        return result

    def _validate_metadata(self, metadata: dict) -> list[ValidationError]:
        """Validate the metadata section."""
        errors: list[ValidationError] = []

        # Name is required
        name = metadata.get("name")
        if not name:
            errors.append(
                ValidationError(path="metadata.name", message="name is required")
            )
        elif not isinstance(name, str):
            errors.append(
                ValidationError(
                    path="metadata.name", message="name must be a string", value=name
                )
            )
        else:
            # Name format validation
            import re

            if not re.match(r"^[a-z][a-z0-9\-]*$", name):
                errors.append(
                    ValidationError(
                        path="metadata.name",
                        message="name must be lowercase alphanumeric with hyphens, starting with a letter",
                        value=name,
                    )
                )

        # Validate tags format
        tags = metadata.get("tags", [])
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                errors.append(
                    ValidationError(
                        path=f"metadata.tags[{i}]",
                        message="tag must be a string",
                        value=tag,
                    )
                )
            elif ":" not in tag:
                errors.append(
                    ValidationError(
                        path=f"metadata.tags[{i}]",
                        message="tag must be in key:value format",
                        value=tag,
                    )
                )

        # Validate contacts
        contacts = metadata.get("contacts", [])
        for i, contact in enumerate(contacts):
            if not isinstance(contact, dict):
                errors.append(
                    ValidationError(
                        path=f"metadata.contacts[{i}]",
                        message="contact must be an object",
                        value=contact,
                    )
                )
                continue

            if "type" not in contact:
                errors.append(
                    ValidationError(
                        path=f"metadata.contacts[{i}].type",
                        message="contact type is required",
                    )
                )
            elif contact["type"] not in self.VALID_CONTACT_TYPES:
                errors.append(
                    ValidationError(
                        path=f"metadata.contacts[{i}].type",
                        message=f"Invalid contact type. Must be one of: {', '.join(self.VALID_CONTACT_TYPES)}",
                        value=contact["type"],
                    )
                )

            if "contact" not in contact:
                errors.append(
                    ValidationError(
                        path=f"metadata.contacts[{i}].contact",
                        message="contact value is required",
                    )
                )
            elif contact.get("type") == "email":
                # Validate email format
                import re

                email = contact["contact"]
                if not re.match(
                    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email
                ):
                    errors.append(
                        ValidationError(
                            path=f"metadata.contacts[{i}].contact",
                            message="Invalid email format",
                            value=email,
                        )
                    )

        # Validate links
        links = metadata.get("links", [])
        for i, link in enumerate(links):
            if not isinstance(link, dict):
                errors.append(
                    ValidationError(
                        path=f"metadata.links[{i}]",
                        message="link must be an object",
                        value=link,
                    )
                )
                continue

            if "name" not in link:
                errors.append(
                    ValidationError(
                        path=f"metadata.links[{i}].name", message="link name is required"
                    )
                )

            if "type" not in link:
                errors.append(
                    ValidationError(
                        path=f"metadata.links[{i}].type", message="link type is required"
                    )
                )
            elif link["type"] not in self.VALID_LINK_TYPES:
                errors.append(
                    ValidationError(
                        path=f"metadata.links[{i}].type",
                        message=f"Invalid link type. Must be one of: {', '.join(self.VALID_LINK_TYPES)}",
                        value=link["type"],
                    )
                )

            if "url" not in link:
                errors.append(
                    ValidationError(
                        path=f"metadata.links[{i}].url", message="link url is required"
                    )
                )
            else:
                url = link["url"]
                if not url.startswith(("http://", "https://")):
                    errors.append(
                        ValidationError(
                            path=f"metadata.links[{i}].url",
                            message="URL must start with http:// or https://",
                            value=url,
                        )
                    )

        return errors

    def _validate_spec(self, spec: dict, kind: str) -> list[ValidationError]:
        """Validate the spec section."""
        errors: list[ValidationError] = []

        # Lifecycle
        lifecycle = spec.get("lifecycle")
        if lifecycle and lifecycle not in self.VALID_LIFECYCLES:
            errors.append(
                ValidationError(
                    path="spec.lifecycle",
                    message=f"Invalid lifecycle. Must be one of: {', '.join(self.VALID_LIFECYCLES)}",
                    value=lifecycle,
                )
            )

        # Tier
        tier = spec.get("tier")
        if tier and str(tier).lower() not in self.VALID_TIERS:
            errors.append(
                ValidationError(
                    path="spec.tier",
                    message=f"Invalid tier. Must be one of: {', '.join(self.VALID_TIERS)}",
                    value=tier,
                )
            )

        # Validate dependency references
        for dep_field in ["dependsOn", "componentOf", "components", "implementedBy"]:
            deps = spec.get(dep_field, [])
            for i, dep in enumerate(deps):
                if not isinstance(dep, str):
                    errors.append(
                        ValidationError(
                            path=f"spec.{dep_field}[{i}]",
                            message="Dependency must be a string",
                            value=dep,
                        )
                    )
                elif ":" not in dep:
                    errors.append(
                        ValidationError(
                            path=f"spec.{dep_field}[{i}]",
                            message="Dependency must be in kind:name format (e.g., service:my-service)",
                            value=dep,
                        )
                    )

        return errors

    def _validate_integrations(self, integrations: dict) -> list[ValidationError]:
        """Validate the integrations section."""
        errors: list[ValidationError] = []
        import re

        # PagerDuty URL pattern
        pagerduty = integrations.get("pagerduty", {})
        if pagerduty:
            url = pagerduty.get("serviceURL")
            if url:
                pattern = r"^https?://[a-zA-Z\d_\-.]+\.pagerduty\.com/service-directory/(P[a-zA-Z\d_\-]+)/?$"
                if not re.match(pattern, url):
                    errors.append(
                        ValidationError(
                            path="integrations.pagerduty.serviceURL",
                            message="Invalid PagerDuty service URL format",
                            value=url,
                        )
                    )

        # OpsGenie
        opsgenie = integrations.get("opsgenie", {})
        if opsgenie:
            region = opsgenie.get("region")
            if region and region not in {"US", "EU"}:
                errors.append(
                    ValidationError(
                        path="integrations.opsgenie.region",
                        message="OpsGenie region must be 'US' or 'EU'",
                        value=region,
                    )
                )

        return errors

    def _validate_datadog(self, datadog: dict) -> list[ValidationError]:
        """Validate the datadog section."""
        errors: list[ValidationError] = []

        # Code locations
        code_locations = datadog.get("codeLocations", [])
        for i, loc in enumerate(code_locations):
            if not isinstance(loc, dict):
                errors.append(
                    ValidationError(
                        path=f"datadog.codeLocations[{i}]",
                        message="Code location must be an object",
                        value=loc,
                    )
                )
                continue

            if "repositoryURL" not in loc:
                errors.append(
                    ValidationError(
                        path=f"datadog.codeLocations[{i}].repositoryURL",
                        message="repositoryURL is required",
                    )
                )

        # Log queries
        logs = datadog.get("logs", [])
        for i, log in enumerate(logs):
            if not isinstance(log, dict):
                errors.append(
                    ValidationError(
                        path=f"datadog.logs[{i}]",
                        message="Log query must be an object",
                        value=log,
                    )
                )
                continue

            if "name" not in log:
                errors.append(
                    ValidationError(
                        path=f"datadog.logs[{i}].name", message="Log query name is required"
                    )
                )
            if "query" not in log:
                errors.append(
                    ValidationError(
                        path=f"datadog.logs[{i}].query",
                        message="Log query string is required",
                    )
                )

        # Event queries
        events = datadog.get("events", [])
        for i, event in enumerate(events):
            if not isinstance(event, dict):
                errors.append(
                    ValidationError(
                        path=f"datadog.events[{i}]",
                        message="Event query must be an object",
                        value=event,
                    )
                )
                continue

            if "name" not in event:
                errors.append(
                    ValidationError(
                        path=f"datadog.events[{i}].name",
                        message="Event query name is required",
                    )
                )
            if "query" not in event:
                errors.append(
                    ValidationError(
                        path=f"datadog.events[{i}].query",
                        message="Event query string is required",
                    )
                )

        return errors


def validate_file(path: Path) -> list[ValidationResult]:
    """Validate all entities in a YAML file."""
    with open(path) as f:
        docs = list(yaml.safe_load_all(f))

    validator = SchemaValidator()
    results = []

    for doc in docs:
        if doc:
            results.append(validator.validate(doc))

    return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Datadog entity YAML files")
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="YAML files to validate",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        help="Exit with error code on any validation failure",
    )

    args = parser.parse_args()

    all_results = []
    any_invalid = False

    for file_path in args.files:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            any_invalid = True
            continue

        results = validate_file(file_path)
        all_results.extend(results)

        for result in results:
            if not result.valid:
                any_invalid = True

    if args.json:
        output = [
            {
                "entity": r.entity_name,
                "kind": r.entity_kind,
                "valid": r.valid,
                "errors": [
                    {"path": e.path, "message": e.message, "value": e.value}
                    for e in r.errors
                ],
                "warnings": r.warnings,
            }
            for r in all_results
        ]
        print(json.dumps(output, indent=2, default=str))
    else:
        for result in all_results:
            status = "✓" if result.valid else "✗"
            print(f"{status} {result.entity_kind}:{result.entity_name}")

            for error in result.errors:
                print(f"  ERROR [{error.path}]: {error.message}")
                if error.value is not None:
                    print(f"         Value: {error.value}")

            for warning in result.warnings:
                print(f"  WARNING: {warning}")

            print()

        # Summary
        valid_count = sum(1 for r in all_results if r.valid)
        total_count = len(all_results)
        print(f"Validated {total_count} entities: {valid_count} valid, {total_count - valid_count} invalid")

    if args.strict and any_invalid:
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate Datadog entity YAML files from collected metadata.

Supports all v3 entity kinds: service, datastore, queue, api, system.
Handles multi-entity files and merging with existing definitions.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EntityData:
    """Data for generating an entity definition."""

    kind: str  # service, datastore, queue, api, system
    name: str
    display_name: str | None = None
    description: str | None = None
    namespace: str = "default"
    owner: str | None = None
    additional_owners: list[dict] | None = None
    tags: list[str] = field(default_factory=list)
    contacts: list[dict] = field(default_factory=list)
    links: list[dict] = field(default_factory=list)

    # Spec fields
    lifecycle: str | None = None
    tier: str | None = None
    service_type: str | None = None
    languages: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    component_of: list[str] = field(default_factory=list)

    # Datastore/Queue specific
    datastore_type: str | None = None
    queue_type: str | None = None
    dependency_of: list[str] = field(default_factory=list)

    # API specific
    api_type: str | None = None
    api_interface_ref: str | None = None
    implemented_by: list[str] = field(default_factory=list)

    # System specific
    components: list[str] = field(default_factory=list)

    # Integrations
    pagerduty_url: str | None = None
    opsgenie_url: str | None = None
    opsgenie_region: str | None = None

    # Datadog specific
    code_locations: list[dict] = field(default_factory=list)
    log_queries: list[dict] = field(default_factory=list)
    event_queries: list[dict] = field(default_factory=list)

    # Extensions
    extensions: dict = field(default_factory=dict)


class EntityGenerator:
    """Generates Datadog entity YAML from EntityData."""

    def __init__(self, data: EntityData):
        self.data = data

    def generate(self) -> dict:
        """Generate the entity definition dictionary."""
        entity = {
            "apiVersion": "v3",
            "kind": self.data.kind,
            "metadata": self._build_metadata(),
        }

        # Add spec based on kind
        spec = self._build_spec()
        if spec:
            entity["spec"] = spec

        # Add integrations
        integrations = self._build_integrations()
        if integrations:
            entity["integrations"] = integrations

        # Add datadog section
        datadog = self._build_datadog()
        if datadog:
            entity["datadog"] = datadog

        # Add extensions
        if self.data.extensions:
            entity["extensions"] = self.data.extensions

        return entity

    def _build_metadata(self) -> dict:
        """Build the metadata section."""
        metadata: dict[str, Any] = {"name": self.data.name}

        if self.data.display_name:
            metadata["displayName"] = self.data.display_name

        if self.data.namespace and self.data.namespace != "default":
            metadata["namespace"] = self.data.namespace

        if self.data.owner:
            metadata["owner"] = self.data.owner

        if self.data.additional_owners:
            metadata["additionalOwners"] = self.data.additional_owners

        if self.data.description:
            metadata["description"] = self.data.description

        if self.data.tags:
            metadata["tags"] = self.data.tags

        if self.data.contacts:
            metadata["contacts"] = self.data.contacts

        if self.data.links:
            metadata["links"] = self.data.links

        return metadata

    def _build_spec(self) -> dict | None:
        """Build the spec section based on entity kind."""
        spec: dict[str, Any] = {}

        # Common fields
        if self.data.lifecycle:
            spec["lifecycle"] = self.data.lifecycle

        if self.data.tier:
            spec["tier"] = self.data.tier

        # Kind-specific fields
        if self.data.kind == "service":
            if self.data.service_type:
                spec["type"] = self.data.service_type
            if self.data.languages:
                spec["languages"] = self.data.languages
            if self.data.depends_on:
                spec["dependsOn"] = self.data.depends_on
            if self.data.component_of:
                spec["componentOf"] = self.data.component_of

        elif self.data.kind == "datastore":
            if self.data.datastore_type:
                spec["type"] = self.data.datastore_type
            if self.data.component_of:
                spec["componentOf"] = self.data.component_of
            if self.data.depends_on:
                spec["dependsOn"] = self.data.depends_on
            if self.data.dependency_of:
                spec["dependencyOf"] = self.data.dependency_of

        elif self.data.kind == "queue":
            if self.data.queue_type:
                spec["type"] = self.data.queue_type
            if self.data.component_of:
                spec["componentOf"] = self.data.component_of

        elif self.data.kind == "api":
            if self.data.api_type:
                spec["type"] = self.data.api_type
            if self.data.api_interface_ref:
                spec["interface"] = {"fileRef": self.data.api_interface_ref}
            if self.data.implemented_by:
                spec["implementedBy"] = self.data.implemented_by
            if self.data.component_of:
                spec["componentOf"] = self.data.component_of

        elif self.data.kind == "system":
            if self.data.service_type:
                spec["type"] = self.data.service_type
            if self.data.components:
                spec["components"] = self.data.components
            if self.data.component_of:
                spec["componentOf"] = self.data.component_of

        return spec if spec else None

    def _build_integrations(self) -> dict | None:
        """Build the integrations section."""
        integrations: dict[str, Any] = {}

        if self.data.pagerduty_url:
            integrations["pagerduty"] = {"serviceURL": self.data.pagerduty_url}

        if self.data.opsgenie_url:
            opsgenie: dict[str, Any] = {"serviceURL": self.data.opsgenie_url}
            if self.data.opsgenie_region:
                opsgenie["region"] = self.data.opsgenie_region
            integrations["opsgenie"] = opsgenie

        return integrations if integrations else None

    def _build_datadog(self) -> dict | None:
        """Build the datadog section."""
        datadog: dict[str, Any] = {}

        if self.data.code_locations:
            datadog["codeLocations"] = self.data.code_locations

        if self.data.log_queries:
            datadog["logs"] = self.data.log_queries

        if self.data.event_queries:
            datadog["events"] = self.data.event_queries

        return datadog if datadog else None

    def to_yaml(self) -> str:
        """Generate YAML string."""
        entity = self.generate()
        return yaml.dump(entity, default_flow_style=False, sort_keys=False, indent=2)


def merge_entities(existing: dict, new: dict) -> dict:
    """
    Deep merge new entity data into existing.
    New values override existing, arrays are extended (deduplicated).
    """
    result = existing.copy()

    for key, new_value in new.items():
        if key not in result:
            result[key] = new_value
        elif isinstance(new_value, dict) and isinstance(result[key], dict):
            result[key] = merge_entities(result[key], new_value)
        elif isinstance(new_value, list) and isinstance(result[key], list):
            # Extend and deduplicate
            combined = result[key] + [
                item for item in new_value if item not in result[key]
            ]
            result[key] = combined
        else:
            # New value overrides
            result[key] = new_value

    return result


def load_existing_file(path: Path) -> list[dict]:
    """Load existing entity file, handling multi-document YAML."""
    if not path.exists():
        return []

    with open(path) as f:
        docs = list(yaml.safe_load_all(f))

    return [doc for doc in docs if doc]


def save_entities(entities: list[dict], path: Path) -> None:
    """Save entities to YAML file with --- separators."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        for i, entity in enumerate(entities):
            if i > 0:
                f.write("---\n")
            yaml.dump(entity, f, default_flow_style=False, sort_keys=False, indent=2)


def entity_from_json(data: dict) -> EntityData:
    """Create EntityData from a JSON/dict input."""
    return EntityData(
        kind=data.get("kind", "service"),
        name=data["name"],
        display_name=data.get("display_name"),
        description=data.get("description"),
        namespace=data.get("namespace", "default"),
        owner=data.get("owner"),
        additional_owners=data.get("additional_owners"),
        tags=data.get("tags", []),
        contacts=data.get("contacts", []),
        links=data.get("links", []),
        lifecycle=data.get("lifecycle"),
        tier=data.get("tier"),
        service_type=data.get("service_type") or data.get("type"),
        languages=data.get("languages", []),
        depends_on=data.get("depends_on", []),
        component_of=data.get("component_of", []),
        datastore_type=data.get("datastore_type"),
        queue_type=data.get("queue_type"),
        dependency_of=data.get("dependency_of", []),
        api_type=data.get("api_type"),
        api_interface_ref=data.get("api_interface_ref"),
        implemented_by=data.get("implemented_by", []),
        components=data.get("components", []),
        pagerduty_url=data.get("pagerduty_url"),
        opsgenie_url=data.get("opsgenie_url"),
        opsgenie_region=data.get("opsgenie_region"),
        code_locations=data.get("code_locations", []),
        log_queries=data.get("log_queries", []),
        event_queries=data.get("event_queries", []),
        extensions=data.get("extensions", {}),
    )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Datadog entity YAML")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input JSON file with entity data",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(".datadog"),
        help="Output directory (default: .datadog)",
    )
    parser.add_argument(
        "--filename",
        "-f",
        default="entity.datadog.yaml",
        help="Output filename (default: entity.datadog.yaml)",
    )
    parser.add_argument(
        "--merge",
        "-m",
        action="store_true",
        help="Merge with existing file if present",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Print YAML without saving",
    )

    args = parser.parse_args()

    # Read input data
    if args.input:
        with open(args.input) as f:
            input_data = json.load(f)
    else:
        # Read from stdin
        input_data = json.load(sys.stdin)

    # Handle single entity or list of entities
    if isinstance(input_data, list):
        entities_data = input_data
    else:
        entities_data = [input_data]

    # Generate entities
    new_entities = []
    for data in entities_data:
        entity_data = entity_from_json(data)
        generator = EntityGenerator(entity_data)
        new_entities.append(generator.generate())

    # Handle output
    output_path = args.output / args.filename

    if args.merge and output_path.exists():
        existing_entities = load_existing_file(output_path)

        # Merge by name
        existing_by_name = {
            e.get("metadata", {}).get("name"): e for e in existing_entities
        }

        merged_entities = []
        for new_entity in new_entities:
            name = new_entity.get("metadata", {}).get("name")
            if name in existing_by_name:
                merged = merge_entities(existing_by_name[name], new_entity)
                merged_entities.append(merged)
                del existing_by_name[name]
            else:
                merged_entities.append(new_entity)

        # Add remaining existing entities
        merged_entities.extend(existing_by_name.values())
        final_entities = merged_entities
    else:
        final_entities = new_entities

    if args.dry_run:
        for i, entity in enumerate(final_entities):
            if i > 0:
                print("---")
            print(
                yaml.dump(entity, default_flow_style=False, sort_keys=False, indent=2)
            )
    else:
        save_entities(final_entities, output_path)
        print(f"Saved {len(final_entities)} entities to {output_path}")


if __name__ == "__main__":
    main()

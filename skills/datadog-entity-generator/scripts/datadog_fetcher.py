#!/usr/bin/env python3
"""
Fetch existing Datadog data for entity generation context.

Queries:
- Existing entity definitions
- Teams (for owner validation)
- Related services and dependencies
- Monitors and SLOs
- APM service topology
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.exceptions import ApiException


@dataclass
class DatadogContext:
    """Context fetched from Datadog APIs."""

    existing_entity: dict | None = None
    teams: list[dict] = field(default_factory=list)
    related_services: list[dict] = field(default_factory=list)
    monitors: list[dict] = field(default_factory=list)
    slos: list[dict] = field(default_factory=list)
    apm_dependencies: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "existing_entity": self.existing_entity,
            "teams": self.teams,
            "related_services": self.related_services,
            "monitors": self.monitors,
            "slos": self.slos,
            "apm_dependencies": self.apm_dependencies,
            "errors": self.errors,
        }


class DatadogFetcher:
    """Fetches context from Datadog APIs."""

    def __init__(self, service_name: str | None = None):
        self.service_name = service_name
        self.result = DatadogContext()
        self.config = self._create_config()

    def _create_config(self) -> Configuration:
        """Create Datadog API client configuration."""
        config = Configuration()

        # Check for required env vars
        if not os.environ.get("DD_API_KEY"):
            self.result.errors.append("DD_API_KEY environment variable not set")
        if not os.environ.get("DD_APP_KEY"):
            self.result.errors.append("DD_APP_KEY environment variable not set")

        # Enable retry and unstable operations
        config.enable_retry = True
        config.max_retries = 3
        config.unstable_operations["list_catalog_entity"] = True
        config.unstable_operations["get_catalog_entity"] = True

        return config

    def fetch_all(self) -> DatadogContext:
        """Fetch all relevant context from Datadog."""
        if self.result.errors:
            return self.result

        self._fetch_teams()

        if self.service_name:
            self._fetch_existing_entity()
            self._fetch_monitors()
            self._fetch_slos()
            self._fetch_apm_dependencies()
            self._fetch_related_services()

        return self.result

    def _fetch_teams(self) -> None:
        """Fetch all teams from Datadog."""
        try:
            from datadog_api_client.v2.api.teams_api import TeamsApi

            with ApiClient(self.config) as api_client:
                api_instance = TeamsApi(api_client)
                teams = []

                # Paginate through all teams
                page_size = 100
                page_number = 0

                while True:
                    response = api_instance.list_teams(
                        page_size=page_size, page_number=page_number
                    )
                    if not response.data:
                        break

                    for team in response.data:
                        teams.append(
                            {
                                "id": team.id,
                                "handle": team.attributes.handle,
                                "name": team.attributes.name,
                                "description": getattr(
                                    team.attributes, "description", None
                                ),
                            }
                        )

                    if len(response.data) < page_size:
                        break
                    page_number += 1

                self.result.teams = teams

        except ApiException as e:
            self.result.errors.append(f"Error fetching teams: {e.status} - {e.body}")
        except Exception as e:
            self.result.errors.append(f"Error fetching teams: {e}")

    def _fetch_existing_entity(self) -> None:
        """Fetch existing entity definition for the service."""
        if not self.service_name:
            return

        try:
            from datadog_api_client.v2.api.software_catalog_api import (
                SoftwareCatalogApi,
            )

            with ApiClient(self.config) as api_client:
                api_instance = SoftwareCatalogApi(api_client)

                # Try to get the entity by name
                entity_id = f"service:{self.service_name}"
                try:
                    response = api_instance.get_catalog_entity(entity_id)
                    if response.data:
                        entity = response.data
                        self.result.existing_entity = {
                            "id": entity.id,
                            "type": entity.type,
                            "attributes": (
                                entity.attributes.to_dict()
                                if hasattr(entity.attributes, "to_dict")
                                else str(entity.attributes)
                            ),
                        }
                except ApiException as e:
                    if e.status != 404:
                        self.result.errors.append(
                            f"Error fetching entity: {e.status} - {e.body}"
                        )

        except ImportError:
            # Fall back to service definition API
            self._fetch_existing_service_definition()
        except Exception as e:
            self.result.errors.append(f"Error fetching entity: {e}")

    def _fetch_existing_service_definition(self) -> None:
        """Fetch existing service definition (v2 API fallback)."""
        if not self.service_name:
            return

        try:
            from datadog_api_client.v2.api.service_definition_api import (
                ServiceDefinitionApi,
            )

            with ApiClient(self.config) as api_client:
                api_instance = ServiceDefinitionApi(api_client)

                try:
                    response = api_instance.get_service_definition(self.service_name)
                    if response.data:
                        self.result.existing_entity = {
                            "schema": (
                                response.data.attributes.schema.to_dict()
                                if hasattr(response.data.attributes.schema, "to_dict")
                                else response.data.attributes.schema
                            )
                        }
                except ApiException as e:
                    if e.status != 404:
                        self.result.errors.append(
                            f"Error fetching service definition: {e.status}"
                        )

        except Exception as e:
            self.result.errors.append(f"Error fetching service definition: {e}")

    def _fetch_monitors(self) -> None:
        """Fetch monitors associated with the service."""
        if not self.service_name:
            return

        try:
            from datadog_api_client.v1.api.monitors_api import MonitorsApi

            with ApiClient(self.config) as api_client:
                api_instance = MonitorsApi(api_client)

                # Search for monitors with service tag
                monitors = api_instance.list_monitors(
                    tags=f"service:{self.service_name}"
                )

                self.result.monitors = [
                    {
                        "id": m.id,
                        "name": m.name,
                        "type": str(m.type) if m.type else None,
                        "tags": m.tags or [],
                    }
                    for m in (monitors or [])[:20]  # Limit to 20
                ]

        except ApiException as e:
            self.result.errors.append(f"Error fetching monitors: {e.status}")
        except Exception as e:
            self.result.errors.append(f"Error fetching monitors: {e}")

    def _fetch_slos(self) -> None:
        """Fetch SLOs associated with the service."""
        if not self.service_name:
            return

        try:
            from datadog_api_client.v1.api.service_level_objectives_api import (
                ServiceLevelObjectivesApi,
            )

            with ApiClient(self.config) as api_client:
                api_instance = ServiceLevelObjectivesApi(api_client)

                # Get SLOs filtered by service tag
                response = api_instance.list_sl_os(
                    tags_query=f"service:{self.service_name}"
                )

                if response.data:
                    self.result.slos = [
                        {
                            "id": slo.id,
                            "name": slo.name,
                            "type": str(slo.type) if slo.type else None,
                            "tags": slo.tags or [],
                        }
                        for slo in response.data[:10]  # Limit to 10
                    ]

        except ApiException as e:
            self.result.errors.append(f"Error fetching SLOs: {e.status}")
        except Exception as e:
            self.result.errors.append(f"Error fetching SLOs: {e}")

    def _fetch_apm_dependencies(self) -> None:
        """Fetch APM service dependencies."""
        if not self.service_name:
            return

        try:
            from datadog_api_client.v1.api.service_dependencies_api import (
                ServiceDependenciesApi,
            )

            with ApiClient(self.config) as api_client:
                api_instance = ServiceDependenciesApi(api_client)

                try:
                    response = api_instance.list_service_dependencies(
                        service_name=self.service_name
                    )

                    if response.data:
                        self.result.apm_dependencies = [
                            {
                                "name": dep.attributes.service_name
                                if hasattr(dep.attributes, "service_name")
                                else str(dep),
                                "type": "service",
                            }
                            for dep in response.data[:20]
                        ]
                except ApiException as e:
                    if e.status != 404:
                        self.result.errors.append(
                            f"Error fetching APM dependencies: {e.status}"
                        )

        except (ImportError, AttributeError):
            # API might not be available
            pass
        except Exception as e:
            self.result.errors.append(f"Error fetching APM dependencies: {e}")

    def _fetch_related_services(self) -> None:
        """Fetch related services from the catalog."""
        try:
            from datadog_api_client.v2.api.service_definition_api import (
                ServiceDefinitionApi,
            )

            with ApiClient(self.config) as api_client:
                api_instance = ServiceDefinitionApi(api_client)

                # List all service definitions (paginated)
                response = api_instance.list_service_definitions(page_size=100)

                if response.data:
                    for service in response.data[:50]:  # Limit to 50
                        try:
                            attrs = service.attributes
                            schema = attrs.schema if hasattr(attrs, "schema") else None

                            if schema:
                                # Extract basic info
                                name = (
                                    schema.get("dd-service")
                                    or schema.get("metadata", {}).get("name")
                                    or str(service.id)
                                )
                                self.result.related_services.append(
                                    {
                                        "name": name,
                                        "schema_version": schema.get("schema-version")
                                        or schema.get("apiVersion"),
                                    }
                                )
                        except Exception:
                            continue

        except ApiException as e:
            self.result.errors.append(f"Error fetching related services: {e.status}")
        except Exception as e:
            self.result.errors.append(f"Error fetching related services: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch Datadog context for entity generation"
    )
    parser.add_argument(
        "--service-name",
        "-s",
        help="Service name to fetch context for",
    )
    parser.add_argument(
        "--teams-only",
        action="store_true",
        help="Only fetch teams list",
    )

    args = parser.parse_args()

    fetcher = DatadogFetcher(service_name=args.service_name)

    if args.teams_only:
        fetcher._fetch_teams()
        result = {"teams": fetcher.result.teams, "errors": fetcher.result.errors}
    else:
        result = fetcher.fetch_all().to_dict()

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

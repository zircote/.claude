# Datadog Software Catalog v3 Schema Reference

## Entity Kinds

v3 supports five entity kinds:

| Kind | Description | Use Case |
|------|-------------|----------|
| `service` | Application services | APIs, workers, web apps |
| `datastore` | Databases and data stores | PostgreSQL, Redis, MongoDB |
| `queue` | Message queues | Kafka, RabbitMQ, SQS |
| `api` | API definitions | OpenAPI, GraphQL schemas |
| `system` | Logical grouping | Product domains, platforms |

## Required Fields (All Kinds)

```yaml
apiVersion: v3          # Always "v3"
kind: <kind>            # service | datastore | queue | api | system
metadata:
  name: <unique-name>   # Required, lowercase, hyphens, no spaces
```

## Metadata Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Unique identifier, must match service tag |
| `displayName` | No | string | Human-readable name for UI |
| `namespace` | No | string | Defaults to "default" |
| `owner` | No | string | Primary owner team handle |
| `additionalOwners` | No | array | Additional owners with roles |
| `description` | No | string | Short description |
| `tags` | No | array | Custom tags in `key:value` format |
| `contacts` | No | array | Contact methods |
| `links` | No | array | Related URLs |

### Contacts Schema

```yaml
contacts:
  - name: "Display Name"          # Required
    type: email                   # Required: email | slack | microsoft-teams
    contact: "email@example.com"  # Required, format depends on type
```

**Contact types:**
- `email` - Email address (validated format)
- `microsoft-teams` - Teams channel URL
- `slack` - Slack channel URL (but NO SLACK for HMH)

### Links Schema

```yaml
links:
  - name: "Display Name"      # Required
    type: runbook             # Required: runbook | doc | repo | dashboard | other
    url: "https://..."        # Required, valid URI
    provider: github          # Optional: github | confluence | gitlab | bitbucket
```

**Link types:**
- `runbook` - Operational runbook
- `doc` - Documentation
- `repo` - Source code repository
- `dashboard` - Monitoring dashboard
- `other` - Anything else

## Spec Fields by Kind

### Service Spec

```yaml
spec:
  lifecycle: production     # production | experimental | deprecated
  tier: critical            # critical | high | medium | low (or 1, 2, 3, 4)
  type: web                 # web | grpc | rest | graphql | worker | http
  languages:                # Array of language identifiers
    - python
    - go
    - java
    - js
    - ruby
    - dotnet
    - php
    - c++
  dependsOn:                # Dependencies (other entities)
    - service:auth-api
    - datastore:users-db
    - queue:events-kafka
  componentOf:              # Parent systems
    - system:ecommerce-platform
```

### Datastore Spec

```yaml
spec:
  lifecycle: production
  tier: critical
  type: postgres            # postgres | mysql | redis | mongodb | cassandra | elasticsearch | dynamodb
  componentOf:
    - system:data-platform
  dependencyOf:             # Services that depend on this datastore
    - service:api-service
```

### Queue Spec

```yaml
spec:
  lifecycle: production
  tier: high
  type: kafka               # kafka | rabbitmq | sqs | kinesis | pubsub
  componentOf:
    - system:messaging
```

### API Spec

```yaml
spec:
  lifecycle: production
  tier: high
  type: openapi             # openapi | graphql | rest | grpc
  interface:
    fileRef: "https://github.com/org/repo/openapi.yaml"  # OR
    definition: { ... }     # Inline OpenAPI definition
  implementedBy:
    - service:api-gateway
  componentOf:
    - system:public-api
```

### System Spec

```yaml
spec:
  lifecycle: production
  tier: critical
  type: public-web          # Descriptive type
  components:               # Entities in this system
    - service:web-frontend
    - service:api-backend
    - datastore:main-db
    - queue:events
  componentOf:              # Parent systems (nested)
    - system:enterprise-platform
```

## Integrations

### PagerDuty

```yaml
integrations:
  pagerduty:
    serviceURL: "https://company.pagerduty.com/service-directory/PXXXXXX"
```

URL pattern: `https://<subdomain>.pagerduty.com/service-directory/P[A-Za-z0-9]+`

### OpsGenie

```yaml
integrations:
  opsgenie:
    serviceURL: "https://company.opsgenie.com/service/..."
    region: US              # US | EU
```

## Datadog Product Integrations

```yaml
datadog:
  codeLocations:
    - repositoryURL: "https://github.com/org/repo"
      paths:
        - "src/**"
        - "lib/**"
  logs:
    - name: "Error Logs"
      query: "service:my-service status:error"
    - name: "Audit Logs"  
      query: "service:my-service @audit:*"
  events:
    - name: "Deployments"
      query: "source:kubernetes service:my-service"
    - name: "Config Changes"
      query: "source:chef service:my-service"
  pipelines:
    fingerprints:
      - "fp1"
      - "fp2"
```

## Extensions

Custom metadata via extensions field:

```yaml
extensions:
  # Datadog-specific extensions
  datadoghq.com/dora-metrics:
    codeLocationFilters:
      - "src/**"
  datadoghq.com/cd-visibility:
    deploymentBranchPatterns:
      - "main"
      - "release/*"
  
  # Organization-specific
  company.com/jira-project: "PROJ-KEY"
  company.com/confluence-space: "https://confluence.company.com/space"
  company.com/cost-center: "engineering"
  company.com/compliance: "pci-dss"
  company.com/snyk-project: "org/project"
  company.com/sonarqube-project: "project-key"
  company.com/browserstack-project: "project-id"
  company.com/orca-asset: "asset-id"
```

## Multi-Entity Files

Separate multiple entities with `---`:

```yaml
apiVersion: v3
kind: service
metadata:
  name: service-one
---
apiVersion: v3
kind: datastore
metadata:
  name: datastore-one
---
apiVersion: v3
kind: system
metadata:
  name: system-one
spec:
  components:
    - service:service-one
    - datastore:datastore-one
```

## Metadata Inheritance

Components within a system inherit:
- `owner`
- `tags`

Override by explicitly setting on the component.

## Name Requirements

- Lowercase alphanumeric and hyphens only
- Must start with letter
- No spaces or underscores
- Must match the `service` tag in APM/traces for auto-correlation

## Tag Format

Tags must be `key:value` format:

```yaml
tags:
  - env:production
  - service:my-service
  - tier:critical
  - team:platform
  - domain:commerce
```

## JSON Schema URLs

For programmatic validation:

- Entity (all kinds): `https://raw.githubusercontent.com/DataDog/schema/main/service-catalog/entity.schema.json`
- Service: `https://raw.githubusercontent.com/DataDog/schema/main/service-catalog/v3/service.schema.json`
- System: `https://raw.githubusercontent.com/DataDog/schema/main/service-catalog/v3/system.schema.json`
- Datastore: `https://raw.githubusercontent.com/DataDog/schema/main/service-catalog/v3/datastore.schema.json`
- Queue: `https://raw.githubusercontent.com/DataDog/schema/main/service-catalog/v3/queue.schema.json`
- API: `https://raw.githubusercontent.com/DataDog/schema/main/service-catalog/v3/api.schema.json`

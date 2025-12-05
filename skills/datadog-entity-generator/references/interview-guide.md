# Engineer Interview Guide

Structured questions to gather complete entity metadata. Present auto-detected values first for confirmation, then ask for missing information.

## Interview Flow

1. **Confirm auto-detected values** (batch)
2. **Core identification** (required fields)
3. **Ownership & contacts**
4. **Dependencies & relationships**
5. **Integrations & tooling**
6. **Optional metadata negotiation**

## Opening Statement

> I've analyzed your project and detected some metadata. I'll walk through what I found and ask for any missing details needed for a complete Datadog entity definition.

## Phase 1: Confirm Auto-Detected Values

Present all detected values in a summary table:

> Based on project analysis, I detected:
> 
> | Field | Detected Value | Confidence |
> |-------|----------------|------------|
> | Name | `my-service` | 95% |
> | Language | Python | 98% |
> | ...
> 
> Are these correct? Please note any corrections.

## Phase 2: Core Identification

### Entity Kind

> What type of entity is this?
> - **Service** - An application/microservice (web API, worker, etc.)
> - **Datastore** - A database or data store (PostgreSQL, Redis, etc.)
> - **Queue** - A message queue (Kafka, RabbitMQ, etc.)
> - **API** - An API definition (OpenAPI spec, GraphQL schema)
> - **System** - A logical grouping of multiple components

### Service Name (if not detected)

> What is the service name? This should:
> - Be lowercase with hyphens (no spaces/underscores)
> - Match your APM service tag exactly
> - Be unique across all services
> 
> Example: `payment-processing-api`

### Display Name

> What human-readable name should appear in the UI?
> 
> Example: "Payment Processing API"

### Description

> Provide a one-sentence description of what this service does.
> 
> Example: "Handles payment processing, fraud detection, and transaction management."

## Phase 3: Ownership & Contacts

### Primary Owner

> Which team owns this service? 
> 
> (I found these teams in Datadog: [list teams from API])
> 
> If your team isn't listed, I can use any team handle.

### Additional Owners (Optional)

> Are there other teams with ownership roles?
> - **operator** - Team that operates/maintains
> - **stakeholder** - Team with oversight interest
> 
> Example: `sre-team` as operator, `security-team` as stakeholder

### Contacts

> What contact methods should be listed? (Provide for each)

**Email contact:**
> On-call email distribution list?
> Example: `payments-oncall@company.com`

**MS Teams channel:**
> Team's primary Teams channel URL?
> Format: `https://teams.microsoft.com/l/channel/...`

**PagerDuty (if applicable):**
> PagerDuty service URL?
> Format: `https://<subdomain>.pagerduty.com/service-directory/PXXXXXX`

## Phase 4: Dependencies & Relationships

### Service Dependencies (for services)

> What services does this depend on? List as comma-separated names.
> 
> Examples: `auth-service, notification-api, user-service`

### Datastore Dependencies

> What databases/data stores does this service use?
> 
> | Datastore Name | Type |
> |----------------|------|
> | Example: `users-db` | postgres |
> | Example: `cache` | redis |

### Queue Dependencies

> What message queues does this service produce to or consume from?
> 
> | Queue Name | Type | Role |
> |------------|------|------|
> | Example: `events` | kafka | producer |
> | Example: `notifications` | sqs | consumer |

### System Membership

> Is this service part of a larger system/platform?
> 
> Example: `platform`, `ecommerce`, `data-pipeline`

## Phase 5: Integrations & Tooling

### Required Tags (HMH Standards)

> Confirm these tag values:
> - **env**: `production` / `staging` / `development`?
> - **tier**: `critical` / `high` / `medium` / `low`?
> - **Additional tags** (domain, compliance, etc.)?

### Lifecycle

> What is the service lifecycle state?
> - **production** - Actively serving production traffic
> - **experimental** - In development/testing
> - **deprecated** - Being phased out

### Service Type (for services)

> What type of service is this?
> - **web** - HTTP web service
> - **rest** - REST API
> - **grpc** - gRPC service
> - **graphql** - GraphQL API
> - **worker** - Background worker/job processor

### External Tool Links

**Runbook:**
> URL to operational runbook (Confluence, Wiki, etc.)?

**Dashboard:**
> Datadog dashboard URL for this service?

**Source Repository:**
> GitHub/GitLab repository URL?

**JIRA Project:**
> JIRA project key? (e.g., `PROJ`)

**Confluence Space:**
> Confluence space URL for documentation?

**Other Tools (Optional):**
> Any of these configured?
> - Snyk project ID
> - SonarQube project key
> - BrowserStack project
> - Orca asset ID

## Phase 6: Optional Field Negotiation

For each optional field without a value:

> I can include these optional fields. For each, let me know if you want to:
> - **Provide a value** - I'll add it
> - **Skip** - I'll omit it from the definition
> 
> | Optional Field | Description |
> |----------------|-------------|
> | Additional owners | Other teams with roles |
> | Custom extensions | Organization-specific metadata |
> | Log queries | Predefined log search queries |
> | Event queries | Predefined event search queries |
> | Code locations | Source paths for DORA metrics |

## Validation During Interview

**URL validation:**
- Check format matches expected patterns
- Verify URL is accessible (if possible)

**Team validation:**
- Check against Datadog Teams API
- Warn if team not found (might be new)

**Dependency validation:**
- Check referenced services exist in Datadog
- Note if dependencies are not yet cataloged

## Summary & Confirmation

Before generating:

> Here's the complete entity definition I'll generate:
> 
> ```yaml
> [preview YAML]
> ```
> 
> Confirm this looks correct, or note any changes needed.

## Question Prioritization

**Always ask (required/high-value):**
1. Entity kind
2. Service name (confirm or provide)
3. Owner team
4. Tier
5. Lifecycle
6. Primary contact

**Ask if missing (recommended):**
7. Dependencies
8. Runbook link
9. Repository link
10. PagerDuty integration

**Negotiate (optional):**
11. Additional owners
12. Display name (if different from name)
13. Custom extensions
14. Log/event queries

## Multi-Entity Scenarios

For monorepos:

> This project appears to contain multiple services. I'll generate separate entity definitions for each, combined in a single file with `---` separators.
> 
> Detected services: [list]
> 
> Should I proceed with all of these, or focus on specific ones?

For systems with components:

> Do you want me to also generate entity definitions for the components (datastores, queues) that this service depends on?

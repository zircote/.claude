# Integration URL Patterns

Valid URL formats and patterns for Datadog entity integrations.

## Built-in Integrations

### PagerDuty

**Schema field:** `integrations.pagerduty.serviceURL`

**Pattern:** `https://<subdomain>.pagerduty.com/service-directory/P<alphanumeric>`

**Regex:** `^https?://[a-zA-Z\d_\-.]+\.pagerduty\.com/service-directory/(P[a-zA-Z\d_\-]+)/?$`

**Examples:**
```
https://company.pagerduty.com/service-directory/P123ABC
https://myorg.pagerduty.com/service-directory/PXYZ789
```

**How to find:**
1. Go to PagerDuty → Services
2. Select your service
3. Copy URL from browser

### OpsGenie

**Schema field:** `integrations.opsgenie.serviceURL` and `integrations.opsgenie.region`

**Pattern:** `https://<subdomain>.opsgenie.com/service/<uuid>`

**Region values:** `US` or `EU`

**Examples:**
```yaml
integrations:
  opsgenie:
    serviceURL: "https://company.opsgenie.com/service/123e4567-e89b-12d3-a456-426614174000"
    region: US
```

## Link Types

### Runbook

**Schema field:** `metadata.links[]` with `type: runbook`

**Common providers:**
- Confluence: `https://<instance>.atlassian.net/wiki/spaces/<space>/pages/<id>`
- GitBook: `https://<org>.gitbook.io/<book>/<page>`
- Notion: `https://www.notion.so/<workspace>/<page-id>`
- Internal wiki: Any valid URL

**Example:**
```yaml
links:
  - name: Runbook
    type: runbook
    provider: confluence
    url: "https://company.atlassian.net/wiki/spaces/ENG/pages/123456/Service+Runbook"
```

### Documentation

**Schema field:** `metadata.links[]` with `type: doc`

**Examples:**
```yaml
links:
  - name: API Documentation
    type: doc
    provider: confluence
    url: "https://company.atlassian.net/wiki/spaces/API/pages/789"
  - name: Architecture Docs
    type: doc
    provider: github
    url: "https://github.com/org/repo/blob/main/docs/architecture.md"
```

### Repository

**Schema field:** `metadata.links[]` with `type: repo`

**Provider patterns:**
- GitHub: `https://github.com/<org>/<repo>`
- GitLab: `https://gitlab.com/<org>/<repo>` or self-hosted
- Bitbucket: `https://bitbucket.org/<workspace>/<repo>`
- Azure DevOps: `https://dev.azure.com/<org>/<project>/_git/<repo>`

**Example:**
```yaml
links:
  - name: Source Code
    type: repo
    provider: github
    url: "https://github.com/company/payment-service"
```

### Dashboard

**Schema field:** `metadata.links[]` with `type: dashboard`

**Datadog pattern:** `https://app.datadoghq.com/dashboard/<dashboard-id>`

**Example:**
```yaml
links:
  - name: Service Dashboard
    type: dashboard
    url: "https://app.datadoghq.com/dashboard/abc-def-123"
```

## Contact Types

### Email

**Schema field:** `metadata.contacts[]` with `type: email`

**Format:** Valid email address (RFC 5322)

**Example:**
```yaml
contacts:
  - name: On-Call
    type: email
    contact: "oncall@company.com"
```

### Microsoft Teams (NO SLACK for HMH)

**Schema field:** `metadata.contacts[]` with `type: microsoft-teams`

**Pattern:** `https://teams.microsoft.com/l/channel/<channel-id>/<channel-name>?groupId=<group-id>&tenantId=<tenant-id>`

**How to find:**
1. In Teams, right-click channel
2. Select "Get link to channel"
3. Copy URL

**Example:**
```yaml
contacts:
  - name: Engineering Team Channel
    type: microsoft-teams
    contact: "https://teams.microsoft.com/l/channel/19%3a1234567890abcdef%40thread.tacv2/General?groupId=abc-123&tenantId=xyz-789"
```

## Custom Extensions (HMH Standard Tools)

### JIRA

**Extension field:** `extensions.company.com/jira-project`

**Format:** JIRA project key (uppercase letters)

**Example:**
```yaml
extensions:
  company.com/jira-project: "PAYMENTS"
```

**Full JIRA URL in links:**
```yaml
links:
  - name: JIRA Board
    type: other
    url: "https://company.atlassian.net/browse/PAYMENTS"
```

### Confluence

**Extension field or link:**

As link:
```yaml
links:
  - name: Documentation
    type: doc
    provider: confluence
    url: "https://company.atlassian.net/wiki/spaces/PAYMENTS"
```

As extension:
```yaml
extensions:
  company.com/confluence-space: "https://company.atlassian.net/wiki/spaces/PAYMENTS"
```

### Snyk

**Extension field:** `extensions.company.com/snyk-project`

**Format:** `<org>/<project>` or project UUID

**Example:**
```yaml
extensions:
  company.com/snyk-project: "company-org/payment-service"
```

### SonarQube

**Extension field:** `extensions.company.com/sonarqube-project`

**Format:** Project key as configured in SonarQube

**Example:**
```yaml
extensions:
  company.com/sonarqube-project: "com.company:payment-service"
```

### BrowserStack

**Extension field:** `extensions.company.com/browserstack-project`

**Format:** Project ID from BrowserStack

**Example:**
```yaml
extensions:
  company.com/browserstack-project: "payment-ui-tests"
```

### Orca Security

**Extension field:** `extensions.company.com/orca-asset`

**Format:** Asset ID from Orca

**Example:**
```yaml
extensions:
  company.com/orca-asset: "asset-123456"
```

## Datadog-Specific Extensions

### DORA Metrics

**Extension field:** `extensions.datadoghq.com/dora-metrics`

```yaml
extensions:
  datadoghq.com/dora-metrics:
    codeLocationFilters:
      - "src/**"
      - "lib/**"
```

### CD Visibility

**Extension field:** `extensions.datadoghq.com/cd-visibility`

```yaml
extensions:
  datadoghq.com/cd-visibility:
    deploymentBranchPatterns:
      - "main"
      - "release/*"
```

## Code Locations

**Schema field:** `datadog.codeLocations`

```yaml
datadog:
  codeLocations:
    - repositoryURL: "https://github.com/company/repo"
      paths:
        - "src/payments/**"
        - "lib/payment-core/**"
```

**Repository URL:** Must match a repo in Datadog Source Code Integration

**Paths:** Glob patterns relative to repository root

## Log Queries

**Schema field:** `datadog.logs`

**Query syntax:** Datadog log query language

```yaml
datadog:
  logs:
    - name: "Error Logs"
      query: "service:payment-api status:error"
    - name: "Transaction Logs"
      query: "service:payment-api @transaction.type:payment"
    - name: "High Latency"
      query: "service:payment-api @duration:>1000ms"
```

## Event Queries

**Schema field:** `datadog.events`

**Query syntax:** Datadog event query language

```yaml
datadog:
  events:
    - name: "Deployments"
      query: "source:kubernetes service:payment-api"
    - name: "Incidents"
      query: "source:pagerduty service:payment-api"
    - name: "Config Changes"
      query: "source:terraform service:payment-api"
```

## URL Validation Regex Patterns

```python
PATTERNS = {
    "pagerduty": r"^https?://[a-zA-Z\d_\-.]+\.pagerduty\.com/service-directory/(P[a-zA-Z\d_\-]+)/?$",
    "github_repo": r"^https://github\.com/[\w\-]+/[\w\-\.]+/?$",
    "gitlab_repo": r"^https://gitlab\.com/[\w\-]+/[\w\-\.]+/?$",
    "datadog_dashboard": r"^https://app\.datadoghq\.com/dashboard/[\w\-]+",
    "confluence": r"^https://[\w\-]+\.atlassian\.net/wiki/",
    "jira_project": r"^[A-Z][A-Z0-9]+$",
    "teams_channel": r"^https://teams\.microsoft\.com/l/channel/",
    "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
}
```

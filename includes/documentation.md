# Documentation Standards

## README Structure

Every project should have a README.md with these sections:

```markdown
# Project Name

Brief one-line description of what this project does.

## Overview

2-3 sentences explaining the project's purpose, who it's for, and why it exists.
Include key features or capabilities.

## Quick Start

\`\`\`bash
# Clone
git clone <repo-url>
cd project-name

# Install dependencies
<package-manager> install

# Configure
cp .env.example .env
# Edit .env with your values

# Run
<package-manager> run dev
\`\`\`

## Prerequisites

- Runtime version (e.g., Node.js 20+, Python 3.13+, Go 1.22+)
- Required tools (e.g., Docker, pnpm)
- External services needed (e.g., PostgreSQL, Redis)

## Installation

Detailed installation steps if different from Quick Start.

## Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `API_KEY` | External service API key | - | Yes |
| `LOG_LEVEL` | Logging verbosity | `info` | No |

## Usage

### Basic Usage
\`\`\`bash
# Example command
<command> --option value
\`\`\`

### API Examples
\`\`\`bash
# Create resource
curl -X POST http://localhost:3000/api/resource \
  -H "Content-Type: application/json" \
  -d '{"name": "example"}'
\`\`\`

## Development

### Project Structure
\`\`\`
src/
├── api/         # API routes
├── services/    # Business logic
├── models/      # Data models
└── utils/       # Helpers
\`\`\`

### Running Tests
\`\`\`bash
<package-manager> test           # Unit tests
<package-manager> test:e2e       # E2E tests
<package-manager> test:coverage  # With coverage
\`\`\`

### Code Quality
\`\`\`bash
<package-manager> lint    # Run linter
<package-manager> format  # Format code
<package-manager> check   # Type check
\`\`\`

## Deployment

Brief deployment instructions or link to deployment docs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) or appropriate license.
```

## API Documentation (OpenAPI/Swagger)

### OpenAPI 3.1 Structure
```yaml
# api/openapi.yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0
  description: |
    API description with markdown support.

    ## Authentication
    All endpoints require Bearer token authentication.

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://api.staging.example.com/v1
    description: Staging

tags:
  - name: Users
    description: User management operations
  - name: Orders
    description: Order processing

paths:
  /users:
    get:
      tags: [Users]
      summary: List all users
      operationId: listUsers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags: [Users]
      summary: Create a new user
      operationId: createUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          $ref: '#/components/responses/Conflict'

components:
  schemas:
    User:
      type: object
      required: [id, email, name, createdAt]
      properties:
        id:
          type: string
          format: uuid
          example: "123e4567-e89b-12d3-a456-426614174000"
        email:
          type: string
          format: email
          example: "user@example.com"
        name:
          type: string
          example: "John Doe"
        createdAt:
          type: string
          format: date-time

    CreateUserRequest:
      type: object
      required: [email, name]
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100

    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object

    Pagination:
      type: object
      properties:
        total:
          type: integer
        limit:
          type: integer
        offset:
          type: integer

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Conflict:
      description: Resource conflict
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

### Best Practices
- Use meaningful `operationId` for code generation
- Include examples in schemas
- Document all error responses
- Use `$ref` for reusable components
- Version the API in URL path (`/v1/`)

## Architecture Decision Records (ADRs)

### Location
```
docs/
└── adr/
    ├── 0001-record-architecture-decisions.md
    ├── 0002-use-postgresql-for-primary-database.md
    ├── 0003-adopt-event-driven-architecture.md
    └── template.md
```

### ADR Template
```markdown
# ADR-NNNN: Title

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Date

YYYY-MM-DD

## Context

What is the issue that we're seeing that is motivating this decision or change?
Describe the forces at play (technical, business, social).
Include relevant constraints and requirements.

## Decision

What is the change that we're proposing and/or doing?
State the decision clearly and concisely.

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1
- Drawback 2

### Neutral
- Trade-off or observation

## Alternatives Considered

### Alternative 1: [Name]
Description of the alternative.

**Pros:**
- Pro 1

**Cons:**
- Con 1

**Why not chosen:** Reason

### Alternative 2: [Name]
...

## References

- Link to relevant documentation
- Link to discussion thread
- Related ADRs
```

### ADR Example
```markdown
# ADR-0002: Use PostgreSQL for Primary Database

## Status

Accepted

## Date

2024-01-15

## Context

We need a primary database for storing user data, transactions, and application state.
The system requires:
- ACID compliance for financial transactions
- Complex querying capabilities (joins, aggregations)
- JSON support for flexible schema fields
- Proven scalability to millions of records
- Strong ecosystem and tooling

## Decision

We will use PostgreSQL 16+ as our primary database.

## Consequences

### Positive
- Mature, battle-tested database with excellent reliability
- Rich feature set (JSON, full-text search, CTEs, window functions)
- Strong community and extensive documentation
- Easy to hire developers with PostgreSQL experience
- Excellent ORMs and drivers across languages

### Negative
- Horizontal scaling requires additional tools (Citus, read replicas)
- More operational overhead than managed NoSQL alternatives
- Schema migrations require careful planning

### Neutral
- Team has moderate PostgreSQL experience; some training needed

## Alternatives Considered

### Alternative 1: MySQL
Solid relational database but PostgreSQL has better JSON support,
advanced features, and better standards compliance.

**Why not chosen:** PostgreSQL's features better match our complex querying needs.

### Alternative 2: MongoDB
Would provide schema flexibility but:
- ACID transactions added recently, less battle-tested
- Joins require application-level handling
- Less suitable for relational data patterns

**Why not chosen:** Our data is highly relational; document model doesn't fit.

## References

- [PostgreSQL vs MySQL comparison](https://example.com)
- [Our data model analysis](./data-model.md)
```

## Inline Code Documentation

### When to Add Comments
- **Complex algorithms** - Explain the "why," not the "what"
- **Non-obvious business rules** - Document the domain logic
- **Workarounds** - Explain temporary fixes and link to issues
- **Public APIs** - Document parameters, returns, exceptions

### When NOT to Add Comments
- Self-explanatory code
- Obvious operations
- Restating what the code does

### Examples

```python
# Bad: States the obvious
# Increment counter by 1
counter += 1

# Good: Explains business rule
# Users get 3 free attempts per day; reset at midnight UTC
if attempt_count >= MAX_FREE_ATTEMPTS:
    raise RateLimitExceeded()

# Good: Explains non-obvious optimization
# Using batch insert for performance: individual inserts
# were causing 10x latency at scale (see ADR-0015)
await repository.batch_insert(records, batch_size=1000)

# Good: Documents workaround
# HACK: API returns inconsistent date formats
# TODO: Remove when upstream fixes issue #12345
date = parse_date_flexible(response["date"])
```

### TODO/FIXME Convention
```python
# TODO: Brief description of what needs to be done
# TODO(username): Assigned task with owner
# FIXME: Something is broken and needs fixing
# HACK: Temporary workaround (include issue link)
# NOTE: Important information for future readers
```

## Changelog

### Keep a Changelog Format
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description

## [1.2.0] - 2024-01-15

### Added
- User profile avatars (#123)
- Export to CSV functionality (#125)

### Changed
- Improved search performance by 40%

### Deprecated
- Legacy `/api/v1/users` endpoint (use `/api/v2/users`)

### Fixed
- Cart total calculation with discounts (#127)

## [1.1.0] - 2024-01-01

...

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/releases/tag/v1.1.0
```

### Categories
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

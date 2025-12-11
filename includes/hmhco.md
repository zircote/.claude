# HMHCO Organization Standards

Organization-specific rules and configurations for HMHCO projects.

## Systems Environments

The ONLY environments that exist (no others unless explicitly stated):
- **prod** - Production
- **cert** - Certification/UAT
- **int** - Integration
- **dev** - Development

Never assume or reference other environment names (staging, qa, uat, preprod, etc.).

## Prohibited Services

**Slack is NOT used at HMHCO.** Never include Slack in:
- Code implementations or examples
- GitHub Actions workflows (no slack-notify, slack-webhook actions)
- Notification pathways or alerting configurations
- Documentation examples
- CI/CD pipelines

## Standard Communication Platform

**Microsoft Teams is the standard communication platform.** Use Teams for:
- CI/CD notifications and alerts
- Workflow status updates
- Team communications and integrations

### Teams Notification Example (GitHub Actions)
```yaml
# Discover current action version first via version-discovery protocol
- uses: jdcargile/ms-teams-notification@vX
  with:
    github-token: ${{ github.token }}
    ms-teams-webhook-uri: ${{ secrets.TEAMS_WEBHOOK_URI }}
    notification-summary: "Build ${{ job.status }}"
```

## Other Approved Notification Methods
- PagerDuty (for alerting/incidents)
- Email notifications
- GitHub native (Issues, PR comments, Checks)

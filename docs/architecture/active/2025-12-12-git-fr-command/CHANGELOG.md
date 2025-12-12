# Changelog

## [1.0.0] - 2025-12-12

### Added
- Complete requirements specification (REQUIREMENTS.md)
- Technical architecture design (ARCHITECTURE.md)
- Implementation plan with 4 phases, 9 tasks (IMPLEMENTATION_PLAN.md)
- Architecture decision records for 6 key decisions (DECISIONS.md)

### Research Conducted
- Analyzed existing `/git:cm`, `/git:cp`, `/git:pr` commands for patterns
- Confirmed frontmatter schema and numbered workflow step format
- Validated command naming conventions

### Decisions Made
- ADR-001: Rebase over merge for sync operations
- ADR-002: Ask user for dirty working directory handling
- ADR-003: Dry-run default for branch deletion
- ADR-004: Session persistence via conversation context
- ADR-005: Smart default branch detection with fallback prompts
- ADR-006: Provide conflict resolution guidance over auto-abort

### Scope
- `/git:fr` - Fetch and rebase
- `/git:sync` - Fetch, rebase, and push
- `/git:ff` - Fast-forward merge only
- `/git:prune` - Clean stale local branches

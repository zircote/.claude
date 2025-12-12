---
document_type: requirements
project_id: ARCH-2025-12-12-001
version: 1.0.0
last_updated: 2025-12-12T00:00:00Z
status: draft
---

# Git Workflow Commands Suite - Product Requirements Document

## Executive Summary

This project expands the existing `/git` command suite with four new commands focused on synchronization and maintenance: `/git:fr` (fetch-rebase), `/git:sync` (full sync loop), `/git:ff` (fast-forward merge), and `/git:prune` (stale branch cleanup). These commands follow established patterns from `/git:cm`, `/git:cp`, and `/git:pr` while introducing smart defaults with fallback prompts and safety-first conflict handling.

## Problem Statement

### The Problem

Developers frequently need to synchronize their local branches with remote repositories. The current `/git` command suite handles committing and pushing but lacks commands for the "pull" side of the workflow—specifically fetching, rebasing, and cleaning up stale branches.

### Impact

- **Manual repetition**: Developers type `git fetch && git rebase origin/main` repeatedly
- **Inconsistent practices**: Different team members use different sync strategies (merge vs rebase)
- **Stale branches accumulate**: Local branches pile up after remote branches are deleted
- **Conflict anxiety**: Developers avoid rebasing due to uncertainty about conflict resolution

### Current State

Users must manually execute git commands or rely on IDE integrations. No standardized Claude Code slash commands exist for sync operations.

## Goals and Success Criteria

### Primary Goal

Provide a complete, consistent set of git workflow commands that handle both "push" (existing) and "pull" (new) operations with smart defaults and safety guards.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Command adoption | Used in >50% of sync operations | User feedback |
| Conflict resolution success | Users complete rebases without aborting | Observation |
| Branch hygiene | Local stale branches reduced | Git branch count |

### Non-Goals (Explicit Exclusions)

- Interactive rebase editing (`git rebase -i`)
- Cherry-picking specific commits
- Branch creation or switching
- Remote management (adding/removing remotes)
- Git configuration changes

## User Analysis

### Primary Users

- **Who**: Developers using Claude Code for git workflows
- **Needs**: Quick, safe synchronization with remote branches
- **Context**: During active development, before PRs, after remote changes

### User Stories

1. As a developer, I want to sync my feature branch with main so that I have the latest changes before continuing work
2. As a developer, I want to be warned about uncommitted changes before rebasing so that I don't lose work
3. As a developer, I want guidance when conflicts occur so that I can resolve them confidently
4. As a developer, I want to clean up branches that no longer exist on remote so that my local repo stays tidy
5. As a developer, I want fast-forward merges when possible so that I maintain a clean history

## Functional Requirements

### Must Have (P0)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-001 | `/git:fr` fetches from remote and rebases current branch | Core sync functionality | Successfully rebases onto specified remote/branch |
| FR-002 | Default remote is `origin` | Consistency with git conventions | Works without arguments |
| FR-003 | Default branch is upstream tracking branch | Smart defaults | Detects and uses tracking branch |
| FR-004 | Prompt user when working directory is dirty | Prevent data loss | Shows warning with options |
| FR-005 | Provide conflict resolution guidance | User confidence | Shows helpful instructions on conflict |
| FR-006 | `/git:ff` performs fast-forward-only merge | Safe merge option | Fails gracefully if FF not possible |
| FR-007 | `/git:prune` shows dry-run by default | Safety first | Lists branches without deleting |
| FR-008 | `/git:prune --force` executes deletion | Explicit action required | Deletes listed branches |
| FR-009 | Smart detection with fallback prompts | Graceful degradation | Asks user if tracking branch missing |
| FR-010 | Session-persistent remote override | Convenience | Remembers user-specified remote in conversation |

### Should Have (P1)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-101 | `/git:sync` combines fetch + rebase + push | Full sync workflow | Completes all three operations |
| FR-102 | Verify tracking branch exists before operations | Prevent errors | Clear message if no tracking branch |
| FR-103 | Show commit summary before rebase | Transparency | Lists commits that will be rebased |
| FR-104 | Confirm push in `/git:sync` | Safety for shared branches | Prompts before pushing |

### Nice to Have (P2)

| ID | Requirement | Rationale | Acceptance Criteria |
|----|-------------|-----------|---------------------|
| FR-201 | Preview mode for `/git:fr` | Extra safety | Shows what would happen without doing it |
| FR-202 | Support `--abort` flag for in-progress rebases | Recovery option | Cleanly aborts and restores state |

## Non-Functional Requirements

### Consistency

- All commands follow the YAML frontmatter pattern from existing `/git` commands
- Numbered workflow steps with clear imperatives
- Safety warnings match style of `/git:cm` and `/git:cp`

### Safety

- Never auto-delete without explicit `--force`
- Always warn about uncommitted changes
- Provide clear abort/recovery instructions

### User Experience

- Commands work with sensible defaults (zero arguments needed for common case)
- Clear, actionable error messages
- Guidance rather than cryptic git errors

## Technical Constraints

- Must be implemented as markdown files in `commands/git/` directory
- Must follow existing frontmatter schema (`description`, optional `argument-hint`)
- Claude Code interprets these as prompts, not scripts
- Session persistence relies on conversation context (stateless commands)

## Dependencies

### Internal Dependencies

- Existing `/git` command patterns in `commands/git/`
- Git CLI available in user environment

### External Dependencies

- None (pure git operations)

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Rebase conflicts confuse users | Medium | Medium | Provide step-by-step conflict resolution guidance |
| Users accidentally delete branches with prune | Low | High | Dry-run default, require `--force` |
| No tracking branch configured | Medium | Low | Smart detection with fallback prompts |
| Dirty working directory causes data loss | Medium | High | Always prompt user before proceeding |

## Open Questions

- [x] Session persistence mechanism → Conversation context (resolved)
- [ ] Should `/git:sync` have a `--no-push` flag for fetch+rebase only?

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| Fetch | Download objects and refs from remote repository |
| Rebase | Reapply commits on top of another base tip |
| Fast-forward | Move branch pointer forward when no divergence exists |
| Tracking branch | Local branch configured to track a remote branch |
| Stale branch | Local branch whose remote counterpart has been deleted |

### Command Summary

| Command | Purpose | Arguments | Default Behavior |
|---------|---------|-----------|------------------|
| `/git:fr` | Fetch and rebase | `[remote] [branch]` | `origin`, tracking branch |
| `/git:sync` | Full sync (fetch+rebase+push) | `[remote] [branch]` | `origin`, tracking branch |
| `/git:ff` | Fast-forward merge only | `[remote] [branch]` | `origin`, tracking branch |
| `/git:prune` | Clean stale local branches | `[--force]` | Dry-run, list only |

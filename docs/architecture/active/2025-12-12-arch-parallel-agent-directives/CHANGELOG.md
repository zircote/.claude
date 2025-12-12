# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-12

### Added
- Complete requirements specification (REQUIREMENTS.md)
  - 8 Must Have (P0) requirements including 2 bug fixes
  - 4 Should Have (P1) requirements
  - 2 Nice to Have (P2) requirements
- Technical architecture design (ARCHITECTURE.md)
  - 6 components: worktree fix, sync fix, directive block, enhanced templates, agent tracking, named research agents
  - Data flow diagrams for planning process
  - Integration points with agent catalog and Task tool
- Implementation plan (IMPLEMENTATION_PLAN.md)
  - 4 phases, 10 tasks total
  - Agent assignments for each task (meta: using the format we're designing)
  - Parallel execution groups defined
  - Estimated effort: 4-6 hours
- Research notes (RESEARCH_NOTES.md)
  - Agent catalog analysis: 121 agents across 10 categories
  - Task tool usage patterns documented
  - Bug root cause analysis
- Architecture decision records (DECISIONS.md)
  - 5 ADRs covering key design choices

### Bug Fixes Identified
- FR-000: Worktree prompt logging initialization (create before launch)
- FR-000a: Document synchronization not updating checkboxes/status
- FR-000b: Hook configuration - multiple hook groups prevents execution of second hook

### Research Conducted
- Parallel exploration of agent catalog (121 agents, 10 categories)
- Task tool usage patterns in existing commands
- IMPLEMENTATION_PLAN template analysis from 3 completed projects

## [Unreleased]

### Changed
- ADR-006: Changed from "hook consolidation in hookify" to "standalone prompt-capture plugin"
- FR-000b: Updated acceptance criteria to reflect plugin approach instead of patching
- Component 0b: Redesigned from hookify patch to standalone plugin architecture
- IMPLEMENTATION_PLAN: Added Task 1.3 for creating standalone prompt-capture plugin

### Added
- Initial project creation
- Project workspace initialized at `docs/architecture/active/2025-12-12-arch-parallel-agent-directives/`
- Requirements elicitation completed

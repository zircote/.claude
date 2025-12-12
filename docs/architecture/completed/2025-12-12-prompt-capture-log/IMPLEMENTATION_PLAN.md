---
document_type: implementation_plan
project_id: ARCH-2025-12-12-002
version: 1.0.0
last_updated: 2025-12-12T22:15:00Z
status: completed
estimated_effort: 25 tasks across 4 phases
---

# Prompt Capture Log - Implementation Plan

## Overview

This plan breaks down the implementation into four phases: Foundation (hook infrastructure), Core (filter pipeline and logging), Integration (/arch:* commands), and Polish (testing and documentation). Each task includes clear acceptance criteria and dependencies.

## Phase Summary

| Phase | Key Deliverables |
|-------|------------------|
| Phase 1: Foundation | Hook skeleton, project structure, basic toggle |
| Phase 2: Core | Filter pipeline, log writer, entry schema |
| Phase 3: Integration | /arch:log command, /arch:c analyzer, retrospective section |
| Phase 4: Polish | Test suite, documentation, edge case handling |

---

## Phase 1: Foundation

**Goal**: Establish hook infrastructure and project structure

### Tasks

#### Task 1.1: Create hook directory structure

- **Description**: Set up the directory layout for hook files, filters, and analyzers
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `~/.claude/hooks/` directory exists
  - [ ] `~/.claude/hooks/filters/` subdirectory created
  - [ ] `~/.claude/hooks/analyzers/` subdirectory created
  - [ ] `__init__.py` files in place for Python imports

#### Task 1.2: Create prompt_capture_hook.py skeleton

- **Description**: Implement basic hook that reads stdin, returns pass-through response
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Hook reads JSON from stdin
  - [ ] Hook outputs valid JSON to stdout
  - [ ] Hook returns `{"decision": "approve"}` (pass-through)
  - [ ] Hook handles malformed input gracefully

#### Task 1.3: Register hook in hookify hooks.json

- **Description**: Add UserPromptSubmit hook registration
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Hook registered in `~/.claude/plugins/cache/claude-code-plugins/hookify/*/hooks/hooks.json`
  - [ ] Hook fires on UserPromptSubmit event
  - [ ] Hook timeout set to 5000ms

#### Task 1.4: Implement toggle check function

- **Description**: Create function to check if logging is enabled for a project
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] `is_logging_enabled(cwd)` function implemented
  - [ ] Returns True if `.prompt-log-enabled` exists in project dir
  - [ ] Returns False if file doesn't exist
  - [ ] Handles missing project directory gracefully

#### Task 1.5: Implement arch context detection

- **Description**: Detect if current session is within /arch:* command context
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] `is_arch_context(input_data)` function implemented
  - [ ] Detects /arch:p, /arch:i, /arch:s, /arch:c contexts
  - [ ] Returns False for non-arch sessions
  - [ ] Uses transcript_path or prompt content for detection

### Phase 1 Deliverables

- [ ] Hook directory structure created
- [ ] Basic hook skeleton working
- [ ] Hook registered and firing
- [ ] Toggle and context detection functions

### Phase 1 Exit Criteria

- [ ] `echo '{"user_prompt":"test"}' | python3 ~/.claude/hooks/prompt_capture_hook.py` returns valid JSON
- [ ] Hook appears in Claude Code hook logs

---

## Phase 2: Core Implementation

**Goal**: Implement filter pipeline and log writing

### Tasks

#### Task 2.1: Create profanity word list

- **Description**: Compile profanity word list for filtering
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `filters/profanity_words.txt` created
  - [ ] Contains common profanity terms (50+ words)
  - [ ] One word per line, lowercase
  - [ ] Includes common variations

#### Task 2.2: Implement profanity filter module

- **Description**: Create profanity detection and replacement
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] `filters/profanity.py` module created
  - [ ] `detect_profanity(text)` returns list of matches
  - [ ] `filter_profanity(text)` replaces with `[FILTERED]`
  - [ ] Case-insensitive matching
  - [ ] Word boundary detection (avoid false positives)

#### Task 2.3: Implement secret patterns module

- **Description**: Create regex patterns for secret detection
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `filters/secrets.py` module created
  - [ ] Patterns for: AWS keys, GitHub tokens, API keys, passwords
  - [ ] `detect_secrets(text)` returns list of (type, match)
  - [ ] `filter_secrets(text)` replaces with `[SECRET:type]`
  - [ ] Patterns pre-compiled for performance

#### Task 2.4: Implement filter pipeline

- **Description**: Chain filters together in correct order
- **Dependencies**: Task 2.2, Task 2.3
- **Acceptance Criteria**:
  - [ ] `filters/pipeline.py` module created
  - [ ] `filter_pipeline(text)` returns FilterResult
  - [ ] Secrets filtered before profanity (avoid masking secrets as profanity)
  - [ ] Returns original length, filtered text, counts

#### Task 2.5: Define log entry schema

- **Description**: Create dataclass for log entries
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] LogEntry dataclass defined
  - [ ] Fields: timestamp, session_id, type, command, content, filter_applied, metadata
  - [ ] `to_dict()` method for JSON serialization
  - [ ] `from_dict()` class method for deserialization

#### Task 2.6: Implement log writer

- **Description**: Create atomic NDJSON append function
- **Dependencies**: Task 2.5
- **Acceptance Criteria**:
  - [ ] `append_to_log(project_path, entry)` function
  - [ ] Creates PROMPT_LOG.json if not exists
  - [ ] Uses file locking for concurrent safety
  - [ ] Appends single JSON line with newline
  - [ ] Handles write errors gracefully

#### Task 2.7: Integrate filter and log in hook

- **Description**: Connect filter pipeline to hook and write logs
- **Dependencies**: Task 2.4, Task 2.6
- **Acceptance Criteria**:
  - [ ] Hook calls filter_pipeline on user_prompt
  - [ ] Hook builds LogEntry from input_data
  - [ ] Hook calls append_to_log with filtered entry
  - [ ] Hook returns success message in systemMessage

### Phase 2 Deliverables

- [ ] Profanity filter module working
- [ ] Secret detection module working
- [ ] Filter pipeline chaining filters
- [ ] Log writer with atomic append
- [ ] Hook writing filtered logs

### Phase 2 Exit Criteria

- [ ] Prompt with profanity logged with `[FILTERED]` replacement
- [ ] Prompt with API key logged with `[SECRET:type]` replacement
- [ ] PROMPT_LOG.json contains valid NDJSON entries

---

## Phase 3: Integration

**Goal**: Integrate with /arch:* commands and retrospective

### Tasks

#### Task 3.1: Create /arch:log command

- **Description**: Implement toggle command for logging control
- **Dependencies**: Phase 2 complete
- **Acceptance Criteria**:
  - [ ] `~/.claude/commands/arch/log.md` created
  - [ ] `/arch:log on` creates `.prompt-log-enabled` in project dir
  - [ ] `/arch:log off` removes `.prompt-log-enabled`
  - [ ] `/arch:log status` shows current state
  - [ ] `/arch:log show` displays recent log entries

#### Task 3.2: Implement expanded prompt capture

- **Description**: Capture the full slash command expansion alongside user input
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Detect when a slash command is being executed
  - [ ] Log expanded prompt content with type "expanded_prompt"
  - [ ] Link to user input via session_id
  - [ ] Handle large expanded prompts (truncate if >50KB)

#### Task 3.3: Implement response summary capture

- **Description**: Generate and log summaries of Claude responses
- **Dependencies**: Task 2.6
- **Acceptance Criteria**:
  - [ ] Hook captures response on subsequent prompt (via transcript)
  - [ ] `summarize_response(text)` extracts key points
  - [ ] Summary limited to 500 characters
  - [ ] Logged with type "response_summary"

#### Task 3.4: Implement log analyzer

- **Description**: Create analysis module for retrospective generation
- **Dependencies**: Task 2.6
- **Acceptance Criteria**:
  - [ ] `analyzers/log_analyzer.py` module created
  - [ ] `analyze_log(log_path)` returns LogAnalysis
  - [ ] Calculates: total prompts, session count, avg length, clarification count
  - [ ] Identifies sessions with high clarification (>10 questions)

#### Task 3.5: Implement retrospective section generator

- **Description**: Generate markdown for RETROSPECTIVE.md
- **Dependencies**: Task 3.4
- **Acceptance Criteria**:
  - [ ] `generate_interaction_analysis(analysis)` returns markdown
  - [ ] Includes metrics table
  - [ ] Includes insights (high clarification warning, etc.)
  - [ ] Includes recommendations for improvement

#### Task 3.6: Integrate analyzer with /arch:c

- **Description**: Modify /arch:c to call analyzer and update retrospective
- **Dependencies**: Task 3.5
- **Acceptance Criteria**:
  - [ ] /arch:c checks for PROMPT_LOG.json
  - [ ] If exists, runs analyzer
  - [ ] Appends "## Interaction Analysis" to RETROSPECTIVE.md
  - [ ] Disables logging (removes .prompt-log-enabled)
  - [ ] Moves PROMPT_LOG.json to completed/

#### Task 3.7: Handle log file lifecycle

- **Description**: Ensure log files move with project through lifecycle
- **Dependencies**: Task 3.6
- **Acceptance Criteria**:
  - [ ] PROMPT_LOG.json included in /arch:c archive
  - [ ] .prompt-log-enabled removed at close-out
  - [ ] Log preserved in completed/ directory

### Phase 3 Deliverables

- [ ] /arch:log command functional
- [ ] Expanded prompts captured
- [ ] Response summaries captured
- [ ] Log analyzer generating insights
- [ ] /arch:c integration complete

### Phase 3 Exit Criteria

- [ ] Full /arch:p session logged with all entry types
- [ ] /arch:c generates Interaction Analysis section
- [ ] PROMPT_LOG.json in completed/ directory

---

## Phase 4: Polish

**Goal**: Testing, documentation, and edge case handling

### Tasks

#### Task 4.1: Create filter test suite

- **Description**: Unit tests for profanity and secret filters
- **Dependencies**: Phase 2 complete
- **Acceptance Criteria**:
  - [ ] Test file `tests/test_filters.py`
  - [ ] Tests for each secret pattern (true positives)
  - [ ] Tests for false positive avoidance
  - [ ] Tests for profanity detection
  - [ ] >80% coverage on filter modules

#### Task 4.2: Create hook integration tests

- **Description**: End-to-end tests for hook functionality
- **Dependencies**: Phase 3 complete
- **Acceptance Criteria**:
  - [ ] Test file `tests/test_hook.py`
  - [ ] Tests hook input/output format
  - [ ] Tests toggle behavior
  - [ ] Tests log file creation
  - [ ] Tests filter application

#### Task 4.3: Create analyzer tests

- **Description**: Unit tests for log analysis
- **Dependencies**: Task 3.4
- **Acceptance Criteria**:
  - [ ] Test file `tests/test_analyzer.py`
  - [ ] Tests metric calculations
  - [ ] Tests with sample log files
  - [ ] Tests edge cases (empty log, single entry)

#### Task 4.4: Handle edge cases

- **Description**: Implement graceful handling for error scenarios
- **Dependencies**: Phase 3 complete
- **Acceptance Criteria**:
  - [ ] Handles missing project directory
  - [ ] Handles corrupted log file (skip bad lines)
  - [ ] Handles very long prompts (truncate)
  - [ ] Handles hook timeout (fail-open)
  - [ ] Handles concurrent writes

#### Task 4.5: Update CLAUDE.md with logging guidance

- **Description**: Document logging feature in project instructions
- **Dependencies**: Phase 3 complete
- **Acceptance Criteria**:
  - [ ] Add section on prompt logging to CLAUDE.md
  - [ ] Document /arch:log commands
  - [ ] Explain what is captured and filtered
  - [ ] Note privacy considerations

#### Task 4.6: Final review and cleanup

- **Description**: Code review, cleanup, final testing
- **Dependencies**: All previous tasks
- **Acceptance Criteria**:
  - [ ] All code follows existing style conventions
  - [ ] No TODO comments left in code
  - [ ] All tests passing
  - [ ] Documentation complete
  - [ ] Ready for merge to main

### Phase 4 Deliverables

- [ ] Test suite with >80% coverage
- [ ] Edge cases handled gracefully
- [ ] Documentation updated
- [ ] Code reviewed and clean

### Phase 4 Exit Criteria

- [ ] All tests passing
- [ ] Manual end-to-end test successful
- [ ] Documentation reviewed

---

## Dependency Graph

```
Phase 1:
  Task 1.1 ──┬──► Task 1.2 ──┬──► Task 1.3
             │               │
             │               └──► Task 1.4
             │               │
             │               └──► Task 1.5
             │
             └───────────────────► Phase 2

Phase 2:
  Task 2.1 ──► Task 2.2 ──┐
                          │
  Task 2.3 ──────────────┼──► Task 2.4 ──► Task 2.7
                          │                    │
  Task 2.5 ──► Task 2.6 ──┘                    │
                                               │
                                               └──► Phase 3

Phase 3:
  Task 3.1 ──────────────────────────────────────┐
                                                  │
  Task 3.2 ──────────────────────────────────────┼──► Phase 4
                                                  │
  Task 3.3 ──────────────────────────────────────┤
                                                  │
  Task 3.4 ──► Task 3.5 ──► Task 3.6 ──► Task 3.7┘

Phase 4:
  Task 4.1 ──┐
             │
  Task 4.2 ──┼──► Task 4.4 ──► Task 4.6
             │          │
  Task 4.3 ──┘          ▼
                   Task 4.5
```

## Risk Mitigation Tasks

| Risk | Mitigation Task | Phase |
|------|-----------------|-------|
| Hook latency affects UX | Performance testing in Task 4.2 | 4 |
| False positive secret detection | Comprehensive test suite in Task 4.1 | 4 |
| Hook breaks on Claude Code update | Version check in Task 4.4 | 4 |
| Sensitive data leaks | Multiple filter passes in Task 2.4 | 2 |

## Testing Checklist

- [ ] Unit tests for filter modules (Task 4.1)
- [ ] Integration tests for hook (Task 4.2)
- [ ] Unit tests for analyzer (Task 4.3)
- [ ] Manual end-to-end test (Task 4.6)
- [ ] Performance validation (<100ms latency)

## Documentation Tasks

- [ ] Update CLAUDE.md (Task 4.5)
- [ ] Inline code documentation (throughout)
- [ ] README for hooks directory (Task 4.6)

## Launch Checklist

- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Manual testing successful
- [ ] Merged to main branch
- [ ] Feature announced/documented

## Post-Launch

- [ ] Monitor for hook errors (first week)
- [ ] Gather feedback on filter accuracy
- [ ] Collect sample retrospective analyses
- [ ] Consider enhancements based on usage

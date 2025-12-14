# Claude Code Configuration

Personal Claude Code configuration repository containing agents, skills, commands, and coding standards for AI-assisted development workflows.

## Overview

This repository provides a comprehensive configuration for [Claude Code](https://claude.ai/claude-code), Anthropic's CLI for Claude. It includes:

- **100+ specialized agents** organized by domain
- **60+ reusable skills** for common development tasks
- **Custom slash commands** for streamlined workflows
- **Coding standards** for multiple languages and frameworks

## Repository Structure

```
.claude/
├── CLAUDE.md              # Global instructions & behavior rules
├── agents/                # Specialized AI agents by category
│   ├── 01-core-development/
│   ├── 02-language-specialists/
│   ├── 03-infrastructure/
│   ├── 04-quality-security/
│   ├── 05-data-ai/
│   ├── 06-developer-experience/
│   ├── 07-specialized-domains/
│   ├── 08-business-product/
│   ├── 09-meta-orchestration/
│   └── 10-research-analysis/
├── skills/                # Reusable skill definitions
├── commands/              # Custom slash commands
│   └── git/               # Git workflow commands
├── includes/              # Language & framework standards
└── docs/                  # Additional documentation
```

## Agents

Agents are specialized AI assistants with domain expertise. Each agent has:
- Defined tools and capabilities
- Model preferences
- Contextual expertise

### Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **Core Development** | Full-stack & platform development | `backend-developer`, `frontend-developer`, `fullstack-developer` |
| **Language Specialists** | Language-specific expertise | `python-pro`, `typescript-pro`, `golang-pro`, `rust-engineer` |
| **Infrastructure** | DevOps, cloud, & platform | `kubernetes-specialist`, `terraform-engineer`, `cloud-architect` |
| **Quality & Security** | Testing, security, code review | `security-engineer`, `qa-expert`, `penetration-tester` |
| **Data & AI** | ML, data engineering, analytics | `ml-engineer`, `data-scientist`, `llm-architect` |
| **Developer Experience** | Tooling & workflows | `cli-developer`, `build-engineer`, `documentation-engineer` |
| **Specialized Domains** | Industry-specific | `fintech-engineer`, `blockchain-developer`, `game-developer` |
| **Business & Product** | Non-technical roles | `product-manager`, `technical-writer`, `ux-researcher` |
| **Meta & Orchestration** | Multi-agent coordination | `workflow-orchestrator`, `task-distributor` |
| **Research & Analysis** | Information gathering | `research-analyst`, `competitive-analyst`, `market-researcher` |

## Skills

Skills are reusable capabilities that can be invoked during conversations. Notable skills include:

- **Document Processing**: `pdf`, `docx`, `xlsx`, `pptx`
- **Media**: `ai-multimodal`, `media-processing`, `image-enhancer`
- **Development**: `frontend-development`, `backend-development`, `databases`
- **DevOps**: `devops`, `chrome-devtools`, `webapp-testing`
- **AI/ML**: `anthropic-prompt-engineer`, `openai-prompt-engineer`
- **Utilities**: `changelog-generator`, `file-organizer`, `docs-seeker`

## Commands

Custom slash commands for common workflows:

| Command | Description |
|---------|-------------|
| `/git:cm` | Stage all files and create a commit |
| `/git:cp` | Stage, commit, and push all changes |
| `/git:pr` | Create a pull request |
| `/cs:p` | Strategic project planner with Socratic requirements elicitation |
| `/cs:s` | Project status and portfolio manager |
| `/cs:c` | Project close-out and archival |
| `/cr` | Comprehensive code review with parallel specialist agents |
| `/cr-fx` | Interactive remediation of code review findings |
| `/explore` | Exhaustive codebase exploration (Opus 4.5) |
| `/deep-research` | Multi-phase research protocol (Opus 4.5) |

## Includes

Environment-specific coding standards automatically loaded based on context:

| Environment | File | Purpose |
|-------------|------|---------|
| Python | `includes/python.md` | Python best practices & style |
| Go | `includes/golang.md` | Go idioms & patterns |
| React/TypeScript | `includes/react.md` | React & TS conventions |
| Git | `includes/git.md` | Version control workflows |
| Testing | `includes/testing.md` | Testing strategies |
| Documentation | `includes/documentation.md` | Doc standards |
| MCP | `includes/mcp-reference.md` | Model Context Protocol |
| Opus 4.5 | `includes/opus-4-5.md` | Opus 4.5 optimizations |

## Configuration

### Global Instructions (CLAUDE.md)

The `CLAUDE.md` file contains:
- Planning confidence requirements
- MCP query pagination patterns
- Memory agent usage guidelines
- API response validation rules
- Environment definitions

### Ignored Files

The following are intentionally not tracked (see `.gitignore`):
- Session data (`history.jsonl`, `todos/`, `plans/`)
- Local settings (`settings.local.json`, `.env`)
- IDE configurations
- Plugins (reinstallable from marketplace)
- Project-specific data

## Usage

1. Clone to your home directory as `~/.claude/`
2. Claude Code automatically loads `CLAUDE.md` for global instructions
3. Agents and skills are available via the Task tool
4. Slash commands work with `/command:name` syntax

## Requirements

- [Claude Code CLI](https://claude.ai/claude-code)
- Anthropic API access
- Optional: MCP servers for extended capabilities

## License

Personal configuration - adapt for your own use.

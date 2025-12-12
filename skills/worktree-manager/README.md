# Worktree Manager

![Worktree Manager](cover.png)

A Claude Code skill for managing parallel development environments using git worktrees.

## Installation

Clone this repo into your Claude skills directory:

```bash
# Global installation (available in all projects)
git clone git@github.com:Wirasm/worktree-manager-skill.git ~/.claude/skills/worktree-manager

# Or project-specific (available only in that project)
git clone git@github.com:Wirasm/worktree-manager-skill.git .claude/skills/worktree-manager
```

Restart Claude Code after installation.

## Configuration

Edit `~/.claude/skills/worktree-manager/config.json` to customize:

```json
{
  "terminal": "ghostty",
  "shell": "bash",
  "claudeCommand": "claude --dangerously-skip-permissions",
  "portPool": { "start": 8100, "end": 8199 },
  "portsPerWorktree": 2,
  "worktreeBase": "~/tmp/worktrees"
}
```

| Setting            | Default                                 | Description                                                                               |
| ------------------ | --------------------------------------- | ----------------------------------------------------------------------------------------- |
| `terminal`         | `ghostty`                               | Terminal to open agents in (`ghostty`, `iterm2`, `tmux`, `wezterm`, `kitty`, `alacritty`) |
| `shell`            | `bash`                                  | Shell to use (`bash`, `zsh`, `fish`)                                                      |
| `claudeCommand`    | `claude --dangerously-skip-permissions` | Command to launch Claude Code                                                             |
| `portPool`         | `8100-8199`                             | Port range for dev servers                                                                |
| `portsPerWorktree` | `2`                                     | Ports allocated per worktree (e.g., API + frontend)                                       |
| `worktreeBase`     | `~/tmp/worktrees`                       | Where worktrees are created                                                               |

## What This Does

**The problem:** You're working on a feature when an urgent bug comes in. You have uncommitted changes, half-finished work, a dev server running. Switching branches means stashing everything, stopping servers, and losing your flow. When you come back, you have to reconstruct your entire environment.

**The solution:** Git worktrees let you have multiple branches checked out simultaneously in separate directories. Each is a complete, independent working copy. But setting them up manually is tedious—you need to create the worktree, copy environment files, install dependencies, configure ports so nothing conflicts, and remember to clean everything up later.

**This skill automates all of that.** Just say:

> "Spin up worktrees for feature/auth and fix/payment-bug"

Claude will:

1. Create isolated worktree directories for each branch
2. Copy necessary files (`.env`, `.agents/`, etc.)
3. Install dependencies automatically
4. Allocate unique ports so dev servers don't conflict
5. Open new terminal windows with Claude Code agents ready to work

All worktrees are tracked in a global registry, so you can check status across all your projects and clean up when branches are merged.

**Why it's valuable:**

- **Parallel development** — Work on multiple features simultaneously with dedicated Claude agents
- **Zero context switching** — Each worktree maintains its own state, dependencies, and running servers
- **No port conflicts** — Global port allocation ensures dev servers across projects never collide
- **Easy cleanup** — One command removes worktrees, kills servers, and releases ports when you're done

## Usage

The skill activates automatically when you mention worktrees:

- "Create a worktree for feature/dark-mode"
- "Spin up 3 worktrees for these tickets"
- "What's the status of my worktrees?"
- "Clean up the auth worktree"

## Initial Prompts

Launch Claude Code agents with a prompt that's ready to go when the instance starts. Choose between interactive mode (default) or headless mode.

### Prompt Modes

| Mode | Syntax | Behavior |
|------|--------|----------|
| **Interactive** (default) | `with prompt "..."` | Prompt is pre-filled, you can edit and press Enter |
| **Headless** | `with prompt "..." --headless` | Auto-executes immediately, runs and exits |

### Basic Syntax

Add `with prompt "your prompt here"` to any worktree creation command:

```
spin up worktrees for feature/auth, feature/payments with prompt "run all tests"
```

For headless (auto-execute) mode, add `--headless`:
```
spin up worktrees for auth, payments with prompt "/review-code" --headless
```

### Template Variables

Use variables to customize prompts per worktree:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{service}}` | Branch slug (short name) | `feature-auth` |
| `{{branch}}` | Full branch name | `feature/auth` |
| `{{branch_slug}}` | Same as `{{service}}` | `feature-auth` |
| `{{project}}` | Project name | `my-api` |
| `{{worktree_path}}` | Full path to worktree | `/Users/.../worktrees/my-api/feature-auth` |
| `{{port}}` | First allocated port | `8100` |
| `{{ports}}` | All allocated ports | `8100,8101` |

### Examples

**Run tests on multiple services:**
```
spin up worktrees for auth, payments, users with prompt "run the test suite for {{service}} and fix any failures"
```

**Code review:**
```
create worktree for feature/new-api with prompt "/review-code"
```

**Custom task per service:**
```
spin up worktrees for api, frontend with prompt "analyze {{service}} performance and suggest optimizations"
```

**Using slash commands:**
```
new worktree for fix/login-bug with prompt "/deep-research the login authentication flow"
```

**Natural language prompts:**
```
spin up worktrees for auth, billing with prompt "refactor {{service}} to use the new error handling pattern"
```

### How It Works

1. You provide a prompt template with optional `{{variable}}` placeholders
2. For each worktree, variables are replaced with that worktree's values
3. Claude Code launches with your prompt:
   - **Interactive** (default): Prompt is passed as argument, pre-fills the input field
   - **Headless** (`--headless`): Uses `-p` flag, auto-executes immediately

### Tips

- **Any valid prompt works**: Natural language, slash commands, multi-line instructions
- **Combine with tasks**: The task description (shown in terminal) provides context; the prompt auto-executes
- **Escape quotes carefully**: Use single quotes inside double-quoted prompts or vice versa
- **Long prompts**: For complex instructions, consider creating a slash command and referencing it

### Script Usage

You can also use the launch script directly:

```bash
# No prompt
./launch-agent.sh ~/Projects/worktrees/my-project/feature-auth "Implement OAuth"

# Interactive prompt (pre-fills input, default)
./launch-agent.sh ~/Projects/worktrees/my-project/feature-auth "" --prompt "/explore"

# Headless prompt (auto-executes and exits)
./launch-agent.sh ~/Projects/worktrees/my-project/feature-auth "" --prompt "/review-code" --headless

# With task and interactive prompt
./launch-agent.sh ~/Projects/worktrees/my-project/feature-auth "Optimize auth" --prompt "analyze {{service}}"
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Prompt not pre-filling | Ensure `claudeCommand` in config.json doesn't already include `-p` |
| Variables not substituting | Check spelling: `{{service}}` not `{service}` or `{{ service }}` |
| Quotes breaking command | Escape inner quotes or use alternate quote style |
| Claude exits immediately | Expected with `--headless`; use interactive mode (default) to stay open |

## Requirements

- `jq` — Install with `brew install jq` (macOS) or `apt install jq` (Linux)
- `git` — For worktree operations
- A supported terminal application

## License

MIT

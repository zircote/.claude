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

## Requirements

- `jq` — Install with `brew install jq` (macOS) or `apt install jq` (Linux)
- `git` — For worktree operations
- A supported terminal application

## License

MIT

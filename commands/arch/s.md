---
argument-hint: [project-id|--list|--expired|--cleanup]
description: View architecture project status, list portfolio, find expired plans, or cleanup. Part of the /arch suite - use /arch/p to plan, /arch/c to complete.
model: claude-sonnet-4-5-20250929
allowed-tools: Read, Bash, Glob, Grep
---

# /arch/s - Project Status & Portfolio Manager

<role>
You are a Project Portfolio Manager. Your job is to provide visibility into architecture projects and help maintain project hygiene.
</role>

<command_argument>
$ARGUMENTS
</command_argument>

<operations>

## Operation: List All Projects (--list or no argument)

```bash
echo "=== ACTIVE PROJECTS ==="
for dir in docs/architecture/active/*/; do
  if [ -d "$dir" ]; then
    echo "📂 $dir"
    grep -E "^(project_id|project_name|status|created|expires):" "$dir/README.md" 2>/dev/null | head -5
    echo ""
  fi
done

echo "=== APPROVED (Awaiting Implementation) ==="
for dir in docs/architecture/approved/*/; do
  if [ -d "$dir" ]; then
    echo "📂 $dir"
    grep -E "^(project_id|project_name|status|approved):" "$dir/README.md" 2>/dev/null | head -4
    echo ""
  fi
done

echo "=== COMPLETED ==="
ls -1 docs/architecture/completed/ 2>/dev/null | head -10
echo "[Use --list-completed for full list]"

echo "=== SUPERSEDED ==="
ls -1 docs/architecture/superseded/ 2>/dev/null | head -5
```

Format output as:

```
📊 Architecture Project Portfolio

┌─────────────────────────────────────────────────────────────────┐
│ ACTIVE PROJECTS (3)                                             │
├─────────────────────────────────────────────────────────────────┤
│ 📂 2025-12-11-user-auth                                         │
│    ID: ARCH-2025-12-11-001                                      │
│    Status: in-progress                                          │
│    Created: 2025-12-11 | Expires: 2026-03-11                   │
│                                                                 │
│ 📂 2025-12-08-api-gateway                                       │
│    ID: ARCH-2025-12-08-002                                      │
│    Status: in-review                                            │
│    Created: 2025-12-08 | Expires: 2026-03-08                   │
├─────────────────────────────────────────────────────────────────┤
│ APPROVED - AWAITING IMPLEMENTATION (1)                          │
├─────────────────────────────────────────────────────────────────┤
│ 📂 2025-11-20-payment-system                                    │
│    ID: ARCH-2025-11-20-001                                      │
│    Approved: 2025-11-25                                         │
├─────────────────────────────────────────────────────────────────┤
│ COMPLETED: 5 projects | SUPERSEDED: 2 projects                  │
└─────────────────────────────────────────────────────────────────┘
```

## Operation: View Specific Project (project-id or path)

```bash
PROJECT_PATH=$(find docs/architecture -name "*${PROJECT_SLUG}*" -type d | head -1)
cat "${PROJECT_PATH}/README.md"
```

Display:

```
📋 Project Details: ${PROJECT_NAME}

┌─────────────────────────────────────────────────────────────────┐
│ METADATA                                                        │
├─────────────────────────────────────────────────────────────────┤
│ Project ID:    ARCH-2025-12-11-001                             │
│ Name:          User Authentication System                       │
│ Status:        in-progress                                      │
│ Location:      docs/architecture/active/2025-12-11-user-auth/  │
├─────────────────────────────────────────────────────────────────┤
│ TIMELINE                                                        │
├─────────────────────────────────────────────────────────────────┤
│ Created:       2025-12-11                                       │
│ Approved:      2025-12-13                                       │
│ Started:       2025-12-14                                       │
│ Expires:       2026-03-11 (90 days remaining)                  │
├─────────────────────────────────────────────────────────────────┤
│ DOCUMENTS                                                       │
├─────────────────────────────────────────────────────────────────┤
│ ✅ README.md           (2.1 KB)                                 │
│ ✅ REQUIREMENTS.md     (8.4 KB) - 12 requirements               │
│ ✅ ARCHITECTURE.md     (6.2 KB) - 5 components                  │
│ ✅ IMPLEMENTATION_PLAN.md (4.8 KB) - 24 tasks                   │
│ ✅ RESEARCH_NOTES.md   (3.1 KB)                                 │
│ ✅ DECISIONS.md        (1.9 KB) - 3 ADRs                        │
│ ✅ CHANGELOG.md        (0.8 KB)                                 │
├─────────────────────────────────────────────────────────────────┤
│ QUICK STATS                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Requirements:  12 (P0: 5, P1: 4, P2: 3)                        │
│ Tasks:         24 across 4 phases                               │
│ Est. Effort:   120 hours                                        │
│ Risks:         4 identified                                     │
└─────────────────────────────────────────────────────────────────┘

📂 View documents:
   cat docs/architecture/active/2025-12-11-user-auth/REQUIREMENTS.md
```

## Operation: Find Expired Projects (--expired)

```bash
TODAY=$(date +%Y-%m-%d)
echo "Checking for expired projects..."

for readme in docs/architecture/active/*/README.md docs/architecture/approved/*/README.md; do
  if [ -f "$readme" ]; then
    EXPIRES=$(grep "^expires:" "$readme" | cut -d' ' -f2 | cut -dT -f1)
    if [[ "$EXPIRES" < "$TODAY" ]]; then
      echo "EXPIRED: $readme (expired: $EXPIRES)"
    fi
  fi
done
```

Display:

```
⚠️  Expired Architecture Projects

┌─────────────────────────────────────────────────────────────────┐
│ EXPIRED (2 projects)                                            │
├─────────────────────────────────────────────────────────────────┤
│ 📂 2025-08-15-legacy-migration                                  │
│    Expired: 2025-11-15 (26 days ago)                           │
│    Status: approved (never started)                             │
│    Action needed: Supersede or refresh                          │
│                                                                 │
│ 📂 2025-09-01-reporting-dashboard                               │
│    Expired: 2025-12-01 (10 days ago)                           │
│    Status: in-progress (stalled?)                               │
│    Action needed: Complete, extend, or abandon                  │
├─────────────────────────────────────────────────────────────────┤
│ EXPIRING SOON (next 14 days)                                    │
├─────────────────────────────────────────────────────────────────┤
│ 📂 2025-09-20-notification-system                               │
│    Expires: 2025-12-20 (9 days remaining)                      │
│    Status: in-review                                            │
└─────────────────────────────────────────────────────────────────┘

Recommended Actions:
• Use /arch/c to close finished projects
• Use /arch/s --cleanup to handle outdated plans
• Extend TTL via /arch/s on specific project
```

## Operation: Cleanup (--cleanup)

Performs hygiene checks and offers actions:

```
🧹 Architecture Project Cleanup

Checking for issues...

┌─────────────────────────────────────────────────────────────────┐
│ ISSUES FOUND                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ❌ Expired projects: 2                                          │
│ ⚠️  Missing documents: 1 project missing DECISIONS.md           │
│ ⚠️  Stale projects: 1 project unchanged for 30+ days           │
│ ⚠️  Orphaned folders: 1 folder without README.md               │
├─────────────────────────────────────────────────────────────────┤
│ RECOMMENDATIONS                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 1. Review expired projects:                                     │
│    - 2025-08-15-legacy-migration → supersede or delete         │
│    - 2025-09-01-reporting-dashboard → complete or abandon      │
│                                                                 │
│ 2. Add missing DECISIONS.md to:                                │
│    - 2025-12-01-cache-layer                                    │
│                                                                 │
│ 3. Check on stale project:                                     │
│    - 2025-10-15-search-indexer (last updated: 2025-11-10)     │
│                                                                 │
│ 4. Remove or initialize orphaned folder:                       │
│    - docs/architecture/active/temp-test/                       │
└─────────────────────────────────────────────────────────────────┘

Would you like me to:
A) Move expired projects to superseded/
B) Generate missing documents
C) Show details on stale projects
D) Remove orphaned folders
E) All of the above
F) Skip cleanup
```

</operations>

<helper_operations>

## Extend Project TTL

If user wants to extend a project's expiration:

```bash
# Update README.md expires field
NEW_EXPIRES=$(date -d "+90 days" +%Y-%m-%dT%H:%M:%SZ)
sed -i "s/^expires:.*/expires: ${NEW_EXPIRES}/" ${PROJECT_PATH}/README.md
```

Add CHANGELOG entry:
```markdown
### Changed
- Extended project expiration to ${NEW_EXPIRES} (reason: [user provided])
```

## Supersede Project

If user wants to mark a project as superseded:

```bash
# Update status
sed -i "s/^status:.*/status: superseded/" ${PROJECT_PATH}/README.md

# Add superseded_by reference
sed -i "s/^superseded_by:.*/superseded_by: ${NEW_PROJECT_PATH}/" ${PROJECT_PATH}/README.md

# Move to superseded folder
mv ${PROJECT_PATH} docs/architecture/superseded/
```

## Quick Stats Summary

```
📈 Portfolio Summary

Total Projects: 11
├── Active: 3
├── Approved: 1  
├── Completed: 5
└── Superseded: 2

Health Score: 82% (2 issues)
├── ⚠️ 2 expired projects need attention
└── ✅ All active projects have complete documentation

Recent Activity:
├── Last created: 2025-12-11 (user-auth)
├── Last completed: 2025-12-08 (api-gateway)
└── Last updated: 2025-12-11
```

</helper_operations>

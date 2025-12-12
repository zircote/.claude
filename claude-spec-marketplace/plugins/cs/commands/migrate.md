---
argument-hint: [--dry-run|--force|--backup]
description: Migrate from docs/architecture/ to docs/spec/ structure and update all CLAUDE.md references. Use --dry-run to preview changes.
model: claude-opus-4-5-20251101
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /cs/migrate - Architecture to Spec Migration

<role>
You are a Migration Specialist. Your job is to safely migrate existing architecture projects from the `docs/architecture/` structure to the new `docs/spec/` structure, updating all references and maintaining data integrity.
</role>

<command_argument>
$ARGUMENTS
</command_argument>

<migration_protocol>

## Pre-Flight Checks

Before any migration:

1. **Verify git status is clean**
2. **Check for docs/architecture/ existence**
3. **Verify no existing docs/spec/ conflicts**
4. **Create backup if requested**

```bash
# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo "[!] WARNING: You have uncommitted changes"
    echo "    Consider committing or stashing before migration"
    echo ""
fi

# Check source exists
if [ ! -d "docs/architecture" ]; then
    echo "[ERROR] docs/architecture/ directory not found"
    echo "        Nothing to migrate"
    exit 1
fi

# Check destination
if [ -d "docs/spec" ]; then
    echo "[!] WARNING: docs/spec/ already exists"
    echo "    Migration will merge into existing structure"
fi
```

## Step 1: Analyze Current Structure

```bash
echo "=== ARCHITECTURE STRUCTURE ANALYSIS ==="

# Count projects in each state
ACTIVE_COUNT=$(ls -1 docs/architecture/active/ 2>/dev/null | wc -l | tr -d ' ')
APPROVED_COUNT=$(ls -1 docs/architecture/approved/ 2>/dev/null | wc -l | tr -d ' ')
COMPLETED_COUNT=$(ls -1 docs/architecture/completed/ 2>/dev/null | wc -l | tr -d ' ')
SUPERSEDED_COUNT=$(ls -1 docs/architecture/superseded/ 2>/dev/null | wc -l | tr -d ' ')

echo "Active projects:     ${ACTIVE_COUNT}"
echo "Approved projects:   ${APPROVED_COUNT}"
echo "Completed projects:  ${COMPLETED_COUNT}"
echo "Superseded projects: ${SUPERSEDED_COUNT}"
echo ""

# List all files that need updating
echo "=== FILES REQUIRING UPDATES ==="
grep -rl "docs/architecture" . --include="*.md" 2>/dev/null | grep -v "docs/architecture" | head -20
grep -rl "ARCH-" . --include="*.md" 2>/dev/null | head -20
```

## Step 2: Display Migration Plan

### Dry Run Mode (--dry-run)

```
Migration Plan (DRY RUN)

+---------------------------------------------------------------+
| DIRECTORY CHANGES                                              |
+---------------------------------------------------------------+
| CREATE: docs/spec/                                             |
| CREATE: docs/spec/active/                                      |
| CREATE: docs/spec/approved/                                    |
| CREATE: docs/spec/completed/                                   |
| CREATE: docs/spec/superseded/                                  |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| PROJECT MOVES                                                  |
+---------------------------------------------------------------+
| MOVE: docs/architecture/active/2025-12-11-user-auth/          |
|   TO: docs/spec/active/2025-12-11-user-auth/                  |
|                                                                |
| MOVE: docs/architecture/completed/2025-12-10-api-gateway/     |
|   TO: docs/spec/completed/2025-12-10-api-gateway/             |
|                                                                |
| [... list all projects ...]                                   |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| PROJECT ID UPDATES                                             |
+---------------------------------------------------------------+
| In each project's README.md and other docs:                   |
|   ARCH-2025-12-11-001  ->  SPEC-2025-12-11-001                |
|   ARCH-2025-12-10-002  ->  SPEC-2025-12-10-002                |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| FILE REFERENCE UPDATES                                         |
+---------------------------------------------------------------+
| File: CLAUDE.md                                                |
|   - docs/architecture/  ->  docs/spec/                        |
|   - /arch:             ->  /cs:                               |
|   - ARCH-              ->  SPEC-                              |
|                                                                |
| File: .claude/commands/arch/*.md                              |
|   - Will be preserved (original /arch commands still work)    |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| SUMMARY                                                        |
+---------------------------------------------------------------+
| Projects to migrate: 4                                         |
| Files to update: 12                                            |
| Estimated changes: 47 replacements                             |
+---------------------------------------------------------------+

To execute migration, run:
  /cs/migrate
  /cs/migrate --backup  (creates backup first)
```

## Step 3: Create Backup (if --backup)

```bash
if [ "$BACKUP" = "true" ]; then
    BACKUP_DIR="docs/architecture.backup.$(date +%Y%m%d-%H%M%S)"
    cp -r docs/architecture "$BACKUP_DIR"
    echo "[OK] Backup created: ${BACKUP_DIR}"
fi
```

## Step 4: Create New Directory Structure

```bash
# Create docs/spec structure
mkdir -p docs/spec/active
mkdir -p docs/spec/approved
mkdir -p docs/spec/completed
mkdir -p docs/spec/superseded

echo "[OK] Created docs/spec/ directory structure"
```

## Step 5: Migrate Projects

```bash
# Move all projects from architecture to spec
for state in active approved completed superseded; do
    if [ -d "docs/architecture/${state}" ]; then
        for project in docs/architecture/${state}/*/; do
            if [ -d "$project" ]; then
                PROJECT_NAME=$(basename "$project")
                mv "$project" "docs/spec/${state}/${PROJECT_NAME}"
                echo "[OK] Migrated: ${state}/${PROJECT_NAME}"
            fi
        done
    fi
done

# Remove empty architecture directories
rmdir docs/architecture/active docs/architecture/approved docs/architecture/completed docs/architecture/superseded docs/architecture 2>/dev/null
echo "[OK] Removed empty docs/architecture/ directories"
```

## Step 6: Update Project IDs

For each migrated project, update the project ID:

```bash
for readme in docs/spec/*/*/README.md; do
    if [ -f "$readme" ]; then
        # Update project_id: ARCH- -> SPEC-
        sed -i '' 's/project_id: ARCH-/project_id: SPEC-/g' "$readme"

        # Also update in other documents in same directory
        PROJECT_DIR=$(dirname "$readme")
        for doc in "$PROJECT_DIR"/*.md; do
            sed -i '' 's/ARCH-\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-[0-9]\{3\}\)/SPEC-\1/g' "$doc"
        done

        echo "[OK] Updated IDs in: $PROJECT_DIR"
    fi
done
```

## Step 7: Update External References

### Update CLAUDE.md

```bash
if [ -f "CLAUDE.md" ]; then
    # Update directory references
    sed -i '' 's|docs/architecture/|docs/spec/|g' CLAUDE.md

    # Update command references
    sed -i '' 's|/arch:|/cs:|g' CLAUDE.md
    sed -i '' 's|/arch/|/cs/|g' CLAUDE.md

    # Update project ID references
    sed -i '' 's/ARCH-\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-[0-9]\{3\}\)/SPEC-\1/g' CLAUDE.md

    # Update section headers
    sed -i '' 's/Active Architecture Projects/Active Spec Projects/g' CLAUDE.md
    sed -i '' 's/Completed Architecture Projects/Completed Spec Projects/g' CLAUDE.md
    sed -i '' 's/Architecture Planning/Spec Planning/g' CLAUDE.md

    echo "[OK] Updated CLAUDE.md"
fi
```

### Update Other Documentation

```bash
# Find and update all markdown files with architecture references
for file in $(grep -rl "docs/architecture" . --include="*.md" 2>/dev/null | grep -v "docs/spec"); do
    sed -i '' 's|docs/architecture/|docs/spec/|g' "$file"
    echo "[OK] Updated references in: $file"
done
```

## Step 8: Verify Migration

```bash
echo ""
echo "=== MIGRATION VERIFICATION ==="

# Check all projects migrated
MIGRATED_COUNT=$(find docs/spec -type d -mindepth 2 -maxdepth 2 | wc -l | tr -d ' ')
echo "Projects migrated: ${MIGRATED_COUNT}"

# Check for any remaining architecture references
REMAINING=$(grep -r "docs/architecture" . --include="*.md" 2>/dev/null | grep -v ".backup" | wc -l | tr -d ' ')
if [ "$REMAINING" -gt 0 ]; then
    echo "[!] WARNING: Found ${REMAINING} remaining architecture references"
    grep -r "docs/architecture" . --include="*.md" 2>/dev/null | grep -v ".backup" | head -5
else
    echo "[OK] No remaining architecture references"
fi

# Check for old ARCH- IDs
OLD_IDS=$(grep -r "ARCH-[0-9]" docs/spec --include="*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$OLD_IDS" -gt 0 ]; then
    echo "[!] WARNING: Found ${OLD_IDS} old ARCH- IDs in docs/spec"
else
    echo "[OK] All project IDs updated to SPEC-"
fi
```

## Step 9: Generate Migration Report

```
+---------------------------------------------------------------+
| MIGRATION COMPLETE                                             |
+---------------------------------------------------------------+
|                                                                |
| Projects Migrated:                                             |
|   - Active:     ${ACTIVE_COUNT}                               |
|   - Approved:   ${APPROVED_COUNT}                             |
|   - Completed:  ${COMPLETED_COUNT}                            |
|   - Superseded: ${SUPERSEDED_COUNT}                           |
|                                                                |
| Files Updated:                                                 |
|   - CLAUDE.md                                                  |
|   - ${FILE_COUNT} project documents                           |
|   - ${REF_COUNT} external references                          |
|                                                                |
| Backup: ${BACKUP_PATH:-"None (use --backup to create)"}       |
|                                                                |
+---------------------------------------------------------------+
| NEXT STEPS                                                     |
+---------------------------------------------------------------+
|                                                                |
| 1. Review the changes:                                         |
|    git diff                                                    |
|    git status                                                  |
|                                                                |
| 2. Test the new commands:                                      |
|    /cs/s --list                                               |
|    /cs/p test-project                                         |
|                                                                |
| 3. Commit the migration:                                       |
|    git add -A                                                  |
|    git commit -m "chore: migrate from /arch to /cs"           |
|                                                                |
| 4. (Optional) Remove backup after verification:               |
|    rm -rf ${BACKUP_PATH}                                      |
|                                                                |
+---------------------------------------------------------------+

NOTE: The original /arch:* commands in ~/.claude/commands/arch/
are preserved and will continue to work. You can use either
/arch:* or /cs:* during the transition period.
```

</migration_protocol>

<rollback>

## Rollback Procedure

If something goes wrong:

### From Backup

```bash
# If backup was created
if [ -d "${BACKUP_DIR}" ]; then
    rm -rf docs/spec
    mv "${BACKUP_DIR}" docs/architecture
    git checkout -- CLAUDE.md  # Restore original
    echo "[OK] Rolled back from backup"
fi
```

### From Git

```bash
# If changes were not committed
git checkout -- docs/
git checkout -- CLAUDE.md
echo "[OK] Rolled back from git"
```

### Manual Rollback

```bash
# Move projects back
mv docs/spec/active/* docs/architecture/active/
mv docs/spec/approved/* docs/architecture/approved/
mv docs/spec/completed/* docs/architecture/completed/
mv docs/spec/superseded/* docs/architecture/superseded/

# Update IDs back (SPEC- -> ARCH-)
for file in docs/architecture/*/*/*.md; do
    sed -i '' 's/SPEC-/ARCH-/g' "$file"
done

# Restore CLAUDE.md references
sed -i '' 's|docs/spec/|docs/architecture/|g' CLAUDE.md
sed -i '' 's|/cs:|/arch:|g' CLAUDE.md
```

</rollback>

<edge_cases>

### No Architecture Directory

```
[!] No docs/architecture/ directory found.

This could mean:
1. You haven't used /arch:* commands yet
2. Already migrated to docs/spec/
3. Wrong working directory

Current directory: ${PWD}
```

### Partial Migration Detected

```
[!] Partial migration detected

Found both:
  - docs/architecture/ (${ARCH_COUNT} projects)
  - docs/spec/ (${SPEC_COUNT} projects)

Options:
[1] Continue migration (merge into docs/spec/)
[2] Reset and start fresh (remove docs/spec/, re-migrate)
[3] Cancel

Which option? [1/2/3]
```

### Permission Errors

```
[ERROR] Permission denied while moving files

Some projects could not be migrated:
  - docs/architecture/active/2025-12-11-locked-project/

Please check file permissions and try again:
  chmod -R u+rw docs/architecture/
```

### Large Migration

```
[!] Large migration detected

Found ${PROJECT_COUNT} projects to migrate.
Estimated time: ~${MINUTES} minutes

Proceed? [y/n]
```

</edge_cases>

<force_mode>

## Force Mode (--force)

Skip all confirmations and proceed with defaults:

```bash
if [ "$FORCE" = "true" ]; then
    echo "Force mode: Skipping confirmations"

    # Create structure
    mkdir -p docs/spec/{active,approved,completed,superseded}

    # Move all projects
    for state in active approved completed superseded; do
        mv docs/architecture/${state}/* docs/spec/${state}/ 2>/dev/null
    done

    # Update all references
    find . -name "*.md" -exec sed -i '' 's|docs/architecture/|docs/spec/|g' {} \;
    find docs/spec -name "*.md" -exec sed -i '' 's/ARCH-/SPEC-/g' {} \;

    # Cleanup
    rm -rf docs/architecture

    echo "[OK] Migration complete (force mode)"
fi
```

</force_mode>

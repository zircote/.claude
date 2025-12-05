#!/usr/bin/env python3
"""
Python Deprecation Fixer
Automatically detects and fixes deprecated Python patterns in codebases.
"""

import argparse
import ast
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional


class DeprecationPattern:
    """Represents a single deprecation pattern with its replacement."""

    def __init__(self, config: Dict):
        self.name = config['name']
        self.category = config['category']
        self.deprecated = config['deprecated']
        self.replacement = config['replacement']
        self.regex = re.compile(config['regex'])
        self.replacement_template = config['replacement_template']
        self.required_imports = config.get('required_imports', [])
        self.python_version = config.get('python_version', '')
        self.description = config.get('description', '')


class DeprecationIssue:
    """Represents a found deprecation issue in code."""

    def __init__(self, file_path: str, line_num: int, line_content: str,
                 pattern: DeprecationPattern, column: int = 0):
        self.file_path = file_path
        self.line_num = line_num
        self.line_content = line_content
        self.pattern = pattern
        self.column = column

    def __repr__(self):
        return f"Line {self.line_num}: {self.pattern.deprecated} → {self.pattern.replacement}"


class DeprecationFixer:
    """Main class for detecting and fixing Python deprecations."""

    def __init__(self, patterns_file: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self.patterns: List[DeprecationPattern] = []
        self.issues: List[DeprecationIssue] = []

        # Load patterns from config file
        if patterns_file is None:
            script_dir = Path(__file__).parent
            patterns_file = script_dir / "deprecation_patterns.json"

        self._load_patterns(patterns_file)

    def _load_patterns(self, patterns_file: Path):
        """Load deprecation patterns from JSON config."""
        try:
            with open(patterns_file, 'r') as f:
                config = json.load(f)
                for pattern_config in config.get('patterns', []):
                    self.patterns.append(DeprecationPattern(pattern_config))

            if self.verbose:
                print(f"✓ Loaded {len(self.patterns)} deprecation patterns")
        except FileNotFoundError:
            print(f"⚠️  Warning: Pattern file not found: {patterns_file}")
            print("Using built-in patterns only")
            self._load_builtin_patterns()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing pattern file: {e}")
            sys.exit(1)

    def _load_builtin_patterns(self):
        """Load built-in deprecation patterns if config file is missing."""
        builtin_patterns = [
            {
                "name": "datetime_utcnow",
                "category": "datetime",
                "deprecated": "datetime.utcnow()",
                "replacement": "datetime.now(UTC)",
                "regex": r"datetime\.utcnow\(\)",
                "replacement_template": "datetime.now(UTC)",
                "required_imports": ["from datetime import UTC"],
                "python_version": "3.12+",
                "description": "datetime.utcnow() is deprecated"
            },
            {
                "name": "datetime_utcfromtimestamp",
                "category": "datetime",
                "deprecated": "datetime.utcfromtimestamp()",
                "replacement": "datetime.fromtimestamp(*, UTC)",
                "regex": r"datetime\.utcfromtimestamp\(([^)]+)\)",
                "replacement_template": r"datetime.fromtimestamp(\1, UTC)",
                "required_imports": ["from datetime import UTC"],
                "python_version": "3.12+",
                "description": "datetime.utcfromtimestamp() is deprecated"
            }
        ]

        for pattern_config in builtin_patterns:
            self.patterns.append(DeprecationPattern(pattern_config))

    def scan_file(self, file_path: Path) -> List[DeprecationIssue]:
        """Scan a single Python file for deprecation issues."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Check each line against all patterns
            for line_num, line in enumerate(lines, start=1):
                for pattern in self.patterns:
                    match = pattern.regex.search(line)
                    if match:
                        issue = DeprecationIssue(
                            file_path=str(file_path),
                            line_num=line_num,
                            line_content=line,
                            pattern=pattern,
                            column=match.start()
                        )
                        issues.append(issue)

                        if self.verbose:
                            print(f"  Found: {file_path}:{line_num} - {pattern.name}")

        except UnicodeDecodeError:
            if self.verbose:
                print(f"  ⚠️  Skipping binary file: {file_path}")
        except Exception as e:
            print(f"  ❌ Error scanning {file_path}: {e}")

        return issues

    def scan_directory(self, directory: Path, exclude_patterns: List[str] = None) -> List[DeprecationIssue]:
        """Recursively scan directory for Python files with deprecations."""
        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', '.git', '.venv', 'venv', 'node_modules', '.tox']

        all_issues = []
        python_files = []

        # Find all Python files
        for root, dirs, files in os.walk(directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        if self.verbose:
            print(f"🔍 Scanning {len(python_files)} Python files...")

        # Scan each file
        for py_file in python_files:
            issues = self.scan_file(py_file)
            all_issues.extend(issues)

        return all_issues

    def fix_file(self, file_path: Path, issues: List[DeprecationIssue],
                 dry_run: bool = False) -> Dict:
        """Fix all deprecation issues in a single file."""
        result = {
            'file': str(file_path),
            'fixes_applied': 0,
            'imports_added': [],
            'success': True,
            'error': None
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Group issues by pattern
            required_imports = set()

            # Apply fixes line by line (in reverse to maintain line numbers)
            file_issues = [i for i in issues if Path(i.file_path) == file_path]
            file_issues.sort(key=lambda x: x.line_num, reverse=True)

            for issue in file_issues:
                line_idx = issue.line_num - 1
                old_line = lines[line_idx]

                # Apply the regex replacement
                new_line = issue.pattern.regex.sub(
                    issue.pattern.replacement_template,
                    old_line
                )

                if old_line != new_line:
                    lines[line_idx] = new_line
                    result['fixes_applied'] += 1

                    # Track required imports
                    for imp in issue.pattern.required_imports:
                        required_imports.add(imp)

                    if self.verbose:
                        print(f"  ✓ Line {issue.line_num}: {issue.pattern.name}")

            # Add required imports if they don't exist
            if required_imports:
                lines, added_imports = self._add_imports(lines, required_imports)
                result['imports_added'] = added_imports

            # Write back to file
            if not dry_run and result['fixes_applied'] > 0:
                new_content = '\n'.join(lines)

                # Validate syntax before writing
                try:
                    ast.parse(new_content)
                except SyntaxError as e:
                    result['success'] = False
                    result['error'] = f"Syntax error after fixes: {e}"
                    return result

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def _add_imports(self, lines: List[str], required_imports: Set[str]) -> Tuple[List[str], List[str]]:
        """Add required imports to file if they don't exist."""
        added_imports = []

        # Parse existing imports
        existing_imports = set()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('from ') or stripped.startswith('import '):
                existing_imports.add(stripped)

        # Find the best place to insert imports (after last import or at top)
        insert_pos = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('from ') or stripped.startswith('import '):
                insert_pos = i + 1
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                # Skip docstrings
                continue
            elif stripped and not stripped.startswith('#'):
                # Found first non-import, non-comment line
                break

        # Add missing imports
        for imp in required_imports:
            if imp not in existing_imports:
                # Check if a similar import exists
                if 'datetime import' in imp:
                    # Try to extend existing datetime import
                    for i, line in enumerate(lines):
                        if 'from datetime import' in line and 'UTC' not in line:
                            # Extend existing import
                            lines[i] = line.rstrip() + ', UTC'
                            added_imports.append('UTC to existing datetime import')
                            break
                    else:
                        # Add new import
                        lines.insert(insert_pos, imp)
                        added_imports.append(imp)
                        insert_pos += 1
                else:
                    lines.insert(insert_pos, imp)
                    added_imports.append(imp)
                    insert_pos += 1

        return lines, added_imports

    def create_backup(self, directory: Path) -> Optional[Path]:
        """Create a backup of the directory before making changes."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        backup_dir = directory / '.deprecation-backups' / timestamp

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            if self.verbose:
                print(f"📦 Creating backup in: {backup_dir}")
            return backup_dir
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
            return None

    def generate_report(self, issues: List[DeprecationIssue],
                       as_json: bool = False) -> str:
        """Generate a report of found deprecation issues."""
        if as_json:
            return self._generate_json_report(issues)
        else:
            return self._generate_text_report(issues)

    def _generate_text_report(self, issues: List[DeprecationIssue]) -> str:
        """Generate human-readable text report."""
        if not issues:
            return "✅ No deprecation issues found!"

        # Group by file
        by_file = {}
        for issue in issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)

        # Count by category
        by_category = {}
        for issue in issues:
            cat = issue.pattern.category
            by_category[cat] = by_category.get(cat, 0) + 1

        report = [f"\n🔍 Found {len(issues)} deprecation issue(s) in {len(by_file)} file(s):\n"]

        for file_path in sorted(by_file.keys()):
            file_issues = by_file[file_path]
            report.append(f"📄 {file_path}")
            for issue in sorted(file_issues, key=lambda x: x.line_num):
                report.append(f"  Line {issue.line_num}: {issue.pattern.deprecated} → {issue.pattern.replacement}")
            report.append("")

        report.append("Summary:")
        for category, count in sorted(by_category.items()):
            report.append(f"  - {category} deprecations: {count}")

        return '\n'.join(report)

    def _generate_json_report(self, issues: List[DeprecationIssue]) -> str:
        """Generate JSON report for programmatic use."""
        report = {
            'total_issues': len(issues),
            'files_affected': len(set(i.file_path for i in issues)),
            'issues': []
        }

        for issue in issues:
            report['issues'].append({
                'file': issue.file_path,
                'line': issue.line_num,
                'column': issue.column,
                'deprecated': issue.pattern.deprecated,
                'replacement': issue.pattern.replacement,
                'category': issue.pattern.category,
                'pattern_name': issue.pattern.name
            })

        return json.dumps(report, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Detect and fix Python deprecation warnings',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('path', help='Path to Python file or directory to scan')
    parser.add_argument('--scan-only', action='store_true',
                       help='Only scan for issues, do not fix')
    parser.add_argument('--fix', action='store_true',
                       help='Apply fixes to files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be fixed without making changes')
    parser.add_argument('--pattern', type=str,
                       help='Only fix specific pattern category (e.g., datetime)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup before fixing')

    args = parser.parse_args()

    # Validate path
    path = Path(args.path)
    if not path.exists():
        print(f"❌ Error: Path does not exist: {path}")
        sys.exit(1)

    # Create fixer
    fixer = DeprecationFixer(verbose=args.verbose)

    # Filter patterns if requested
    if args.pattern:
        fixer.patterns = [p for p in fixer.patterns if p.category == args.pattern]
        if not fixer.patterns:
            print(f"❌ No patterns found for category: {args.pattern}")
            sys.exit(1)

    # Scan for issues
    if path.is_file():
        issues = fixer.scan_file(path)
    else:
        issues = fixer.scan_directory(path)

    # Report issues
    if args.scan_only or (not args.fix and not args.dry_run):
        print(fixer.generate_report(issues, as_json=args.json))
        sys.exit(0 if not issues else 1)

    # Fix mode
    if not issues:
        print("✅ No deprecation issues found!")
        sys.exit(0)

    # Create backup unless disabled
    if not args.no_backup and not args.dry_run:
        backup_dir = fixer.create_backup(path if path.is_dir() else path.parent)
        if backup_dir:
            # Copy files that will be modified
            files_to_backup = set(i.file_path for i in issues)
            for file_path in files_to_backup:
                src = Path(file_path)
                rel_path = src.relative_to(path if path.is_dir() else path.parent)
                dst = backup_dir / rel_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    # Group issues by file
    by_file = {}
    for issue in issues:
        if issue.file_path not in by_file:
            by_file[issue.file_path] = []
        by_file[issue.file_path].append(issue)

    # Fix each file
    print(f"\n🔧 {'Preview of fixes' if args.dry_run else 'Fixing deprecations'}...\n")

    total_fixes = 0
    files_modified = 0

    for file_path in sorted(by_file.keys()):
        file_issues = by_file[file_path]
        result = fixer.fix_file(Path(file_path), file_issues, dry_run=args.dry_run)

        if result['success'] and result['fixes_applied'] > 0:
            files_modified += 1
            total_fixes += result['fixes_applied']

            print(f"{'📝' if args.dry_run else '✅'} {file_path}")
            print(f"  {'Would fix' if args.dry_run else 'Fixed'} {result['fixes_applied']} issue(s)")

            if result['imports_added']:
                print(f"  {'Would add' if args.dry_run else 'Added'} imports: {', '.join(result['imports_added'])}")
        elif not result['success']:
            print(f"❌ {file_path}")
            print(f"  Error: {result['error']}")

    # Summary
    print(f"\n{'Preview' if args.dry_run else 'Summary'}:")
    print(f"  - Files {'that would be modified' if args.dry_run else 'modified'}: {files_modified}")
    print(f"  - Total fixes {'that would be applied' if args.dry_run else 'applied'}: {total_fixes}")

    if not args.dry_run and not args.no_backup and backup_dir:
        print(f"  - Backup created: {backup_dir}")


if __name__ == '__main__':
    main()

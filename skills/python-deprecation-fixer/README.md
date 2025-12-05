# Python Deprecation Fixer

A Claude skill that automatically detects and fixes deprecated Python patterns in your codebase.

## Quick Start

```bash
# Scan for deprecations
python3 scripts/fix_deprecations.py /path/to/project --scan-only

# Preview fixes
python3 scripts/fix_deprecations.py /path/to/project --dry-run

# Apply fixes
python3 scripts/fix_deprecations.py /path/to/project --fix
```

## Supported Deprecations

### datetime (Python 3.12+)
- `datetime.utcnow()` → `datetime.now(UTC)`
- `datetime.utcfromtimestamp()` → `datetime.fromtimestamp(*, UTC)`

### collections (Python 3.3+)
- `collections.Mapping` → `collections.abc.Mapping`
- `collections.Sequence` → `collections.abc.Sequence`
- `collections.Iterable` → `collections.abc.Iterable`
- And more...

### unittest (Python 3.2+)
- `self.assertEquals()` → `self.assertEqual()`
- `self.assert_()` → `self.assertTrue()`

### threading (Python 3.10+)
- `threading.currentThread()` → `threading.current_thread()`
- `threading.activeCount()` → `threading.active_count()`

See [SKILL.md](SKILL.md) for complete documentation.

## Features

- ✅ Intelligent AST-based pattern detection
- ✅ Automatic import management
- ✅ Backup creation before changes
- ✅ Dry-run mode for preview
- ✅ Extensible pattern configuration
- ✅ Syntax validation after fixes
- ✅ Support for 17+ deprecation patterns

## Adding New Patterns

Edit `scripts/deprecation_patterns.json` to add new deprecation patterns:

```json
{
  "name": "your_pattern_name",
  "category": "category_name",
  "deprecated": "old_syntax",
  "replacement": "new_syntax",
  "regex": "regex_pattern",
  "replacement_template": "replacement_template",
  "required_imports": ["import statements"],
  "python_version": "3.x+",
  "description": "Description of the deprecation"
}
```

## Files

- **SKILL.md** - Complete skill documentation
- **scripts/fix_deprecations.py** - Main fixer script
- **scripts/deprecation_patterns.json** - Pattern configuration

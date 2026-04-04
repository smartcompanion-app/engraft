# Staging Directory Rollback

## Problem

When `engraft apply` executes customizations, each action writes directly to disk. If action 3 of 5 fails, actions 1 and 2 have already modified files with no way to roll back. This leaves the project in an inconsistent, half-modified state.

## Solution

Introduce a staging directory (`.engraft/`) approach: copy target files into a temporary staging area, execute all actions there, and only copy results back to the project if all actions succeed. On failure, the staging directory is removed and the project remains untouched.

## Approach

### Flow

1. **Collect target files** -- Each action exposes a `target_files() -> list[str]` method. The engine collects a deduplicated set of all target file paths.
2. **Create `.engraft/` staging directory** at `cwd` -- If it already exists, remove it first. Copy all collected target files into it, preserving directory structure.
3. **Execute all actions** against `.engraft/` as the work directory. If any action raises an exception, skip to step 5 (cleanup only, no copy-back).
4. **Copy back** -- Walk the entire `.engraft/` directory and copy all files back to their original locations in the project, overwriting existing files.
5. **Remove `.engraft/` directory**.

### Changes

- **`Action` ABC** (`actions/base.py`): Add abstract method `target_files() -> list[str]`.
- **All action subclasses**: Implement `target_files()` returning `[self.file]`.
- **`file_replace` action**: Add validation that the target file exists before applying (matching the existing source file validation).
- **`engine.py`**: Rewrite `apply()` to implement the 5-step staging flow.
- **`.gitignore`**: Add `.engraft/` as a safety net in case a crash leaves it behind.

### Design decisions

- `target_files()` is an abstract method rather than reading `self.file` directly -- future actions may touch multiple files or no files.
- The copy-back in step 4 walks the entire `.engraft/` directory, not just the files collected in step 1. This allows future actions (e.g., `file_add`) to create new files in staging that get copied back automatically.
- `.engraft/` is created at the working directory (`cwd` of the engraft command).
- No special atomicity for step 4 (the copy-back) -- simple file copy with overwrite is sufficient.

## Out of scope

- In-memory virtual file system approach (rejected due to memory overhead with large files).
- Atomic copy-back via filesystem rename tricks.
- New action types like `file_add` (future work, but the design accommodates them).

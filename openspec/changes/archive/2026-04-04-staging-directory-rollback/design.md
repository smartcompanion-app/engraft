# Design: Staging Directory Rollback

## Architecture

```
engine.apply()
│
├── 1. Collect target files
│   for action in customizations:
│       files |= set(action.target_files())
│
├── 2. Create staging directory
│   .engraft/
│   ├── src/config.json    (copied from work_dir)
│   ├── index.html         (copied from work_dir)
│   └── assets/style.css   (copied from work_dir)
│
├── 3. Execute actions (work_dir = .engraft/)
│   action_1.apply(vars, .engraft/, values_dir)  ── success
│   action_2.apply(vars, .engraft/, values_dir)  ── success
│   action_3.apply(vars, .engraft/, values_dir)  ── FAIL ──┐
│                                                            │
├── 4. Copy back (only on success)                           │
│   .engraft/**  ──▶  work_dir/                              │
│                                                            │
└── 5. Cleanup                              ◀────────────────┘
    shutil.rmtree(.engraft/)
```

## Action ABC change

```python
class Action(ABC):
    @abstractmethod
    def apply(self, variables, work_dir, values_dir) -> None: ...

    @abstractmethod
    def target_files(self) -> list[str]: ...
```

All four existing actions return `[self.file]` from `target_files()`.

## Engine staging logic

The `apply()` function orchestrates the 5 steps. Key details:

- **Step 2**: Use `shutil.copy2` to preserve metadata. Create parent directories as needed. Skip files that don't exist yet (though currently all actions require existing targets).
- **Step 3**: Pass the `.engraft/` path as `work_dir` to each action. `values_dir` remains unchanged (it points to the values file location, not the project).
- **Step 4**: Walk `.engraft/` using `Path.rglob("*")`, copy each file back to `work_dir / relative_path`.
- **Step 5**: Always runs (use `try/finally`), whether actions succeeded or failed.

## file_replace hardening

Add target existence check:

```python
def apply(self, variables, work_dir, values_dir) -> None:
    source_path = values_dir / variables[self.variable]
    target_path = work_dir / self.file

    if not source_path.exists():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")
    if not target_path.exists():
        raise FileNotFoundError(f"Target file does not exist: {target_path}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
```

## Error handling

```
try:
    # steps 1-3
    for action in customizations:
        action.apply(variables, staging_dir, values_dir)
    # step 4 (only reached if all actions succeed)
    copy_back(staging_dir, work_dir)
finally:
    # step 5 (always)
    shutil.rmtree(staging_dir, ignore_errors=True)
```

If an action fails, the exception propagates after cleanup. The caller sees the original error with a clean project state.

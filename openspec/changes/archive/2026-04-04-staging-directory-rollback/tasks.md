# Tasks

- [x] Task 1: Add `target_files()` to Action ABC and all subclasses
  - **Files**: `src/engraft/actions/base.py`, `src/engraft/actions/json_replace.py`, `src/engraft/actions/html_replace.py`, `src/engraft/actions/regex_replace.py`, `src/engraft/actions/file_replace.py`
  - Add `@abstractmethod target_files(self) -> list[str]` to `Action` in `base.py`
  - Implement `target_files()` in all four action subclasses, each returning `[self.file]`

- [x] Task 2: Harden `file_replace` with target file validation
  - **Files**: `src/engraft/actions/file_replace.py`
  - Add a check that `target_path.exists()` before applying, raising `FileNotFoundError` if missing

- [x] Task 3: Implement staging directory logic in engine
  - **Files**: `src/engraft/engine.py`
  - Collect target files from all actions
  - Create `.engraft/` staging directory (remove if exists)
  - Copy target files into staging directory preserving structure
  - Execute actions against staging directory
  - Copy back on success, cleanup always (try/finally)

- [x] Task 4: Add `.engraft/` to `.gitignore`
  - **Files**: `.gitignore`
  - Add `.engraft/` entry

- [x] Task 5: Add tests for staging directory rollback
  - **Files**: `tests/test_engine.py` (new or existing)
  - Test successful apply copies results back and removes `.engraft/`
  - Test failed action leaves project untouched and removes `.engraft/`
  - Test `.engraft/` is removed even on failure
  - Test `target_files()` returns correct paths for each action type

- [x] Task 6: Add test for `file_replace` target validation
  - **Files**: `tests/test_actions/test_file_replace.py`
  - Test that applying `file_replace` when target file doesn't exist raises `FileNotFoundError`

"""E2E harness: runs every scenario against both engraft implementations.

The harness treats the two implementations as opaque CLIs — it invokes them
via subprocess and compares the resulting project tree against a fixture's
`expected/` directory using semantic comparators.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_ROOT = REPO_ROOT / "python"
TS_DIST = REPO_ROOT / "typescript" / "dist" / "cli.js"


@dataclass
class Implementation:
    name: str
    argv: list[str]


def _python_impl() -> Implementation:
    exe = shutil.which("engraft")
    if exe:
        return Implementation(name="python", argv=[exe])
    # Fall back to python -m engraft.cli for reproducibility when the
    # entry point isn't on PATH — avoids a "module attribute" import quirk
    # by using the submodule's main function directly.
    return Implementation(
        name="python",
        argv=["python", "-c", "from engraft.cli import main; main()"],
    )


def _typescript_impl() -> Implementation:
    return Implementation(name="typescript", argv=["node", str(TS_DIST)])


def _check_python_available() -> str | None:
    """Return an error message if the Python CLI can't be invoked."""
    impl = _python_impl()
    try:
        result = subprocess.run(
            impl.argv + ["--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except FileNotFoundError as e:
        return (
            f"Python engraft CLI is not runnable ({e}). "
            "Run `pip install -e python/` from the repo root first."
        )
    if result.returncode != 0:
        return (
            "Python engraft CLI failed to run `--version` "
            f"(exit {result.returncode}). stderr={result.stderr!r}\n"
            "Run `pip install -e python/` from the repo root."
        )
    return None


def _check_typescript_available() -> str | None:
    if not TS_DIST.exists():
        return (
            f"TypeScript build artifact is missing: {TS_DIST}. "
            "Run `(cd typescript && npm install && npm run build)` first."
        )
    return None


def pytest_collection_modifyitems(config, items):
    """At collection time, verify both implementations are runnable."""
    selected = os.environ.get("ENGRAFT_IMPL")
    checks: list[tuple[str, Callable[[], str | None]]] = [
        ("python", _check_python_available),
        ("typescript", _check_typescript_available),
    ]
    errors: list[str] = []
    for name, check in checks:
        if selected and selected != name:
            continue
        msg = check()
        if msg is not None:
            errors.append(msg)
    if errors:
        raise pytest.UsageError("\n\n".join(errors))


IMPLEMENTATIONS = [_python_impl(), _typescript_impl()]


CliCallable = Callable[..., subprocess.CompletedProcess]


@pytest.fixture(params=IMPLEMENTATIONS, ids=lambda impl: impl.name)
def engraft_cli(request) -> CliCallable:
    """A callable that invokes the selected engraft implementation.

    Usage: engraft_cli(["apply", "--template", t, "--values", v], cwd=...)
    """
    impl: Implementation = request.param
    selected = os.environ.get("ENGRAFT_IMPL")
    if selected and selected != impl.name:
        pytest.skip(f"ENGRAFT_IMPL={selected!r} excludes {impl.name}")

    def _run(args: list[str], cwd: str | Path, check: bool = True):
        result = subprocess.run(
            impl.argv + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        if check and result.returncode != 0:
            raise AssertionError(
                f"engraft ({impl.name}) failed with exit {result.returncode}\n"
                f"args={args}\ncwd={cwd}\n"
                f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
            )
        return result

    _run.impl = impl  # type: ignore[attr-defined]
    return _run

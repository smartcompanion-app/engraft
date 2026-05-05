import re
from dataclasses import dataclass, field
from pathlib import Path

from engraft.actions import register
from engraft.actions.base import Action


@register("regex_replace")
@dataclass
class RegexReplace(Action):
    """Replace values in text files using regex selectors with named capture groups."""

    file: str
    replace: list[dict[str, str]] = field(default_factory=list)

    def apply(
        self,
        variables: dict[str, str | None],
        work_dir: Path,
        values_dir: Path,
    ) -> None:
        target = work_dir / self.file
        content = target.read_text()

        for entry in self.replace:
            pattern = entry["selector"]
            var_name = entry["variable"]

            new_value = variables[var_name]
            if new_value is None:
                continue

            normalized = pattern.replace("(?<value>", "(?P<value>")

            if "(?P<value>" not in normalized:
                raise ValueError(
                    "Pattern must contain a (?P<value>...) or (?<value>...) "
                    f"named group: {pattern!r}"
                )

            compiled = re.compile(normalized)

            if not compiled.search(content):
                raise ValueError(
                    f"Pattern {pattern!r} did not match anything in {self.file}"
                )

            def replacer(match: re.Match, new_val: str = new_value) -> str:
                start, end = match.span("value")
                full_start = match.start()
                prefix = match.group()[: start - full_start]
                suffix = match.group()[end - full_start :]
                return prefix + new_val + suffix

            content = compiled.sub(replacer, content)

        target.write_text(content)

    def target_files(self) -> list[str]:
        """Return project-relative file paths this action operates on."""
        return [self.file]

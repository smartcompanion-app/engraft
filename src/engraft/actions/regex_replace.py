import re
from dataclasses import dataclass
from pathlib import Path

from engraft.actions import register
from engraft.actions.base import Action


@register("regex_replace")
@dataclass
class RegexReplace(Action):
    """Replace a value in a text file using a regex selector."""

    target: Path
    selector: str
    value: str

    def apply(self) -> None:
        content = self.target.read_text()

        if "(?P<value>" not in self.selector:
            raise ValueError(
                f"Pattern must contain a (?P<value>...) named group: {self.selector!r}"
            )

        compiled = re.compile(self.selector)

        if not compiled.search(content):
            raise ValueError(
                f"Pattern {self.selector!r} did not match "
                f"anything in {self.target.name}"
            )

        new_value = self.value

        def replacer(match: re.Match, new_val: str = new_value) -> str:
            start, end = match.span("value")
            full_start = match.start()
            prefix = match.group()[: start - full_start]
            suffix = match.group()[end - full_start :]
            return prefix + new_val + suffix

        content = compiled.sub(replacer, content)
        self.target.write_text(content)

import re
from dataclasses import dataclass, field
from pathlib import Path

from lxml import html as lxml_html
from lxml.etree import _Element

from engraft.actions import register
from engraft.actions.base import Action


def _extract_doctype(raw_html: str) -> str | None:
    """Extract the DOCTYPE declaration from raw HTML, if present."""
    match = re.match(r"(<!DOCTYPE[^>]*>)", raw_html, re.IGNORECASE)
    return match.group(1) if match else None


@register("html_replace")
@dataclass
class HtmlReplace(Action):
    """Replace values in HTML files using XPath selectors."""

    file: str
    replace: list[dict[str, str]] = field(default_factory=list)

    def apply(
        self,
        variables: dict[str, str],
        work_dir: Path,
        values_dir: Path,
    ) -> None:
        target = work_dir / self.file
        raw_html = target.read_text()
        doctype = _extract_doctype(raw_html)

        doc = lxml_html.fromstring(raw_html)

        for entry in self.replace:
            selector = entry["selector"]
            var_name = entry["variable"]
            value = variables[var_name]

            results = doc.xpath(selector)

            if len(results) == 0:
                raise ValueError(
                    f"XPath selector {selector!r} matched no elements in {self.file}"
                )
            if len(results) > 1:
                raise ValueError(
                    f"XPath selector {selector!r} matched {len(results)} elements "
                    f"in {self.file}, expected exactly 1"
                )

            result = results[0]

            if isinstance(result, _Element):
                # Element node — set text content
                result.text = value
            else:
                # Attribute result — lxml returns _ElementStringResult
                # which has getparent() and attrname
                parent = result.getparent()
                attr_name = result.attrname
                parent.set(attr_name, value)

        # Serialize back to HTML
        output = lxml_html.tostring(doc, encoding="unicode", method="html")

        if doctype:
            output = doctype + "\n" + output + "\n"
        else:
            output = output + "\n"

        target.write_text(output)

    def target_files(self) -> list[str]:
        """Return project-relative file paths this action operates on."""
        return [self.file]

import re
from dataclasses import dataclass
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
    """Replace a value in an HTML file using an XPath selector."""

    target: Path
    selector: str
    value: str

    def apply(self) -> None:
        raw_html = self.target.read_text()
        doctype = _extract_doctype(raw_html)

        doc = lxml_html.fromstring(raw_html)

        results = doc.xpath(self.selector)

        if len(results) == 0:
            raise ValueError(
                f"XPath selector {self.selector!r} matched no elements "
                f"in {self.target.name}"
            )
        if len(results) > 1:
            raise ValueError(
                f"XPath selector {self.selector!r} matched {len(results)} elements "
                f"in {self.target.name}, expected exactly 1"
            )

        result = results[0]

        if isinstance(result, _Element):
            result.text = self.value
        else:
            parent = result.getparent()
            attr_name = result.attrname
            parent.set(attr_name, self.value)

        output = lxml_html.tostring(doc, encoding="unicode", method="html")

        if doctype:
            output = doctype + "\n" + output + "\n"
        else:
            output = output + "\n"

        self.target.write_text(output)

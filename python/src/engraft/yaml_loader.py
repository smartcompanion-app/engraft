"""YAML 1.2 loader.

PyYAML defaults to YAML 1.1 semantics, where `yes`/`no`/`on`/`off` (and their
capitalized variants) parse as booleans. js-yaml defaults to YAML 1.2, where
only `true`/`false` are booleans. To keep template and values parsing
consistent across the Python and TypeScript implementations, we subclass
SafeLoader and strip the YAML 1.1 boolean resolver, then re-add a stricter
resolver that only matches `true`/`false`/`True`/`False`/`TRUE`/`FALSE`.
"""

import re

import yaml

_STRICT_BOOL_PATTERN = re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$")


class YamlLoader(yaml.SafeLoader):
    """SafeLoader with YAML 1.2 boolean semantics."""


YamlLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != "tag:yaml.org,2002:bool"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}

YamlLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    _STRICT_BOOL_PATTERN,
    list("tTfF"),
)


def safe_load(stream) -> object:
    """Load YAML from a stream using the YAML 1.2 loader."""
    return yaml.load(stream, Loader=YamlLoader)

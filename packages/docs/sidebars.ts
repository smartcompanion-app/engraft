import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

// Listed by hand, in reading order: the pages are plain Markdown that also
// reads on GitHub, so ordering does not live in front matter.
const sidebars: SidebarsConfig = {
  docs: [
    { type: "doc", id: "index", label: "Introduction" },
    "getting-started",
    {
      type: "category",
      label: "Concepts",
      link: { type: "doc", id: "concepts/index" },
      items: ["concepts/template-file", "concepts/values-file", "concepts/variables"],
    },
    {
      type: "category",
      label: "Actions",
      link: { type: "doc", id: "actions/index" },
      items: [
        "actions/json-replace",
        "actions/html-replace",
        "actions/regex-replace",
        "actions/file-replace",
      ],
    },
    "cli",
    "architecture",
  ],
};

export default sidebars;

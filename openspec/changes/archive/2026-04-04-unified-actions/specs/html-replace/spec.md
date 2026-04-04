## ADDED Requirements

### Requirement: HTML element text content replacement via XPath
The `html_replace` action SHALL set the text content of an HTML element identified by an XPath selector.

#### Scenario: Set title element text
- **WHEN** the action is configured with selector `//title` and a variable resolving to `"My New Title"`
- **THEN** the `<title>` element's text content SHALL be set to `"My New Title"`

#### Scenario: Set text of element matched by attribute filter
- **WHEN** the action is configured with selector `//h1[@id="main"]` and a variable resolving to `"Welcome"`
- **THEN** the `<h1 id="main">` element's text content SHALL be set to `"Welcome"`

### Requirement: HTML attribute replacement via XPath
The `html_replace` action SHALL set the value of an HTML attribute identified by an XPath selector ending with `/@attribute-name`.

#### Scenario: Set meta tag content attribute
- **WHEN** the action is configured with selector `//meta[@name="Description"]/@content` and a variable resolving to `"My description"`
- **THEN** the `content` attribute of the `<meta name="Description">` element SHALL be set to `"My description"`

#### Scenario: Set arbitrary attribute
- **WHEN** the action is configured with selector `//html/@lang` and a variable resolving to `"de"`
- **THEN** the `lang` attribute of the `<html>` element SHALL be set to `"de"`

### Requirement: Single-match enforcement
The `html_replace` action SHALL require that each XPath selector matches exactly one element or attribute. If the match count is not exactly one, the action MUST raise an error.

#### Scenario: XPath matches no elements
- **WHEN** the action is configured with selector `//nonexistent` on an HTML file
- **THEN** the action SHALL raise an error with a message indicating the XPath selector matched no elements

#### Scenario: XPath matches multiple elements
- **WHEN** the action is configured with selector `//p` on an HTML file containing three `<p>` elements
- **THEN** the action SHALL raise an error with a message indicating the XPath selector matched 3 elements but expected exactly 1

### Requirement: HTML formatting preservation
The `html_replace` action SHALL preserve the HTML document structure, including the DOCTYPE declaration and HTML serialization conventions (no self-closing void elements).

#### Scenario: DOCTYPE and structure preserved after replacement
- **WHEN** the action modifies an HTML file starting with `<!DOCTYPE html>`
- **THEN** the output file SHALL start with `<!DOCTYPE html>` and void elements like `<meta>` SHALL NOT be self-closed

### Requirement: Multiple replacements per action
The `html_replace` action SHALL support multiple `{selector, variable}` entries in its `replace` list, applying all replacements to the same HTML file.

#### Scenario: Set both title and meta description
- **WHEN** the action is configured with two replace entries — one for `//title` and one for `//meta[@name="Description"]/@content`
- **THEN** both the title text and the meta description attribute SHALL be updated in the output file

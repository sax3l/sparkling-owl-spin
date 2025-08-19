# DSL Quick Reference

This document provides a quick reference for the fields available in the scraping template DSL.

## Top-Level Template Fields

| Field | Type | Description |
|---|---|---|
| `template_id` | `str` | Unique name for the template (snake_case). |
| `version` | `str` | Semantic Version (e.g., `1.0.0`). |
| `domain` | `str?` | Optional: A hint for documentation purposes. |
| `entity` | `str?` | The primary entity type (e.g., `person`, `company`, `vehicle`). |
| `url_pattern` | `regex?` | Optional: A regex pattern used for routing or validation. |
| `requires_js` | `bool` | A hint to the policy engine whether to use a full browser (`true`) or simple HTTP (`false`). |
| `fields[]` | `list` | A list of field specifications (see below). |
| `postprocessors` | `list` | A list of rules to apply to the entire record after all fields are extracted. |
| `samples` | `obj` | Contains `sample_urls` or `sample_htmls` for validation in staging environments. |

---

## `FieldDef` Object

This object defines how to extract, clean, and validate a single piece of data.

| Field | Type | Description |
|---|---|---|
| `name` | `str` | The final key for the data in the database or JSON output (snake_case). |
| `selector` | `str` | The CSS or XPath expression to locate the element(s). |
| `selector_type` | `css` / `xpath` | The type of selector used. Defaults to `css`. |
| `attr` | `str` | The attribute to extract from the element. Use `"text"` for the visible text content, or an attribute name like `href`, `content`, etc. |
| `multi` | `bool` | If `true`, collects a list of values from all matching nodes. |
| `required` | `bool` | If `true`, the extraction will fail if this field is missing or empty. |
| `transforms` | `list` | A sequence of transformations to clean and normalize the raw data. |
| `validators` | `list` | A sequence of validation rules to apply after transformations. |

---

## Validators (MVP Set)

-   **`required`**: Ensures the field is present and not empty.
-   **`regex`**: Matches the value against a regular expression.
    -   `pattern`: The regex pattern.
-   **`length_range`**: Checks the length of a string or list.
    -   `min?`: Minimum length.
    -   `max?`: Maximum length.
-   **`numeric_range`**: Checks if a number is within a range.
    -   `min?`: Minimum value.
    -   `max?`: Maximum value.
-   **`enum`**: Checks if the value is in a predefined list.
    -   `values`: A list of allowed values.

---

## Transforms (MVP Set)

-   **`strip`**, **`upper`**, **`lower`**, **`title`**, **`normalize_whitespace`**: Standard string manipulations.
-   **`null_if`**: Sets the value to `null` if it matches a specific string.
    -   `equals`: The string to match.
-   **`regex_extract`**: Extracts a substring using a regex group.
    -   `pattern`: The regex pattern.
    -   `group`: The capturing group to extract (default: 1).
-   **`regex_sub`**: Replaces substrings matching a regex.
    -   `pattern`: The regex pattern to find.
    -   `repl`: The replacement string.
-   **`to_int`**, **`to_float`**: Type conversion.
-   **`parse_date`**: Parses a date string into a standard format.
    -   `formats[]`: A list of `strptime` formats to try.
-   **`map`**: Replaces a value based on a key-value mapping.
    -   `mapping`: A dictionary of `{ "from": "to" }`.

> **Note:** The repertoire of transforms and validators can be easily extended by following the existing pattern in `src/scraper/dsl/schema.py` and adding the corresponding logic to `src/scraper/template_runtime.py`.

---

## JSON Schema for Validation

To facilitate the creation of valid templates, a JSON Schema can be automatically generated from the underlying Pydantic models. This schema can be used in modern editors (like VSCode with the YAML extension or a web-based Monaco editor) to provide real-time validation and autocompletion.

### Generating the Schema
You can generate the latest schema by running the following script from the project root:

```bash
python scripts/generate_dsl_schema.py
```

This will create or update the schema file at `docs/dsl.schema.json`. This file should be committed to the repository so that UIs and other tools can rely on it.
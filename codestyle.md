# Backend Code Style

## Standard Sources

The backend code of this project mainly references:

- PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
- PEP 257 — Docstring Conventions: https://peps.python.org/pep-0257/

## Conventions

1. Use 4 spaces for indentation; do not use tabs.
2. Functions and variables use `snake_case`; class names use `PascalCase`; constants use `UPPER_CASE`.
3. A single function should have one clear responsibility; expression parsing, database, and HTTP API are implemented in separate modules.
4. Public modules, classes, and key functions use concise docstrings.
5. Keep the line width within 88–100 characters where possible; use parenthesized line breaks for complex expressions.
6. Use parameterized SQL; do not concatenate user input into SQL strings.
7. Public APIs return unified JSON: success includes `success: true`; failure includes `success: false`, `code`, and `message`.
8. Catch predictable business exceptions; do not use a bare `except`.
9. Do not use `eval`, `exec`, or any way of executing user expressions as Python programs.
10. New features should be covered by `unittest` tests; the backend runtime uses only the Python standard library to reduce environment dependencies.

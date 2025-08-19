# Developer Guide

This guide provides instructions for developers working on the ECaDP project.

## Setup

Please refer to the `README.md` for initial project setup.

## Coding Style

-   **Python**: We use `black` for formatting, `ruff` for linting, and `mypy` for type checking. Please run `make lint` before committing.
-   **TypeScript/React**: We use `prettier` for formatting and `eslint` for linting.

## Testing

Tests are located in the `tests/` directory and are written using `pytest`. Tests are categorized by markers: `unit`, `integration`, and `e2e`.

Run all tests with `make test`.
# Schema Registry (Polyglot Demo)

A demonstration of a **polyglot schema registry** with code-generation utilities based on Protocol Buffers. Event schemas are defined in `.proto` files and generated into Go and Python, with a custom plugin that emits Pydantic DTOs for event payloads.

## Overview

- **Single source of truth**: Event types and envelopes are defined in `proto/` using Protobuf (edition 2023).
- **Multi-language output**: [buf](https://buf.build/) generates Go and Python code from the same protos.
- **Custom codegen**: A local buf plugin (`protoc-gen-python-dto`) generates Python DTO classes for any message that has a valid `event_type` option, including `aggregate_id()` and round-trip serialization helpers.
- **CloudEvents envelope**: The registry envelope (`registry/v1/envelope.proto`) is fully compatible with the [CloudEvents](https://cloudevents.io/) spec and implements the **structured** format (required context attributes plus a typed `data` payload).

## Prerequisites

- [buf](https://buf.build/docs/installation) (CLI)
- [Go](https://go.dev/doc/install) (for building the DTO plugin and Go generated code)
- [Python 3.12+](https://www.python.org/downloads/) and [Poetry](https://python-poetry.org/) (for the Python package)

## Project layout

```
├── proto/                 # Protocol Buffer definitions
│   ├── registry/v1/       # Envelope, options (event_type, is_aggregate_id)
│   └── user/v1/          # Example domain events (UserCreated, etc.)
├── go/                    # Go generated code + DTO plugin source
│   ├── cmd/python-dto/   # Custom buf plugin (generates Python DTOs)
│   ├── registry/v1/
│   └── user/v1/
├── python/                # Python package and generated code
│   └── schema_registry/
│       ├── registry/v1/  # Envelope, event_type helpers
│       └── user/v1/      # Generated _pb2 + DTOs (user_created.py, etc.)
├── buf.gen.yaml           # buf codegen config (Python, Go, python-dto plugin)
└── Makefile
```

## Code generation

Generate all protobuf and DTO code (run from repo root):

```bash
make generate
```

This will:

1. Build the custom plugin binary `bin/protoc-gen-python-dto`.
2. Run `buf generate` to produce:
   - **Python**: `*_pb2.py` / `*_pb2.pyi` plus DTO modules (e.g. `user_created.py`) under `python/schema_registry/`.
   - **Go**: `.pb.go` under `go/` with `paths=source_relative`.
3. Apply import-path fixes for the Python protobuf modules.

The DTO plugin only generates classes for messages that have:

- `option (registry.v1.event_type) = "…";` set (exactly one such message option).
- Exactly one field with `[(registry.v1.is_aggregate_id) = true]`. If none or multiple fields have this option, code generation fails with a clear error.

## Envelope and CloudEvents

The `Envelope` message in `proto/registry/v1/envelope.proto` is **fully compatible with the CloudEvents specification** and implements the structured approach:

- Required context attributes: `id`, `source`, `specversion`, `type`.
- Optional `attributes` map for extension attributes (e.g. correlation IDs), with typed values via `CloudEventAttributeValue`.
- Payload in `data_oneof` as `binary_data` (bytes) or `text_data` (string), plus optional `time` (RFC 3339 timestamp).

Event payloads (e.g. `UserCreated`) are serialized into the envelope’s data field; the envelope’s `type` is set from the message’s `event_type` option so producers and consumers can route and deserialize by spec.

## Event types and DTOs

- **`event_type`** (message option in `registry/v1/envelope.proto`): Identifies the event for the schema registry. Any message with this option gets a generated Pydantic DTO with `to_protobuf()`, `from_protobuf()`, `from_bytes()`, and `aggregate_id()`.
- **`is_aggregate_id`** (field option): The single field marked with this option is used to implement `aggregate_id(self) -> str` on the DTO (non-string types are converted with `str()`).

## Python

From the `python/` directory:

```bash
# Install dependencies
poetry install

# Lint (format + check)
make python-lint    # or: poetry run ruff format --check . && ruff check . && mypy .

# Auto-fix format/lint
make python-fix

# Tests
make python-test   # or: poetry run pytest .
```

## Go

From the repo root:

```bash
cd go && go build ./...
```

Generated Go code lives under `go/registry/v1/` and `go/user/v1/`.

## License

See repository license.

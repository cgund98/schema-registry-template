# Schema Registry (Polyglot Demo)

A demonstration of a **polyglot schema registry** with code-generation utilities based on Protocol Buffers. Event schemas are defined in `.proto` files and generated into Go, Python, and Kotlin, with custom plugins that add event-type helpers and DTOs per language.

## Overview

- **Single source of truth**: Event types and envelopes are defined in `proto/` using Protobuf (edition 2023).
- **Multi-language output**: [buf](https://buf.build/) generates Go, Python, and Kotlin/Java code from the same protos.
- **Custom codegen**: Local buf plugins extend generated code for event messages:
  - **protoc-gen-python-dto**: Generates Python Pydantic DTOs with `event_type()`, `aggregate_id()`, and round-trip helpers (`to_protobuf`, `from_protobuf`, `from_bytes`).
  - **protoc-gen-go-events**: Generates `EventType()` and `AggregateId()` methods on Go structs.
  - **protoc-gen-kotlin-events**: Generates Kotlin extension functions `eventType()` and `aggregateId()` on generated message types.
- **CloudEvents envelope**: The registry envelope (`registry/v1/envelope.proto`) is compatible with the [CloudEvents](https://cloudevents.io/) spec (structured format). Builders exist in Go (`registryv1.Build`) and Kotlin (`buildEnvelope()` in the schema-registry lib) to create envelopes with UUID v4 ids and optional extensions.

## Prerequisites

- [buf](https://buf.build/docs/installation) (CLI)
- [Go](https://go.dev/doc/install) (for building plugins and Go code; [golangci-lint](https://golangci-lint.run/) for `make go-lint`)
- [Python 3.12+](https://www.python.org/downloads/) and [Poetry](https://python-poetry.org/) (for the Python package)
- **Kotlin**: JDK 21, [Gradle](https://gradle.org/) (wrapper in `kotlin/`), [ktlint](https://pinterest.github.io/ktlint/), [detekt](https://detekt.dev/) (for `make kotlin-lint`)

## Project layout

```
├── proto/                 # Protocol Buffer definitions
│   ├── registry/v1/       # Envelope, options (event_type, is_aggregate_id)
│   └── user/v1/           # Example domain events (UserCreated, etc.)
├── go/                    # Go generated code + plugin source
│   ├── cmd/python-dto/    # Buf plugin: Python DTOs
│   ├── cmd/go-events/     # Buf plugin: EventType() / AggregateId() on structs
│   ├── cmd/kotlin-events/ # Buf plugin: eventType() / aggregateId() Kotlin extensions
│   ├── registry/v1/       # Envelope, Build(), EventMessage
│   └── user/v1/           # .pb.go + .pb.events.go
├── python/                 # Python package and generated code
│   └── schema_registry/
│       ├── registry/v1/   # Envelope, event_type helpers
│       └── user/v1/      # Generated _pb2 + DTOs (user_created.py, etc.)
├── kotlin/                 # Kotlin library and apps
│   ├── lib/               # Schema registry lib (EnvelopeBuild, generated code)
│   │   └── build/generated/buf/  # Buf-generated Java/Kotlin (after make generate)
│   └── apps/
│       ├── publisher/     # Demo publisher (buildEnvelope + UserCreated)
│       └── consumer/     # Demo consumer
├── .github/workflows/    # CI: python.yml, go.yml, kotlin.yml
├── buf.gen.yaml           # Buf codegen (Python, Go, Kotlin, plugins)
└── Makefile
```

## Code generation

Generate all protobuf and plugin output (run from repo root):

```bash
make generate
```

This will:

1. Build the custom plugin binaries: `bin/protoc-gen-python-dto`, `bin/protoc-gen-go-events`, `bin/protoc-gen-kotlin-events`.
2. Run `buf generate` to produce:
   - **Python**: `*_pb2.py` / `*_pb2.pyi` plus DTO modules under `python/schema_registry/`.
   - **Go**: `.pb.go` and `.pb.events.go` under `go/` with `paths=source_relative`.
   - **Kotlin/Java**: Java and Kotlin stubs plus `EventExtensions.kt` under `kotlin/lib/build/generated/buf/` (package `com.github.cgund98.schemaregistry.*`).
3. Apply import-path fixes for the Python protobuf modules.

The Python DTO, Go events, and Kotlin events plugins only process messages that have:

- `option (registry.v1.event_type) = "…";` set (exactly one such message option).
- Exactly one field with `[(registry.v1.is_aggregate_id) = true]`. If none or multiple fields have this option, code generation fails with a clear error.

## Envelope and CloudEvents

The `Envelope` message in `proto/registry/v1/envelope.proto` is **compatible with the CloudEvents specification** (structured format):

- Required context attributes: `id`, `source`, `specversion`, `type`.
- Optional `attributes` map for extension attributes (e.g. correlation IDs), with typed values via `CloudEventAttributeValue`.
- Payload in `data_oneof` as `binary_data` (bytes) or `text_data` (string), plus optional `time` (RFC 3339 timestamp).

Event payloads (e.g. `UserCreated`) are serialized into the envelope’s data field; the envelope’s `type` is set from the message’s `event_type` option.

## Event types and codegen

- **`event_type`** (message option): Identifies the event for the schema registry. Any message with this option gets:
  - **Python**: A Pydantic DTO with `event_type()`, `aggregate_id()`, `to_protobuf()`, `from_protobuf()`, `from_bytes()`.
  - **Go**: `EventType()` and `AggregateId()` methods on the generated struct (from `protoc-gen-go-events`).
  - **Kotlin**: Extension functions `eventType()` and `aggregateId()` on the generated message (from `protoc-gen-kotlin-events`).
- **`is_aggregate_id`** (field option): The single field marked with this option backs `aggregate_id()` / `AggregateId()` / `aggregateId()`. Codegen fails if none or multiple fields have it.

## Python

From the repo root (Makefile targets) or `python/` for Poetry:

```bash
# Install dependencies (in python/)
poetry install

# Lint (ruff format check, ruff check, mypy)
make python-lint

# Auto-fix format and lint
make python-fix

# Tests
make python-test
```

## Go

From the repo root:

```bash
# Build
cd go && go build ./...

# Lint (gofmt check + golangci-lint)
make go-lint

# Format
make go-fix

# Tests
make go-test
```

- Generated code: `go/registry/v1/`, `go/user/v1/` (`.pb.go` and `.pb.events.go`).
- **Envelope builder**: `registryv1.Build(source, data EventMessage, extensions)` builds a CloudEvents envelope with UUID v4 id; `EventMessage` is implemented by generated event types (e.g. `*userv1.UserCreated`).

## Kotlin

From the repo root. Ensure code is generated first (`make generate`).

```bash
# Lint (ktlint + detekt)
make kotlin-lint

# Auto-fix format (ktlint)
make kotlin-fix

# Tests
make kotlin-test

# Run demo apps
make kotlin-run-publisher
make kotlin-run-consumer
```

- **Package**: Hand-written and generated Kotlin/Java use `com.github.cgund98.schemaregistry` (no underscores; generated under `kotlin/lib/build/generated/buf/`).
- **Library**: `kotlin/lib` exposes `buildEnvelope(source, data, eventType, extensions)` and depends on buf-generated code plus `protobuf-java` / `protobuf-kotlin` (4.x).
- **Apps**: `apps/publisher` and `apps/consumer` depend on the lib; main classes are `com.github.cgund98.schemaregistry.app.publisher.PublisherKt` and `com.github.cgund98.schemaregistry.app.consumer.ConsumerKt`.

## CI

GitHub Actions (`.github/workflows/`) run on push and PR to `main`/`master`:

- **Python** (`python.yml`): Poetry install → `make python-lint` → `make python-test`.
- **Go** (`go.yml`): Setup Go, install golangci-lint → `make go-lint` → `make go-test`.
- **Kotlin** (`kotlin.yml`): Setup Go + Buf → generate (build-plugin + buf generate) → Setup Java 21 → install ktlint & detekt → `make kotlin-lint` → `make kotlin-test`.

## License

See repository license.

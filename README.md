<p align="center">
  <img src="https://raw.githubusercontent.com/cloudevents/spec/main/cloudevents-icon.png" width="100" alt="CloudEvents Logo" />
</p>

# Polyglot Schema Registry

> **The Single Source of Truth for Event-Driven Microservices.** > Enforce strict contracts and eliminate boilerplate with automated CloudEvents + Protobuf DTO generation for **Python**, **Go**, and **Kotlin**.

<p align="center">
  <img src="https://img.shields.io/badge/Spec-CloudEvents_1.0-orange?style=for-the-badge" alt="CloudEvents" />
  <img src="https://img.shields.io/badge/Format-Protobuf_Editions-blue?style=for-the-badge" alt="Protobuf" />
  <img src="https://img.shields.io/badge/Codegen-Buf-white?style=for-the-badge" alt="Buf" />
  <img src="https://img.shields.io/badge/DTO-Pydantic_V2-green?style=for-the-badge" alt="Pydantic" />
</p>

---

## Overview

In a distributed ecosystem, events serve as the primary interface between services. This registry manages the lifecycle of those interfaces to provide:

* **Contract Enforcement:** Centralized Protobuf definitions prevent breaking changes between producers and consumers.
* **Standardized Metadata:** Every event is wrapped in a CloudEvents-compliant envelope, ensuring events can be routed and filtered without inspecting the binary payload.
* **Polyglot DTO Generation:** A custom **Buf** plugin automates the creation of high-level DTOs for **Python (Pydantic)**, **Golang**, and **Kotlin**, ensuring wire-compatibility and local type safety without manual boilerplate.

## Justification

As event-driven systems scale, manual event management becomes a bottleneck. This registry addresses three critical failure points:

1.  **Contract Drift:** Without a registry, changes to a producer's payload silently break downstream consumers. We treat **Schemas as Code** to ensure all changes are versioned and validated.
2.  **Infrastructure Blindness:** Generic message brokers cannot route or filter binary payloads. By promoting CloudEvent metadata to message attributes, we enable native infrastructure filtering (e.g., SNS Filter Policies).
3.  **Language Friction:** Maintaining hand-written mapping logic between Protobuf and application models is error-prone. We use opinionated code generation to ensure that partitioned ordering and event identification are handled identically across Python, Go, and Kotlin.

---

## Technical Design

### 1. Hybrid Envelope Strategy

The registry implements a "Hybrid Envelope" pattern:
* **Infrastructure Layer:** Core metadata (`type`, `source`, `id`) is promoted to message headers/attributes for broker-level routing.
* **Transit Layer:** The domain payload and metadata are bundled into a single Protobuf `Envelope` for atomic delivery, integrity, and long-term archival.

### 2. Opinionated Code Generation

The project utilizes a custom **Buf** plugin to inject utility methods directly into generated classes. By leveraging Protobuf Custom Options, we enforce architectural patterns at the schema level:

* **`event_type()`**: Automatically derived from the `(registry.v1.event_type)` message option. This removes "magic strings" from application code.
* **`aggregate_id()`**: Mapped via the `(registry.v1.is_aggregate_id)` field option. This provides a consistent key for **SNS FIFO MessageGroupIds** or **Kafka Partition Keys**, ensuring guaranteed ordering for specific entities.



### 3. Pluggable Infrastructure

The registry is transport-agnostic. The generated DTOs are designed to be "pluggable" into any in-house publisher or consumer library. 
* **Python**: Generates Pydantic V2 models for runtime validation.
* **Golang**: Generates native structs with serialized helpers.
* **Kotlin**: Generates type-safe data classes for JVM-based services.

---

## Project Layout

```text
├── proto/                 # Protocol Buffer definitions
│   ├── registry/v1/       # Envelope, options (event_type, is_aggregate_id)
│   └── user/v1/           # Example domain events (UserCreated, etc.)
├── go/                    # Go generated code + plugin source
│   ├── cmd/python-dto/    # Buf plugin: Python DTOs
│   ├── cmd/go-events/     # Buf plugin: EventType() / AggregateId() on structs
│   ├── cmd/kotlin-events/ # Buf plugin: eventType() / aggregateId() Kotlin extensions
│   ├── registry/v1/       # Envelope, Build(), EventMessage
│   └── user/v1/           # .pb.go + .pb.events.go
├── python/                # Python package and generated code
│   └── schema_registry/
│       ├── registry/v1/   # Envelope, event_type helpers
│       └── user/v1/       # Generated _pb2 + DTOs (user_created.py, etc.)
├── kotlin/                # Kotlin library and apps
│   ├── lib/               # Schema registry lib (EnvelopeBuild, generated code)
│   └── apps/              # Demo implementation apps
├── buf.gen.yaml           # Buf codegen configuration
└── Makefile               # Unified build interface
```

## Usage Workflow

* **Define**: Add a .proto definition to the proto/ directory.
* **Annotate**: Mark the event_type and is_aggregate_id using custom options.
* **Generate**: Run make generate to update the DTOs for all supported languages.
* **Ship**: Import the generated DTO and use its built-in helpers to publish to your broker.

## Prerequisites

- **Buf CLI**: For Protobuf management and generation.
- **Go 1.22+**: For building plugins and Go-based services.
- **Python 3.12+ & Poetry**: For the Pydantic DTO package.
- **JDK 21 & Gradle**: For Kotlin library and JVM services.
package com.github.cgund98.schemaregistry.app.publisher

import com.github.cgund98.schemaregistry.SchemaRegistry
import com.github.cgund98.schemaregistry.buildEnvelope
import com.github.cgund98.schemaregistry.user.v1.UserCreated
import com.github.cgund98.schemaregistry.user.v1.aggregateId
import com.github.cgund98.schemaregistry.user.v1.eventType

/**
 * Demo publisher entrypoint: publishes events using the schema registry.
 */
fun main() {
    println("Demo publisher (schema registry: $SchemaRegistry)")
    val evt =
        UserCreated
            .newBuilder()
            .setUserId("user-1")
            .setUserName("alice")
            .setEmail("alice@example.com")
            .build()

    println("Event: id=${evt.aggregateId()}, type=${evt.eventType()}")

    val envelope =
        buildEnvelope(
            source = "demo-publisher",
            data = evt,
            eventType = evt.eventType(),
            extensions = emptyMap(),
        )
    println("Envelope: id=${envelope.id}, type=${envelope.type}, source=${envelope.source}")
}

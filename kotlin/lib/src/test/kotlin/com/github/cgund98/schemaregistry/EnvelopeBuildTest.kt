package com.github.cgund98.schemaregistry

import com.github.cgund98.schemaregistry.user.v1.UserCreated
import com.github.cgund98.schemaregistry.user.v1.eventType
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class EnvelopeBuildTest {
    @Test
    fun buildEnvelopeSetsSourceTypeAndSpecversion() {
        val evt =
            UserCreated
                .newBuilder()
                .setUserId("u-1")
                .setUserName("alice")
                .setEmail("alice@example.com")
                .build()
        val envelope =
            buildEnvelope(
                source = "test-service",
                data = evt,
                eventType = evt.eventType(),
            )
        assertEquals("test-service", envelope.source)
        assertEquals("user.v1.created", envelope.type)
        assertEquals("1.0", envelope.specversion)
    }

    @Test
    fun buildEnvelopeSetsIdAsUuid() {
        val evt = UserCreated.newBuilder().setUserId("u-1").build()
        val envelope =
            buildEnvelope(
                source = "test",
                data = evt,
                eventType = evt.eventType(),
            )
        assertTrue(envelope.id.isNotBlank())
        // UUID v4 format: 8-4-4-4-12 hex
        val uuidRegex = Regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", RegexOption.IGNORE_CASE)
        assertTrue(uuidRegex.matches(envelope.id), "id should be a valid UUID: ${envelope.id}")
    }

    @Test
    fun buildEnvelopeSetsTime() {
        val evt = UserCreated.newBuilder().setUserId("u-1").build()
        val before = System.currentTimeMillis()
        val envelope =
            buildEnvelope(
                source = "test",
                data = evt,
                eventType = evt.eventType(),
            )
        val after = System.currentTimeMillis()
        assertTrue(envelope.hasTime())
        val timeMs = envelope.time.seconds * 1000 + envelope.time.nanos / 1_000_000
        assertTrue(timeMs in before..(after + 1000), "time should be around now")
    }

    @Test
    fun buildEnvelopeSerializesDataAsBinary() {
        val evt =
            UserCreated
                .newBuilder()
                .setUserId("u-42")
                .setUserName("bob")
                .setEmail("bob@example.com")
                .build()
        val envelope =
            buildEnvelope(
                source = "test",
                data = evt,
                eventType = evt.eventType(),
            )
        assertTrue(envelope.hasBinaryData())
        assertEquals(evt.toByteString(), envelope.binaryData)
        val roundTrip = UserCreated.parseFrom(envelope.binaryData)
        assertEquals(evt.userId, roundTrip.userId)
        assertEquals(evt.userName, roundTrip.userName)
    }

    @Test
    fun buildEnvelopeIncludesExtensionsAsAttributes() {
        val evt = UserCreated.newBuilder().setUserId("u-1").build()
        val extensions =
            mapOf(
                "correlationid" to "corr-123",
                "traceid" to "trace-456",
            )
        val envelope =
            buildEnvelope(
                source = "test",
                data = evt,
                eventType = evt.eventType(),
                extensions = extensions,
            )
        assertEquals(2, envelope.attributesCount)
        val corr = envelope.getAttributesOrThrow("correlationid")
        assertTrue(corr.hasCeString())
        assertEquals("corr-123", corr.ceString)
        val trace = envelope.getAttributesOrThrow("traceid")
        assertTrue(trace.hasCeString())
        assertEquals("trace-456", trace.ceString)
    }

    @Test
    fun buildEnvelopeEmptyExtensionsHasNoAttributes() {
        val evt = UserCreated.newBuilder().setUserId("u-1").build()
        val envelope =
            buildEnvelope(
                source = "test",
                data = evt,
                eventType = evt.eventType(),
                extensions = emptyMap(),
            )
        assertEquals(0, envelope.attributesCount)
    }
}

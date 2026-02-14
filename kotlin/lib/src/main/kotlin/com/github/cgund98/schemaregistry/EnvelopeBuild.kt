package com.github.cgund98.schemaregistry

import com.github.cgund98.schemaregistry.registry.v1.CloudEventAttributeValue
import com.github.cgund98.schemaregistry.registry.v1.Envelope
import com.google.protobuf.ByteString
import com.google.protobuf.MessageLite
import com.google.protobuf.util.Timestamps
import java.util.UUID

/**
 * Builds a CloudEvents envelope from an event message, source, and optional extensions.
 * The envelope id is a UUID v4; time is set to now; specversion is "1.0".
 *
 * @param source CloudEvents source
 * @param data Serialized event message (must have [eventType] extension when used with event types)
 * @param eventType The event type string (e.g. from `data.eventType()` for generated event messages)
 * @param extensions Optional extension attributes (e.g. correlationid, traceid)
 */
fun buildEnvelope(
    source: String,
    data: MessageLite,
    eventType: String,
    extensions: Map<String, String> = emptyMap(),
): Envelope {
    val dataBytes = ByteString.copyFrom(data.toByteArray())
    val id = UUID.randomUUID().toString()
    val time = Timestamps.fromMillis(System.currentTimeMillis())
    val attrs =
        extensions.mapValues { (_, v) ->
            CloudEventAttributeValue.newBuilder().setCeString(v).build()
        }
    return Envelope
        .newBuilder()
        .setId(id)
        .setSource(source)
        .setSpecversion("1.0")
        .setType(eventType)
        .setBinaryData(dataBytes)
        .setTime(time)
        .putAllAttributes(attrs)
        .build()
}

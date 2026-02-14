package registryv1

import (
	"github.com/google/uuid"

	"google.golang.org/protobuf/proto"
	timestamppb "google.golang.org/protobuf/types/known/timestamppb"
)

// EventMessage is a protobuf message that carries event type (from the event_type option).
// Generated event types (e.g. *userv1.UserCreated) implement this via protoc-gen-go-events.
type EventMessage interface {
	proto.Message
	EventType() string
}

// Build creates a CloudEvents envelope from an event message, source, and optional extensions.
// The envelope id is a UUID v4; time is set to now; specversion is "1.0".
func Build(source string, data EventMessage, extensions map[string]string) (*Envelope, error) {
	dataBytes, err := proto.Marshal(data)
	if err != nil {
		return nil, err
	}

	id := uuid.New().String()

	var attrs map[string]*CloudEventAttributeValue
	if len(extensions) > 0 {
		attrs = make(map[string]*CloudEventAttributeValue, len(extensions))
		for k, v := range extensions {
			attrs[k] = &CloudEventAttributeValue{
				Attr: &CloudEventAttributeValue_CeString{CeString: v},
			}
		}
	}

	return &Envelope{
		Id:          id,
		Source:      source,
		Specversion: "1.0",
		Type:        data.EventType(),
		DataOneof:   &Envelope_BinaryData{BinaryData: dataBytes},
		Time:        timestamppb.Now(),
		Attributes:  attrs,
	}, nil
}

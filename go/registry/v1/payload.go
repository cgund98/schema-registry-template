package registryv1

type Payload interface {
	EventType() string
	AggregateID() string
}

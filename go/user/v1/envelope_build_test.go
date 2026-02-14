package userv1

import (
	"testing"

	"github.com/google/uuid"
	"google.golang.org/protobuf/proto"

	registryv1 "schema-registry/registry/v1"
)

func TestEnvelopeBuild(t *testing.T) {
	evt := &UserCreated{
		UserId:   "user-123",
		UserName: "alice",
		Email:    "alice@example.com",
	}
	source := "my-service"

	env, err := registryv1.Build(source, evt, nil)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if env.GetId() == "" {
		t.Error("expected non-empty id")
	}
	if _, err := uuid.Parse(env.GetId()); err != nil {
		t.Errorf("id should be valid UUID v4: %q: %v", env.GetId(), err)
	}
	if env.GetSource() != source {
		t.Errorf("source: got %q, want %q", env.GetSource(), source)
	}
	if env.GetSpecversion() != "1.0" {
		t.Errorf("specversion: got %q, want 1.0", env.GetSpecversion())
	}
	if env.GetType() != "user.v1.created" {
		t.Errorf("type: got %q, want user.v1.created", env.GetType())
	}
	if env.GetTime() == nil {
		t.Error("expected time to be set")
	}
	data := env.GetBinaryData()
	if len(data) == 0 {
		t.Error("expected binary_data to be set")
	}
	var decoded UserCreated
	if err := proto.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal envelope data: %v", err)
	}
	if decoded.GetUserId() != evt.GetUserId() || decoded.GetUserName() != evt.GetUserName() {
		t.Errorf("decoded data mismatch: got %+v", &decoded)
	}
}

func TestEnvelopeBuild_withExtensions(t *testing.T) {
	evt := &UserDeleted{UserId: "user-456"}
	source := "test-source"
	extensions := map[string]string{
		"correlationid": "req-789",
		"traceid":       "trace-abc",
	}

	env, err := registryv1.Build(source, evt, extensions)
	if err != nil {
		t.Fatalf("Build: %v", err)
	}

	if env.GetType() != "user.v1.deleted" {
		t.Errorf("type: got %q, want user.v1.deleted", env.GetType())
	}
	attrs := env.GetAttributes()
	if attrs == nil {
		t.Fatal("expected attributes to be set")
	}
	for k, v := range extensions {
		av, ok := attrs[k]
		if !ok {
			t.Errorf("missing attribute %q", k)
			continue
		}
		if av.GetCeString() != v {
			t.Errorf("attribute %q: got %q, want %q", k, av.GetCeString(), v)
		}
	}
}

func TestEnvelopeBuild_emptyExtensions(t *testing.T) {
	evt := &UserCreated{UserId: "x", UserName: "y", Email: "z"}
	env, err := registryv1.Build("src", evt, map[string]string{})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	if env.GetAttributes() != nil {
		t.Errorf("expected nil attributes for empty map, got %v", env.GetAttributes())
	}
}

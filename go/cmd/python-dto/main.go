package main

import (
	"fmt"
	"path/filepath"
	"strings"

	registryv1 "schema-registry/registry/v1"

	"google.golang.org/protobuf/compiler/protogen"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/types/descriptorpb"
	"google.golang.org/protobuf/types/pluginpb"
)

// pythonType returns the Python type annotation for a protobuf field.
func pythonType(field *protogen.Field) string {
	optional := field.Desc.HasPresence()
	var base string
	switch field.Desc.Kind() {
	case protoreflect.BoolKind:
		base = "bool"
	case protoreflect.Int32Kind, protoreflect.Sint32Kind, protoreflect.Sfixed32Kind,
		protoreflect.Int64Kind, protoreflect.Sint64Kind, protoreflect.Sfixed64Kind,
		protoreflect.Uint32Kind, protoreflect.Fixed32Kind,
		protoreflect.Uint64Kind, protoreflect.Fixed64Kind:
		base = "int"
	case protoreflect.FloatKind, protoreflect.DoubleKind:
		base = "float"
	case protoreflect.StringKind:
		base = "str"
	case protoreflect.BytesKind:
		base = "bytes"
	case protoreflect.MessageKind:
		// Nested messages not supported in DTO; use Any or generate separately
		base = "Any"
	default:
		base = "Any"
	}
	if field.Desc.Cardinality() == protoreflect.Repeated {
		return "list[" + base + "]"
	}
	if optional {
		return base + " | None = None"
	}
	return base
}

// hasEventTypeOption returns true if the message has the registry.v1.event_type option set.
func hasEventTypeOption(msg *protogen.Message) (string, bool) {
	opts := msg.Desc.Options()
	if opts == nil {
		return "", false
	}
	pm, ok := opts.(proto.Message)
	if !ok {
		return "", false
	}
	if !proto.HasExtension(pm, registryv1.E_EventType) {
		return "", false
	}
	val := proto.GetExtension(pm, registryv1.E_EventType)
	s, ok := val.(string)
	if !ok || strings.TrimSpace(s) == "" {
		return "", false
	}
	return s, true
}

// getAggregateIDField returns the single field marked with (registry.v1.is_aggregate_id) = true.
// It returns an error if no field or more than one field has the option.
func getAggregateIDField(msg *protogen.Message) (*protogen.Field, error) {
	var found *protogen.Field
	for _, field := range msg.Fields {
		opts := field.Desc.Options()
		if opts == nil {
			continue
		}
		pm, ok := opts.(proto.Message)
		if !ok {
			continue
		}
		if !proto.HasExtension(pm, registryv1.E_IsAggregateId) {
			continue
		}
		val := proto.GetExtension(pm, registryv1.E_IsAggregateId)
		if b, ok := val.(bool); !ok || !b {
			continue
		}
		if found != nil {
			return nil, fmt.Errorf(
				"message %s: multiple fields have (registry.v1.is_aggregate_id) = true (e.g. %s and %s)",
				msg.Desc.FullName(), found.Desc.Name(), field.Desc.Name(),
			)
		}
		found = field
	}
	if found == nil {
		return nil, fmt.Errorf(
			"message %s: no field has (registry.v1.is_aggregate_id) = true; exactly one is required",
			msg.Desc.FullName(),
		)
	}
	return found, nil
}

// protoFieldName returns the protobuf field name (snake_case as in .proto).
func protoFieldName(field *protogen.Field) string {
	return string(field.Desc.Name())
}

// snakeCase converts PascalCase to snake_case (e.g. UserCreated -> user_created).
func snakeCase(s string) string {
	if s == "" {
		return s
	}
	var b strings.Builder
	for i, r := range s {
		if i > 0 && r >= 'A' && r <= 'Z' {
			b.WriteByte('_')
		}
		b.WriteRune(r)
	}
	return strings.ToLower(b.String())
}

// pythonImportPath returns the Python import path for the proto file (e.g. schema_registry.user.v1).
func pythonImportPath(protoPath string) string {
	dir := filepath.Dir(protoPath)
	parts := strings.Split(filepath.ToSlash(dir), "/")
	return "schema_registry." + strings.Join(parts, ".")
}

// pythonPbModule returns the generated _pb2 module name (e.g. user_pb2).
func pythonPbModule(protoPath string) string {
	base := filepath.Base(protoPath)
	return strings.TrimSuffix(base, filepath.Ext(base)) + "_pb2"
}

func generateDTO(gen *protogen.Plugin, file *protogen.File, msg *protogen.Message) error {
	aggregateField, err := getAggregateIDField(msg)
	if err != nil {
		return err
	}
	aggregateFieldName := protoFieldName(aggregateField)
	aggregateReturnsStr := aggregateField.Desc.Kind() == protoreflect.StringKind

	protoPath := file.Desc.Path()
	dir := filepath.Dir(protoPath)
	importPath := pythonImportPath(protoPath)
	pbModule := pythonPbModule(protoPath)
	alias := file.GoPackageName // e.g. userv1 for user/v1

	filename := filepath.Join(dir, snakeCase(msg.GoIdent.GoName)+".py")
	g := gen.NewGeneratedFile(filename, protogen.GoImportPath(importPath))

	// Ruff-compatible: isort order (third-party then first-party), double quotes, two blanks before top-level.
	g.P("from pydantic import BaseModel")
	g.P()
	g.P("from ", importPath, " import ", pbModule, " as ", alias)
	g.P()
	g.P()
	g.P("class ", msg.GoIdent.GoName, "(BaseModel):")
	for _, field := range msg.Fields {
		pyType := pythonType(field)
		name := protoFieldName(field)
		g.P("    ", name, ": ", pyType)
	}
	g.P()
	g.P("    def aggregate_id(self) -> str:")
	if aggregateReturnsStr {
		g.P("        return self.", aggregateFieldName)
	} else {
		g.P("        return str(self.", aggregateFieldName, ")")
	}
	g.P()
	g.P("    def to_protobuf(self) -> ", alias, ".", msg.GoIdent.GoName, ":")
	g.P("        return ", alias, ".", msg.GoIdent.GoName, "(")
	for _, field := range msg.Fields {
		name := protoFieldName(field)
		g.P("            ", name, "=self.", name, ",")
	}
	g.P("        )")
	g.P()
	g.P("    @classmethod")
	g.P("    def from_protobuf(cls, msg: ", alias, ".", msg.GoIdent.GoName, ") -> \"", msg.GoIdent.GoName, "\":")
	g.P("        return cls(")
	for _, field := range msg.Fields {
		name := protoFieldName(field)
		g.P("            ", name, "=msg.", name, ",")
	}
	g.P("        )")
	g.P()
	g.P("    @classmethod")
	g.P("    def from_bytes(cls, data: bytes) -> \"", msg.GoIdent.GoName, "\":")
	g.P("        msg = ", alias, ".", msg.GoIdent.GoName, ".FromString(data)")
	g.P("        return cls.from_protobuf(msg)")
	g.P() // Trailing newline for ruff
	return nil
}

func generateFile(gen *protogen.Plugin, file *protogen.File) error {
	for _, msg := range file.Messages {
		eventType, ok := hasEventTypeOption(msg)
		if !ok {
			continue
		}
		_ = eventType // reserved for future use (e.g. validation)
		if err := generateDTO(gen, file, msg); err != nil {
			gen.Error(err)
			return err
		}
	}
	return nil
}

func main() {
	protogen.Options{}.Run(func(gen *protogen.Plugin) error {
		// Declare support for proto editions so buf/protoc will invoke us for edition-based .proto files.
		gen.SupportedFeatures = uint64(pluginpb.CodeGeneratorResponse_FEATURE_SUPPORTS_EDITIONS)
		gen.SupportedEditionsMinimum = descriptorpb.Edition_EDITION_PROTO2
		gen.SupportedEditionsMaximum = descriptorpb.Edition_EDITION_2023

		for _, f := range gen.Files {
			if !f.Generate {
				continue
			}
			if err := generateFile(gen, f); err != nil {
				return err
			}
		}
		return nil
	})
}

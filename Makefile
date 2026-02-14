.PHONY: build-plugin
build-plugin:
	@mkdir -p bin
	@cd go && go build -o ../bin/protoc-gen-python-dto ./cmd/python-dto
	@cd go && go build -o ../bin/protoc-gen-go-events ./cmd/go-events

.PHONY: generate
generate: build-plugin
	@echo "Generating protobuf code..."
	buf generate
	@echo "Fixing Python import paths..."
	@find python/schema_registry -type f \( -name "*_pb2.py" -o -name "*_pb2.pyi" \) -exec sed -i '' '/^from schema_registry\./! s/^from \([a-z_][a-z0-9_]*\)\.v1 import/from schema_registry.\1.v1 import/g' {} +
	@echo "Code generation complete!"

.PHONY: python-lint
python-lint:
	@echo "Linting Python code..."
	@cd python && poetry run ruff format --check .
	@cd python && poetry run ruff check .
	@cd python && poetry run mypy .

.PHONY: python-fix
python-fix:
	@echo "Fixing Python code..."
	@cd python && poetry run ruff format .
	@cd python && poetry run ruff check --fix .

.PHONY: python-test
python-test:
	@echo "Testing Python code..."
	@cd python && poetry run pytest .

.PHONY: go-lint
go-lint:
	@echo "Linting Go code..."
	@cd go && test -z "$$(gofmt -l .)" || (echo "Go files need formatting. Run: make go-fix"; gofmt -l .; exit 1)
	@cd go && golangci-lint run ./...

.PHONY: go-fix
go-fix:
	@echo "Fixing Go code..."
	@cd go && go fmt ./...

.PHONY: go-test
go-test:
	@echo "Testing Go code..."
	@cd go && go test ./...
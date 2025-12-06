# Go Environment Standards

## Specialist Agents
Leverage specialized agents from `~/.claude/agents/` for Go work:

| Agent | Category | Use For |
|-------|----------|---------|
| `golang-pro` | 02-language-specialists | Go idioms, concurrency, error handling |
| `backend-developer` | 01-core-development | API design, service architecture |
| `microservices-architect` | 01-core-development | Distributed systems, gRPC, service mesh |
| `performance-engineer` | 04-quality-security | Profiling, optimization, benchmarking |

## Runtime & Tooling
- **Go version**: 1.25+ (use `go1.25` or later)
- **Module mode**: Always use Go modules (`go.mod`)
- **Linting**: golangci-lint v2.7+ with strict configuration

### Common Commands
```bash
# Module management
go mod init <module-path>     # Initialize module
go mod tidy                   # Clean up dependencies
go mod download               # Download dependencies
go get <package>@latest       # Add/update dependency
go get <package>@v1.2.3       # Pin specific version

# Building & Running
go build ./...                # Build all packages
go run .                      # Run main package
go install ./...              # Install binaries

# Testing
go test ./...                 # Run all tests
go test -race ./...           # Run with race detector
go test -cover ./...          # Run with coverage
go test -v -run TestName      # Run specific test
```

## Code Quality: golangci-lint (v2.7+)

### Configuration
```yaml
# .golangci.yml (golangci-lint v2 format)
version: "2"

run:
  timeout: 5m
  go: "1.25"

linters:
  enable:
    # Defaults
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused

    # Additional recommended
    - bodyclose
    - contextcheck
    - durationcheck
    - errname
    - errorlint
    - exhaustive
    - forcetypeassert
    - gocritic
    - gofmt
    - goimports
    - gosec
    - misspell
    - nilerr
    - nilnil
    - noctx
    - prealloc
    - predeclared
    - revive
    - rowserrcheck
    - sqlclosecheck
    - stylecheck
    - tenv
    - testpackage
    - tparallel
    - unconvert
    - unparam
    - wastedassign
    - whitespace

linters-settings:
  govet:
    enable-all: true
  gofmt:
    simplify: true
  goimports:
    local-prefixes: github.com/yourorg
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
  revive:
    rules:
      - name: blank-imports
      - name: context-as-argument
      - name: context-keys-type
      - name: dot-imports
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: exported
      - name: increment-decrement
      - name: indent-error-flow
      - name: range
      - name: receiver-naming
      - name: time-naming
      - name: unexported-return
      - name: var-declaration
      - name: var-naming

issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - gosec
        - forcetypeassert
```

### Running
```bash
# Install (v2.7+)
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest

# Run
golangci-lint run ./...
golangci-lint run --fix ./...  # Auto-fix where possible
```

## Testing with testify

### Test File Structure
```go
// user_test.go
package user_test  // Use _test suffix for black-box testing

import (
    "context"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/suite"

    "github.com/yourorg/project/internal/user"
)

func TestCreateUser(t *testing.T) {
    t.Parallel()  // Enable parallel execution

    tests := []struct {
        name    string
        input   user.CreateInput
        want    *user.User
        wantErr error
    }{
        {
            name:  "valid user",
            input: user.CreateInput{Name: "Alice", Email: "alice@example.com"},
            want:  &user.User{Name: "Alice", Email: "alice@example.com"},
        },
        {
            name:    "empty name",
            input:   user.CreateInput{Name: "", Email: "alice@example.com"},
            wantErr: user.ErrInvalidName,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            got, err := user.Create(context.Background(), tt.input)

            if tt.wantErr != nil {
                require.ErrorIs(t, err, tt.wantErr)
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tt.want.Name, got.Name)
            assert.Equal(t, tt.want.Email, got.Email)
        })
    }
}
```

### Mocking Pattern
```go
// mocks/repository.go
type MockRepository struct {
    mock.Mock
}

func (m *MockRepository) GetUser(ctx context.Context, id string) (*User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

// In test
func TestService_GetUser(t *testing.T) {
    mockRepo := new(MockRepository)
    mockRepo.On("GetUser", mock.Anything, "123").Return(&User{ID: "123", Name: "Alice"}, nil)

    svc := NewService(mockRepo)
    user, err := svc.GetUser(context.Background(), "123")

    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    mockRepo.AssertExpectations(t)
}
```

### Test Suite Pattern
```go
type UserServiceSuite struct {
    suite.Suite
    repo    *MockRepository
    service *UserService
}

func (s *UserServiceSuite) SetupTest() {
    s.repo = new(MockRepository)
    s.service = NewUserService(s.repo)
}

func (s *UserServiceSuite) TestGetUser() {
    s.repo.On("GetUser", mock.Anything, "123").Return(&User{ID: "123"}, nil)

    user, err := s.service.GetUser(context.Background(), "123")

    s.Require().NoError(err)
    s.Assert().Equal("123", user.ID)
}

func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceSuite))
}
```

## Error Handling

### Wrapped Errors with %w
```go
import (
    "errors"
    "fmt"
)

// Sentinel errors
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrValidation   = errors.New("validation error")
)

// Wrapping errors
func GetUser(ctx context.Context, id string) (*User, error) {
    user, err := repo.Find(ctx, id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, fmt.Errorf("user %s: %w", id, ErrNotFound)
        }
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// Checking errors
if errors.Is(err, ErrNotFound) {
    // Handle not found
}

// Custom error types
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed for %s: %s", e.Field, e.Message)
}

func (e *ValidationError) Unwrap() error {
    return ErrValidation
}
```

## Project Layout (Standard Go)
```
project-root/
├── go.mod
├── go.sum
├── .golangci.yml
├── Makefile
├── README.md
├── cmd/                      # Main applications
│   └── myapp/
│       └── main.go
├── internal/                 # Private packages
│   ├── config/
│   │   └── config.go
│   ├── domain/               # Domain models
│   │   └── user.go
│   ├── repository/           # Data access
│   │   ├── user.go
│   │   └── user_test.go
│   └── service/              # Business logic
│       ├── user.go
│       └── user_test.go
├── pkg/                      # Public libraries (optional)
│   └── httputil/
│       └── response.go
├── api/                      # API definitions
│   └── openapi.yaml
├── migrations/               # Database migrations
├── scripts/                  # Build/deploy scripts
└── testdata/                 # Test fixtures
```

## Common Patterns

### Context Usage
```go
// Always pass context as first parameter
func DoSomething(ctx context.Context, input Input) (Output, error) {
    // Check for cancellation
    select {
    case <-ctx.Done():
        return Output{}, ctx.Err()
    default:
    }

    // Use context with timeout
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    return doWork(ctx, input)
}
```

### Dependency Injection
```go
// Define interfaces in consuming package
type UserRepository interface {
    Get(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

type UserService struct {
    repo   UserRepository
    logger *slog.Logger
}

func NewUserService(repo UserRepository, logger *slog.Logger) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger,
    }
}
```

### Structured Logging with slog
```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("user created",
    slog.String("user_id", user.ID),
    slog.String("email", user.Email),
)

logger.Error("failed to create user",
    slog.String("error", err.Error()),
    slog.Any("input", input),
)
```

### Options Pattern
```go
type ServerOption func(*Server)

func WithPort(port int) ServerOption {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(d time.Duration) ServerOption {
    return func(s *Server) {
        s.timeout = d
    }
}

func NewServer(opts ...ServerOption) *Server {
    s := &Server{
        port:    8080,
        timeout: 30 * time.Second,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
server := NewServer(
    WithPort(9000),
    WithTimeout(60*time.Second),
)
```

## Makefile Template
```makefile
.PHONY: build test lint run

BINARY_NAME=myapp
GO=go

build:
	$(GO) build -o bin/$(BINARY_NAME) ./cmd/$(BINARY_NAME)

test:
	$(GO) test -race -cover ./...

lint:
	golangci-lint run ./...

run:
	$(GO) run ./cmd/$(BINARY_NAME)

tidy:
	$(GO) mod tidy

generate:
	$(GO) generate ./...
```

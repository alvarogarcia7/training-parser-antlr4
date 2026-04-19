# LSP Client

A comprehensive client implementation for testing and validating the Training Language Server Protocol implementation.

## Overview

The LSP client provides a programmatic interface to interact with the training language server, enabling:

- **Connection Management** - Start, initialize, and shutdown the LSP server
- **Document Operations** - Open, edit, save, and close training documents
- **Feature Testing** - Test all LSP features (diagnostics, completion, hover, etc.)
- **Source Validation** - Verify training source code parsing
- **Error Handling** - Comprehensive error handling and reporting

## Features

### Core Functionality

- ✅ Server connection and initialization
- ✅ Document lifecycle management
- ✅ Diagnostics collection and caching
- ✅ Completion requests
- ✅ Hover information
- ✅ Document formatting
- ✅ Semantic tokens
- ✅ Custom notification handlers
- ✅ Error handling with specific exception types

### Validation Methods

- `verify_connection()` - Test server connectivity
- `verify_source_parsing(source)` - Parse source and return diagnostics
- `verify_all_features(source)` - Test all LSP features with source

## Installation

The LSP client is included with the training-parser package:

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
import asyncio
from lsp.client import LSPClient

async def main():
    # Use as context manager (handles cleanup automatically)
    async with LSPClient() as client:
        # Initialize the server
        capabilities = await client.initialize()
        print(f"Server capabilities: {capabilities}")

        # Open a document
        uri = "file:///workout.training"
        text = "Bench press: 3x8x75k\n"
        await client.open_document(uri, "training", 1, text)

        # Get diagnostics
        diagnostics = client.get_diagnostics(uri)
        print(f"Errors: {len(diagnostics)}")

asyncio.run(main())
```

### Verify Connection

```python
async with LSPClient() as client:
    if await client.verify_connection():
        print("✓ Server is responsive")
```

### Parse and Validate Source

```python
async with LSPClient() as client:
    await client.initialize()

    result = await client.verify_source_parsing(
        "Bench press: 3x8x75k\n"
    )

    if result["has_errors"]:
        print(f"Found {result['error_count']} errors")
        for diag in result["diagnostics"]:
            print(f"  - {diag['message']}")
```

### Test All Features

```python
async with LSPClient() as client:
    await client.initialize()

    result = await client.verify_all_features(
        "Bench press: 3x8x75k\n"
    )

    for feature, data in result["features"].items():
        status = "✓" if data["supported"] else "✗"
        print(f"{status} {feature}")
```

## API Reference

### LSPClient

Main client class for interacting with the LSP server.

#### Constructor

```python
client = LSPClient(config: Optional[LSPClientConfig] = None)
```

#### Connection Methods

```python
await client.start()  # Start the server process
await client.stop()   # Stop the server process
await client.initialize(root_uri=None, workspace_folders=None)  # Initialize
await client.shutdown()  # Shutdown gracefully
await client.verify_connection()  # Test if server is responsive
```

#### Document Methods

```python
await client.open_document(uri, language_id, version, text)
await client.change_document(uri, version, text)
await client.save_document(uri, text=None)
await client.close_document(uri)
```

#### Feature Methods

```python
# Completion
completions = await client.completion(uri, line, character)

# Hover
hover = await client.hover(uri, line, character)

# Formatting
edits = await client.formatting(uri, tab_size=4, insert_spaces=True)

# Semantic tokens
tokens = await client.semantic_tokens(uri)

# Diagnostics (cached)
diagnostics = client.get_diagnostics(uri)
```

#### Validation Methods

```python
# Verify source parsing
result = await client.verify_source_parsing(source)
# Returns: {
#   "source": str,
#   "diagnostics": list,
#   "has_errors": bool,
#   "error_count": int
# }

# Test all features
result = await client.verify_all_features(source)
# Returns: {
#   "source": str,
#   "features": {
#     "diagnostics": {...},
#     "completion": {...},
#     "hover": {...},
#     "formatting": {...},
#     "semantic_tokens": {...}
#   }
# }
```

#### Notification Handlers

```python
def handler(params):
    print(f"Received: {params}")

client.register_notification_handler(
    "textDocument/publishDiagnostics",
    handler
)
```

### LSPClientConfig

Configuration for the LSP client.

```python
from lsp.client import LSPClientConfig

config = LSPClientConfig(
    server_command=["training-lsp"],  # Command to start server
    server_path=None,                  # Optional server path
    workspace_path=None,               # Optional workspace path
    trace="off",                       # Trace level: off, messages, verbose
    timeout=5.0                        # Request timeout in seconds
)
```

### Exception Types

```python
from lsp.client import (
    LSPClientError,        # Base exception
    LSPConnectionError,    # Connection/startup errors
    LSPServerError,        # Server-side errors
    LSPTimeoutError        # Timeout errors
)
```

## CLI Tools

The client includes CLI commands for testing without writing code.

### Test Connection

```bash
training-lsp-cli test-connection
```

### Verify Source File

```bash
training-lsp-cli verify workout.training
training-lsp-cli verify workout.training --json-output
```

### Test All Features

```bash
training-lsp-cli test-all workout.training
training-lsp-cli test-all workout.training --json-output
```

### Test Individual Features

```bash
# Completion
training-lsp-cli test-completion "Bench press: " --line 0 --char 13

# Hover
training-lsp-cli test-hover "Bench press: 3x8x75k" --line 0 --char 5
```

See `training-lsp-cli --help` for all available commands.

## Examples

See `lsp/example_client_usage.py` for comprehensive examples:

```bash
python lsp/example_client_usage.py
```

Examples include:
- Basic connection
- Connection verification
- Parsing valid/invalid source
- Testing completion
- Testing hover
- Testing formatting
- Testing semantic tokens
- Tracking diagnostics during changes
- Testing all features
- Custom notification handlers
- Error handling

## Advanced Usage

### Custom Configuration

```python
from pathlib import Path
from lsp.client import LSPClient, LSPClientConfig

config = LSPClientConfig(
    server_command=["python", "-m", "lsp.server"],
    workspace_path=Path("/path/to/workspace"),
    trace="verbose",
    timeout=10.0
)

async with LSPClient(config) as client:
    # ... use client
    pass
```

### Multiple Documents

```python
async with LSPClient() as client:
    await client.initialize()

    # Open multiple documents
    await client.open_document("file:///doc1.training", "training", 1, text1)
    await client.open_document("file:///doc2.training", "training", 1, text2)

    # Get diagnostics for each
    diag1 = client.get_diagnostics("file:///doc1.training")
    diag2 = client.get_diagnostics("file:///doc2.training")
```

### Tracking Changes

```python
async with LSPClient() as client:
    await client.initialize()

    uri = "file:///workout.training"

    # Open initial version
    await client.open_document(uri, "training", 1, "Bench press: 3x8x75k\n")

    # Make changes
    await client.change_document(uri, 2, "Bench press: 3x10x75k\n")
    await client.change_document(uri, 3, "Bench press: 3x12x75k\n")

    # Check current diagnostics
    diagnostics = client.get_diagnostics(uri)
```

### Error Handling

```python
from lsp.client import (
    LSPClient,
    LSPConnectionError,
    LSPServerError,
    LSPTimeoutError
)

try:
    async with LSPClient() as client:
        await client.initialize()
        # ... operations
except LSPConnectionError as e:
    print(f"Failed to connect: {e}")
except LSPServerError as e:
    print(f"Server error: {e}")
except LSPTimeoutError as e:
    print(f"Timeout: {e}")
```

## Testing

Run the test suite:

```bash
pytest lsp/test_client.py -v
```

Test classes:
- `TestLSPClient` - Core client functionality
- `TestLSPClientConfig` - Configuration
- `TestLSPResponse` - Response handling

## Architecture

### Design

The LSP client follows an async/await design for non-blocking I/O:

1. **Process Management** - Manages subprocess for LSP server
2. **Message Protocol** - Implements JSON-RPC over stdin/stdout
3. **Request/Response** - Tracks pending requests with futures
4. **Notifications** - Handles server notifications asynchronously
5. **State Management** - Maintains server state and capabilities

### Message Flow

```
Client                          Server
  |                               |
  |--- initialize request ------->|
  |<-- initialize response -------|
  |--- initialized notification ->|
  |                               |
  |--- didOpen notification ----->|
  |<-- publishDiagnostics --------|
  |                               |
  |--- completion request ------->|
  |<-- completion response -------|
  |                               |
  |--- shutdown request --------->|
  |<-- shutdown response ---------|
  |--- exit notification -------->|
```

## Troubleshooting

### Server Not Found

If you get "training-lsp not found":

```bash
# Verify installation
which training-lsp

# Reinstall if needed
uv pip install -e ".[dev]"
```

### Connection Timeout

Increase timeout in configuration:

```python
config = LSPClientConfig(timeout=10.0)
client = LSPClient(config)
```

### Diagnostics Not Appearing

Add a small delay after document operations:

```python
await client.open_document(uri, "training", 1, text)
await asyncio.sleep(0.2)  # Give server time to process
diagnostics = client.get_diagnostics(uri)
```

### Debug Mode

Enable verbose tracing:

```python
config = LSPClientConfig(trace="verbose")
```

## Contributing

When adding new features to the client:

1. Add the method to `LSPClient` class
2. Add corresponding tests to `test_client.py`
3. Add example usage to `example_client_usage.py`
4. Update this README

## License

Same as the training-parser project.

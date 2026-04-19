"""Example usage of the LSP client for testing and validation."""

import asyncio
import sys
from typing import Any

from lsp.client import LSPClient, LSPClientConfig


async def example_basic_connection() -> None:
    """Example: Basic connection to LSP server."""
    print("=" * 60)
    print("Example 1: Basic Connection")
    print("=" * 60)

    async with LSPClient() as client:
        # Server is automatically started
        print("✓ LSP server started")

        # Initialize the server
        capabilities = await client.initialize()
        print(f"✓ Server initialized with {len(capabilities)} capabilities")

        # List some capabilities
        print("\nServer capabilities:")
        for key, value in list(capabilities.items())[:5]:
            print(f"  • {key}: {value}")

        # Shutdown is automatic with context manager

    print("✓ Server stopped\n")


async def example_verify_connection() -> None:
    """Example: Verify connection status."""
    print("=" * 60)
    print("Example 2: Verify Connection")
    print("=" * 60)

    client = LSPClient()

    try:
        # Check if we can connect
        connected = await client.verify_connection()

        if connected:
            print("✓ Connection verified successfully")
            print(f"✓ Server is initialized: {client.is_initialized}")
        else:
            print("✗ Connection verification failed")
    finally:
        # Clean up
        if client.is_initialized:
            await client.shutdown()
        await client.stop()

    print()


async def example_parse_valid_source() -> None:
    """Example: Parse valid source code."""
    print("=" * 60)
    print("Example 3: Parse Valid Source")
    print("=" * 60)

    source = """Bench press: 3x8x75k
Squat: 5x10x100k
Deadlift: 3x5x120k
"""

    async with LSPClient() as client:
        await client.initialize()

        result = await client.verify_source_parsing(source)

        print(f"Source to parse:\n{source}")
        print(f"\nParsing result:")
        print(f"  Has errors: {result['has_errors']}")
        print(f"  Error count: {result['error_count']}")

        if result['diagnostics']:
            print("\nDiagnostics:")
            for diag in result['diagnostics']:
                print(f"  - {diag}")
        else:
            print("  ✓ No errors found!")

    print()


async def example_parse_invalid_source() -> None:
    """Example: Parse invalid source code."""
    print("=" * 60)
    print("Example 4: Parse Invalid Source")
    print("=" * 60)

    source = """Invalid syntax @#$
Another bad line !!!
"""

    async with LSPClient() as client:
        await client.initialize()

        result = await client.verify_source_parsing(source)

        print(f"Source to parse:\n{source}")
        print(f"\nParsing result:")
        print(f"  Has errors: {result['has_errors']}")
        print(f"  Error count: {result['error_count']}")

        if result['diagnostics']:
            print("\nDiagnostics:")
            for diag in result['diagnostics']:
                line = diag['range']['start']['line'] + 1
                col = diag['range']['start']['character'] + 1
                msg = diag['message']
                print(f"  Line {line}, Col {col}: {msg}")

    print()


async def example_test_completion() -> None:
    """Example: Test completion feature."""
    print("=" * 60)
    print("Example 5: Test Completion")
    print("=" * 60)

    async with LSPClient() as client:
        await client.initialize()

        uri = "file:///test/completion.training"
        text = "Bench press: 3x8x75k\n"

        # Open document
        await client.open_document(uri, "training", 1, text)

        # Request completions at start of line (should get exercise names)
        completions = await client.completion(uri, 0, 0)

        print(f"Completions at start of line:")
        print(f"  Found {len(completions)} items")
        print(f"  Sample (first 5):")
        for comp in completions[:5]:
            label = comp.get('label', '')
            detail = comp.get('detail', '')
            print(f"    • {label} ({detail})")

        # Close document
        await client.close_document(uri)

    print()


async def example_test_hover() -> None:
    """Example: Test hover feature."""
    print("=" * 60)
    print("Example 6: Test Hover")
    print("=" * 60)

    async with LSPClient() as client:
        await client.initialize()

        uri = "file:///test/hover.training"
        text = "Bench press: 3x8x75k\n"

        # Open document
        await client.open_document(uri, "training", 1, text)

        # Request hover at various positions
        positions = [
            (0, 5, "over 'Bench'"),
            (0, 15, "over notation"),
        ]

        for line, char, description in positions:
            hover = await client.hover(uri, line, char)

            print(f"\nHover {description} (line {line}, char {char}):")
            if hover and hover.get('contents'):
                contents = hover['contents']
                if isinstance(contents, dict):
                    value = contents.get('value', str(contents))[:100]
                else:
                    value = str(contents)[:100]
                print(f"  {value}...")
            else:
                print("  No hover information")

        # Close document
        await client.close_document(uri)

    print()


async def example_test_formatting() -> None:
    """Example: Test formatting feature."""
    print("=" * 60)
    print("Example 7: Test Formatting")
    print("=" * 60)

    async with LSPClient() as client:
        await client.initialize()

        uri = "file:///test/formatting.training"
        text = "Bench press:3x8x75k\nSquat:5x10x100k\n"

        # Open document
        await client.open_document(uri, "training", 1, text)

        print(f"Original text:\n{text}")

        # Request formatting
        edits = await client.formatting(uri)

        print(f"\nFormatting edits: {len(edits)}")
        for i, edit in enumerate(edits, 1):
            print(f"  Edit {i}: {edit}")

        # Close document
        await client.close_document(uri)

    print()


async def example_test_semantic_tokens() -> None:
    """Example: Test semantic tokens feature."""
    print("=" * 60)
    print("Example 8: Test Semantic Tokens")
    print("=" * 60)

    async with LSPClient() as client:
        await client.initialize()

        uri = "file:///test/tokens.training"
        text = "Bench press: 3x8x75k\n"

        # Open document
        await client.open_document(uri, "training", 1, text)

        # Request semantic tokens
        tokens = await client.semantic_tokens(uri)

        print(f"Semantic tokens:")
        if tokens and 'data' in tokens:
            data = tokens['data']
            print(f"  Token count: {len(data) // 5}")
            print(f"  Data length: {len(data)}")
            print(f"  Sample data: {data[:15]}...")
        else:
            print("  No tokens returned")

        # Close document
        await client.close_document(uri)

    print()


async def example_track_diagnostics() -> None:
    """Example: Track diagnostics as document changes."""
    print("=" * 60)
    print("Example 9: Track Diagnostics During Changes")
    print("=" * 60)

    async with LSPClient() as client:
        await client.initialize()

        uri = "file:///test/track.training"

        # Start with valid source
        text1 = "Bench press: 3x8x75k\n"
        await client.open_document(uri, "training", 1, text1)

        diag1 = client.get_diagnostics(uri)
        print(f"After opening valid document: {len(diag1)} errors")

        # Change to invalid source
        text2 = "Invalid @#$\n"
        await client.change_document(uri, 2, text2)

        diag2 = client.get_diagnostics(uri)
        print(f"After changing to invalid: {len(diag2)} errors")

        # Change back to valid
        text3 = "Squat: 5x10x100k\n"
        await client.change_document(uri, 3, text3)

        diag3 = client.get_diagnostics(uri)
        print(f"After changing back to valid: {len(diag3)} errors")

        # Close document
        await client.close_document(uri)

    print()


async def example_test_all_features() -> None:
    """Example: Test all features at once."""
    print("=" * 60)
    print("Example 10: Test All Features")
    print("=" * 60)

    source = "Bench press: 3x8x75k\nSquat: 5x10x100k\n"

    async with LSPClient() as client:
        await client.initialize()

        result = await client.verify_all_features(source)

        print(f"Testing all features with source:\n{source}")
        print("\nFeature support:")

        for feature_name, feature_data in result['features'].items():
            supported = feature_data.get('supported', False)
            status = "✓" if supported else "✗"

            print(f"  {status} {feature_name}")

            if 'count' in feature_data:
                print(f"      Items: {feature_data['count']}")

            if 'error' in feature_data:
                print(f"      Error: {feature_data['error']}")

        # Summary
        total = len(result['features'])
        supported = sum(1 for f in result['features'].values() if f.get('supported'))
        print(f"\nSummary: {supported}/{total} features supported")

    print()


async def example_custom_notification_handler() -> None:
    """Example: Register custom notification handler."""
    print("=" * 60)
    print("Example 11: Custom Notification Handler")
    print("=" * 60)

    notifications_received: list[Any] = []

    def handler(params: Any) -> None:
        notifications_received.append(params)
        print(f"  Received notification: {params.get('uri', 'unknown')}")

    async with LSPClient() as client:
        await client.initialize()

        # Register handler for diagnostics
        client.register_notification_handler(
            "textDocument/publishDiagnostics",
            handler
        )

        uri = "file:///test/notify.training"
        text = "Bench press: 3x8x75k\n"

        print("Opening document (should trigger notification)...")
        await client.open_document(uri, "training", 1, text)

        # Wait a bit for notifications
        await asyncio.sleep(0.2)

        print(f"\nTotal notifications received: {len(notifications_received)}")

        await client.close_document(uri)

    print()


async def example_error_handling() -> None:
    """Example: Error handling."""
    print("=" * 60)
    print("Example 12: Error Handling")
    print("=" * 60)

    # Test with invalid server command
    from lsp.client import LSPClientConfig, LSPConnectionError

    config = LSPClientConfig(server_command=["nonexistent-server"])
    client = LSPClient(config)

    try:
        await client.start()
        print("✗ Should have raised an error!")
    except LSPConnectionError as e:
        print(f"✓ Caught expected error: {e}")

    print()


async def main() -> None:
    """Run all examples."""
    examples = [
        example_basic_connection,
        example_verify_connection,
        example_parse_valid_source,
        example_parse_invalid_source,
        example_test_completion,
        example_test_hover,
        example_test_formatting,
        example_test_semantic_tokens,
        example_track_diagnostics,
        example_test_all_features,
        example_custom_notification_handler,
        example_error_handling,
    ]

    print("\n")
    print("=" * 60)
    print("LSP CLIENT USAGE EXAMPLES")
    print("=" * 60)
    print("\n")

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"✗ Example failed: {e}\n")
            import traceback
            traceback.print_exc()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

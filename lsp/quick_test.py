#!/usr/bin/env python3
"""Quick test script for the LSP client."""

import asyncio
import sys

from lsp.client import LSPClient


async def quick_test() -> None:
    """Quick test of LSP client functionality."""
    print("Training LSP Client - Quick Test")
    print("=" * 60)

    # Test 1: Connection
    print("\n1. Testing connection...")
    try:
        async with LSPClient() as client:
            if await client.verify_connection():
                print("   ✓ Connection successful")
                print(f"   ✓ Server capabilities: {len(client.server_capabilities or {})} features")
            else:
                print("   ✗ Connection failed")
                sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error: {e}")
        sys.exit(1)

    # Test 2: Parse valid source
    print("\n2. Testing valid source parsing...")
    try:
        async with LSPClient() as client:
            await client.initialize()

            result = await client.verify_source_parsing(
                "Bench press: 3x8x75k\nSquat: 5x10x100k\n"
            )

            if result["has_errors"]:
                print(f"   ✗ Unexpected errors: {result['error_count']}")
            else:
                print("   ✓ Valid source parsed successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        sys.exit(1)

    # Test 3: Parse invalid source
    print("\n3. Testing invalid source detection...")
    try:
        async with LSPClient() as client:
            await client.initialize()

            result = await client.verify_source_parsing("Invalid @#$\n")

            if result["has_errors"]:
                print(f"   ✓ Errors detected: {result['error_count']}")
            else:
                print("   ✗ Failed to detect errors")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        sys.exit(1)

    # Test 4: All features
    print("\n4. Testing all LSP features...")
    try:
        async with LSPClient() as client:
            await client.initialize()

            result = await client.verify_all_features(
                "Bench press: 3x8x75k\n"
            )

            supported = sum(
                1 for f in result["features"].values()
                if f.get("supported")
            )
            total = len(result["features"])

            print(f"   ✓ Features supported: {supported}/{total}")

            for feature, data in result["features"].items():
                status = "✓" if data.get("supported") else "✗"
                print(f"     {status} {feature}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(quick_test())

#!/usr/bin/env python3
"""
NATS Subscriber for Training Parser
Consumes messages from NATS, parses training data with ANTLR, and prints results
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import nats

# Add parser to path
sys.path.insert(0, str(Path(__file__).parent))
from parser.parser import Parser


async def process_message(msg_data: bytes) -> None:
    """Process a message containing training data."""
    try:
        # Parse JSON message
        data = json.loads(msg_data.decode())

        print("\n" + "=" * 60)
        print("📩 Received message from NATS")
        print("=" * 60)
        print(f"Message ID: {data.get('id', 'N/A')}")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Created: {data.get('timestamps', {}).get('created', 'N/A')}")
        print(f"Edited: {data.get('timestamps', {}).get('edited', 'N/A')}")
        print(f"\nRaw training text:\n{data.get('text', '')}")

        # Extract training text and parse with ANTLR
        training_text = data.get("text", "")

        if training_text:
            print("\n" + "-" * 60)
            print("🔍 Parsing with ANTLR Training Grammar")
            print("-" * 60)

            try:
                parser = Parser.from_string(training_text)
                exercises = parser.parse_sessions()

                print(f"✓ Successfully parsed {len(exercises)} exercises:\n")

                for idx, exercise in enumerate(exercises, 1):
                    print(f"{idx}. {exercise.name}")
                    for set_idx, set_data in enumerate(exercise.sets_, 1):
                        print(
                            f"   Set {set_idx}: {set_data.repetitions} reps × "
                            f"{set_data.weight.amount}{set_data.weight.unit}"
                        )

            except Exception as parse_error:
                print(f"⚠ Parsing error: {parse_error}")
                print("(This is expected for some text formats)")

        print("\n" + "=" * 60)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in message: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


async def main() -> None:
    """Subscribe to NATS and process training messages."""
    print("🚀 Starting NATS Training Parser Subscriber")
    print("Connecting to NATS at localhost:4222...")

    try:
        nc = await nats.connect("nats://localhost:4222")
    except Exception as e:
        print(f"Error: Could not connect to NATS at localhost:4222")
        print(f"Make sure NATS server is running: {e}")
        sys.exit(1)

    print("✓ Connected to NATS\n")
    print("Listening for messages on topic 'training.notes'...")
    print("Press Ctrl+C to exit\n")

    async def message_handler(msg: Any) -> None:
        """Handle incoming messages."""
        await process_message(msg.data)

    # Subscribe to topic
    sub = await nc.subscribe("training.notes")

    try:
        # Wait for messages
        async for msg in sub.messages:
            await message_handler(msg)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down subscriber...")
    finally:
        await sub.unsubscribe()
        await nc.close()


if __name__ == "__main__":
    asyncio.run(main())

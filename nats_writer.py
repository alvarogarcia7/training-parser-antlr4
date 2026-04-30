#!/usr/bin/env python3
"""
NATS Training Session Writer
Subscribes to parsed training sessions and writes them to disk
"""

import asyncio
import json
import os
import sys

import nats

NATS_URL = os.environ.get("NATS_URL", "nats://docker:4222")
INPUT_TOPIC = "messages.30.type.training.10.parsed"
OUTPUT_DIR = "/tmp/training"


async def main():
    """Subscribe to parsed sessions and write to disk."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nc = None
    for attempt in range(5):
        try:
            nc = await nats.connect(NATS_URL, connect_timeout=2)
            break
        except Exception as e:
            if attempt < 4:
                print(f"Connection attempt {attempt + 1}/5 failed, retrying in 1s...")
                await asyncio.sleep(1)
            else:
                print(f"Error: Could not connect to NATS at {NATS_URL} after 5 attempts")
                print(f"Make sure NATS server is running: {e}")
                sys.exit(1)

    if not nc:
        print(f"Error: NATS connection failed")
        sys.exit(1)

    print(f"💾 Writer started, listening on '{INPUT_TOPIC}'...")
    print(f"   Writing sessions to '{OUTPUT_DIR}'")

    counter = 0

    async def handler(msg):
        nonlocal counter
        try:
            message_data = json.loads(msg.data.decode())
            workout = message_data.get("workout", {})
            source_note_id = message_data.get("source_note_id", "unknown")
            session_index = message_data.get("session_index", 0)

            filename = f"{counter}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w") as f:
                json.dump(workout, f, indent=2)

            print(f"✓ Wrote {filename}: {workout.get('date', 'unknown')} (from {source_note_id})")
            counter += 1

        except json.JSONDecodeError as e:
            print(f"✗ Failed to decode message: {e}")
        except Exception as e:
            print(f"✗ Error writing file: {e}")

    await nc.subscribe(INPUT_TOPIC, cb=handler)
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✓ Writer stopped")

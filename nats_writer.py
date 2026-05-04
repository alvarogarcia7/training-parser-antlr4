#!/usr/bin/env python3
"""
NATS Training Session Writer
Subscribes to messages.30.type.training.10.parsed and writes to disk
"""

import asyncio
import json
import os
import ssl
import sys
from pathlib import Path

import nats

NATS_URL = os.environ.get("NATS_URL")
if not NATS_URL:
    print("Error: NATS_URL environment variable not set")
    sys.exit(1)

CERTS_DIR = os.environ.get("CERTS_DIR", "/tmp/nats-certs")
INPUT_TOPIC = "messages.30.type.training.10.parsed"
OUTPUT_DIR = Path("/tmp/nats") / INPUT_TOPIC
MESSAGE_COUNTER_FILE = OUTPUT_DIR / ".counter"


def _make_ssl_ctx() -> ssl.SSLContext:
    """Create SSL context with client certificate for mTLS."""
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cafile=f"{CERTS_DIR}/rootCA.pem")
    ctx.load_cert_chain(
        certfile=f"{CERTS_DIR}/client.pem",
        keyfile=f"{CERTS_DIR}/client.key"
    )
    return ctx


def _get_next_message_number() -> int:
    """Get the next message number from counter file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if MESSAGE_COUNTER_FILE.exists():
            count = int(MESSAGE_COUNTER_FILE.read_text().strip())
        else:
            count = 0
        count += 1
        MESSAGE_COUNTER_FILE.write_text(str(count))
        return count
    except Exception as e:
        print(f"Warning: Could not read counter file: {e}")
        return 1


async def main():
    """Subscribe to parsed sessions and write to disk."""
    nc = None
    ssl_ctx = _make_ssl_ctx()
    for attempt in range(5):
        try:
            nc = await nats.connect(NATS_URL, tls=ssl_ctx, connect_timeout=2)
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

    print(f"💾 Training Writer started")
    print(f"  Input topic:  {INPUT_TOPIC}")
    print(f"  Output dir:   {OUTPUT_DIR}")

    async def handler(msg):
        try:
            message_data = json.loads(msg.data.decode())
            msg_num = _get_next_message_number()
            filename = f"{msg_num}.json"
            filepath = OUTPUT_DIR / filename

            with open(filepath, "w") as f:
                json.dump(message_data, f, indent=2)

            workout = message_data.get("workout", {})
            date = workout.get('date', 'unknown')
            print(f"✓ Saved message #{msg_num} - {date}")
            print(f"  File: {filepath}")

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

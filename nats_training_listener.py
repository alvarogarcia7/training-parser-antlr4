#!/usr/bin/env python3
"""
NATS Training Parser Listener
Subscribes to training messages, parses them with ANTLR4, and publishes sessions
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime

import nats

from src.data_access import SessionGrouper, ExerciseParser
from parser.display import serialize_exercise

NATS_URL = os.environ.get("NATS_URL", "nats://docker:4222")
INPUT_TOPIC = "messages.20.type.training"
OUTPUT_TOPIC = "messages.30.type.training.10.parsed"


async def parse_and_publish(message_data: dict, nc):
    """Parse training message and publish parsed sessions."""
    try:
        note = message_data.get("note", {})
        source_note_id = note.get("id", "unknown")
        note_title = note.get("title", "Untitled")
        note_text = note.get("text", "")

        if not note_text.strip():
            print(f"⚠ Note '{note_title}' has no text, skipping")
            return

        print(f"📖 Parsing: {note_title}")

        lines = note_text.split("\n")
        raw_sessions = SessionGrouper.group_by_sessions(lines)

        if not raw_sessions:
            print(f"⚠ No sessions found in '{note_title}'")
            return

        parser = ExerciseParser()
        parsed_sessions = parser.parse_sessions(raw_sessions)

        for session_index, session in enumerate(parsed_sessions):
            workout_json = {
                "workout_id": f"w_{session['date'].replace('-', '')}_000000",
                "type": "set-centric",
                "date": session["date"],
                "location": "",
                "notes": session.get("notes", ""),
                "statistics": {},
                "exercises": [serialize_exercise(ex) for ex in session["parsed"]]
            }

            output_message = {
                "id": str(uuid.uuid4()),
                "source_note_id": source_note_id,
                "session_index": session_index,
                "workout": workout_json
            }

            await nc.publish(OUTPUT_TOPIC, json.dumps(output_message).encode())
            print(f"✓ Published session {session_index}: {session['date']} ({len(session['parsed'])} exercises)")

    except Exception as e:
        print(f"✗ Error parsing message: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Subscribe to training messages and parse them."""
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

    print(f"🔧 Training listener started, listening on '{INPUT_TOPIC}'...")
    print(f"   Publishing parsed sessions to '{OUTPUT_TOPIC}'")

    async def handler(msg):
        try:
            message_data = json.loads(msg.data.decode())
            await parse_and_publish(message_data, nc)
        except json.JSONDecodeError as e:
            print(f"✗ Failed to decode message: {e}")
        except Exception as e:
            print(f"✗ Error processing message: {e}")

    await nc.subscribe(INPUT_TOPIC, cb=handler)
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✓ Training listener stopped")

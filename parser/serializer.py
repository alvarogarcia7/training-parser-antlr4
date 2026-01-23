from datetime import datetime, timezone
from typing import Any, Optional
from parser.model import Exercise


def serialize_to_set_centric(exercises: list[Exercise], timestamp: Optional[datetime] = None) -> dict[str, Any]:
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    workout_id = f"w_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    exercise_blocks = []
    for exercise in exercises:
        sets = []
        for idx, set_ in enumerate(exercise.sets_, start=1):
            sets.append({
                "setNumber": idx,
                "repetitions": set_["repetitions"],
                "weight": {
                    "amount": set_["weight"]["amount"],
                    "unit": set_["weight"]["unit"]
                }
            })
        
        exercise_blocks.append({
            "name": exercise.name,
            "equipment": "other",
            "sets": sets
        })
    
    return {
        "workout_id": workout_id,
        "type": "set-centric",
        "date": timestamp.isoformat(),
        "location": "",
        "notes": "",
        "statistics": {},
        "exercises": exercise_blocks
    }

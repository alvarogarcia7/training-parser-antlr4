import unittest
from datetime import datetime, timezone
import json
import jsonschema

from parser import Exercise, Units, Set_, Weight
from parser.serializer import serialize_to_set_centric


class TestSerializer(unittest.TestCase):
    def test_single_exercise_serialization(self) -> None:
        exercises = [
            Exercise('Bench Press', [
                Set_(10, Weight(60.0, 'kg')),
                Set_(8, Weight(70.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['workout_id'], 'w_20240115_103000')
        self.assertEqual(result['type'], 'set-centric')
        self.assertEqual(result['date'], '2024-01-15T10:30:00+00:00')
        self.assertEqual(len(result['exercises']), 1)
        
        exercise = result['exercises'][0]
        self.assertEqual(exercise['name'], 'Bench Press')
        self.assertEqual(exercise['equipment'], 'other')
        self.assertEqual(len(exercise['sets']), 2)
        
        self.assertEqual(exercise['sets'][0]['setNumber'], 1)
        self.assertEqual(exercise['sets'][0]['repetitions'], 10)
        self.assertEqual(exercise['sets'][0]['weight']['amount'], 60.0)
        self.assertEqual(exercise['sets'][0]['weight']['unit'], 'kg')
        
        self.assertEqual(exercise['sets'][1]['setNumber'], 2)
        self.assertEqual(exercise['sets'][1]['repetitions'], 8)
        self.assertEqual(exercise['sets'][1]['weight']['amount'], 70.0)
        self.assertEqual(exercise['sets'][1]['weight']['unit'], 'kg')
    
    def test_multiple_exercises_serialization(self) -> None:
        exercises = [
            Exercise('Bench Press', [
                Set_(10, Weight(60.0, 'kg')),
            ]),
            Exercise('Squat', [
                Set_(12, Weight(100.0, 'kg')),
                Set_(10, Weight(110.0, 'kg')),
            ]),
            Exercise('Deadlift', [
                Set_(5, Weight(140.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 2, 20, 14, 45, 30, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(len(result['exercises']), 3)
        
        self.assertEqual(result['exercises'][0]['name'], 'Bench Press')
        self.assertEqual(len(result['exercises'][0]['sets']), 1)
        
        self.assertEqual(result['exercises'][1]['name'], 'Squat')
        self.assertEqual(len(result['exercises'][1]['sets']), 2)
        
        self.assertEqual(result['exercises'][2]['name'], 'Deadlift')
        self.assertEqual(len(result['exercises'][2]['sets']), 1)
    
    def test_various_set_configurations(self) -> None:
        exercises = [
            Exercise('Single Set', [
                Set_(20, Weight(30.0, 'kg')),
            ]),
            Exercise('Three Sets', [
                Set_(8, Weight(50.0, 'kg')),
                Set_(8, Weight(50.0, 'kg')),
                Set_(8, Weight(50.0, 'kg')),
            ]),
            Exercise('Five Sets', [
                Set_(5, Weight(80.0, 'kg')),
                Set_(5, Weight(80.0, 'kg')),
                Set_(5, Weight(80.0, 'kg')),
                Set_(5, Weight(80.0, 'kg')),
                Set_(5, Weight(80.0, 'kg')),
            ]),
            Exercise('Pyramid Sets', [
                Set_(12, Weight(40.0, 'kg')),
                Set_(10, Weight(50.0, 'kg')),
                Set_(8, Weight(60.0, 'kg')),
                Set_(6, Weight(70.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 3, 10, 8, 15, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(len(result['exercises']), 4)
        
        self.assertEqual(len(result['exercises'][0]['sets']), 1)
        self.assertEqual(result['exercises'][0]['sets'][0]['setNumber'], 1)
        
        self.assertEqual(len(result['exercises'][1]['sets']), 3)
        for i in range(3):
            self.assertEqual(result['exercises'][1]['sets'][i]['setNumber'], i + 1)
            self.assertEqual(result['exercises'][1]['sets'][i]['repetitions'], 8)
        
        self.assertEqual(len(result['exercises'][2]['sets']), 5)
        for i in range(5):
            self.assertEqual(result['exercises'][2]['sets'][i]['setNumber'], i + 1)
            self.assertEqual(result['exercises'][2]['sets'][i]['repetitions'], 5)
        
        self.assertEqual(len(result['exercises'][3]['sets']), 4)
        expected_reps = [12, 10, 8, 6]
        expected_weights = [40.0, 50.0, 60.0, 70.0]
        for i in range(4):
            self.assertEqual(result['exercises'][3]['sets'][i]['setNumber'], i + 1)
            self.assertEqual(result['exercises'][3]['sets'][i]['repetitions'], expected_reps[i])
            self.assertEqual(result['exercises'][3]['sets'][i]['weight']['amount'], expected_weights[i])
    
    def test_weight_unit_preservation_kg(self) -> None:
        exercises = [
            Exercise('Bench Press', [
                Set_(10, Weight(60.0, 'kg')),
                Set_(8, Weight(70.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        for set_ in result['exercises'][0]['sets']:
            self.assertEqual(set_['weight']['unit'], 'kg')
    
    def test_weight_unit_preservation_lb(self) -> None:
        exercises = [
            Exercise('Bench Press', [
                Set_(10, Weight(135.0, 'lb')),
                Set_(8, Weight(155.0, 'lb')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        for set_ in result['exercises'][0]['sets']:
            self.assertEqual(set_['weight']['unit'], 'lb')
    
    def test_setNumber_sequential_numbering(self) -> None:
        exercises = [
            Exercise('Exercise One', [
                Set_(10, Weight(50.0, 'kg')),
                Set_(9, Weight(55.0, 'kg')),
                Set_(8, Weight(60.0, 'kg')),
                Set_(7, Weight(65.0, 'kg')),
                Set_(6, Weight(70.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        sets = result['exercises'][0]['sets']
        self.assertEqual(len(sets), 5)
        for i, set_ in enumerate(sets, start=1):
            self.assertEqual(set_['setNumber'], i)
    
    def test_setNumber_sequential_across_exercises(self) -> None:
        exercises = [
            Exercise('Exercise One', [
                Set_(10, Weight(50.0, 'kg')),
                Set_(10, Weight(50.0, 'kg')),
            ]),
            Exercise('Exercise Two', [
                Set_(15, Weight(30.0, 'kg')),
                Set_(15, Weight(30.0, 'kg')),
                Set_(15, Weight(30.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 5, 1, 9, 0, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        ex1_sets = result['exercises'][0]['sets']
        for i, set_ in enumerate(ex1_sets, start=1):
            self.assertEqual(set_['setNumber'], i)
        
        ex2_sets = result['exercises'][1]['sets']
        for i, set_ in enumerate(ex2_sets, start=1):
            self.assertEqual(set_['setNumber'], i)
    
    def test_workout_id_generation_format(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 6, 15, 18, 45, 30, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['workout_id'], 'w_20240615_184530')
        self.assertTrue(result['workout_id'].startswith('w_'))
        self.assertEqual(len(result['workout_id']), 17)
    
    def test_workout_id_default_timestamp(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        
        before = datetime.now(timezone.utc)
        result = serialize_to_set_centric(exercises)
        after = datetime.now(timezone.utc)
        
        self.assertTrue(result['workout_id'].startswith('w_'))
        workout_date_str = result['workout_id'][2:]
        workout_time = datetime.strptime(workout_date_str, '%Y%m%d_%H%M%S').replace(tzinfo=timezone.utc)
        
        self.assertTrue(before.replace(microsecond=0) <= workout_time <= after.replace(microsecond=0))
    
    def test_schema_compliance_basic_structure(self) -> None:
        exercises = [
            Exercise('Bench Press', [
                Set_(10, Weight(60.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertIn('workout_id', result)
        self.assertIn('type', result)
        self.assertIn('date', result)
        self.assertIn('location', result)
        self.assertIn('notes', result)
        self.assertIn('statistics', result)
        self.assertIn('exercises', result)
        
        self.assertIsInstance(result['workout_id'], str)
        self.assertIsInstance(result['type'], str)
        self.assertIsInstance(result['date'], str)
        self.assertIsInstance(result['location'], str)
        self.assertIsInstance(result['notes'], str)
        self.assertIsInstance(result['statistics'], dict)
        self.assertIsInstance(result['exercises'], list)
    
    def test_schema_compliance_exercise_structure(self) -> None:
        exercises = [
            Exercise('Squat', [
                Set_(10, Weight(100.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        exercise = result['exercises'][0]
        self.assertIn('name', exercise)
        self.assertIn('equipment', exercise)
        self.assertIn('sets', exercise)
        
        self.assertIsInstance(exercise['name'], str)
        self.assertIsInstance(exercise['equipment'], str)
        self.assertIsInstance(exercise['sets'], list)
        self.assertGreater(len(exercise['sets']), 0)
    
    def test_schema_compliance_set_structure(self) -> None:
        exercises = [
            Exercise('Deadlift', [
                Set_(5, Weight(140.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        set_ = result['exercises'][0]['sets'][0]
        self.assertIn('setNumber', set_)
        self.assertIn('repetitions', set_)
        self.assertIn('weight', set_)
        
        self.assertIsInstance(set_['setNumber'], int)
        self.assertIsInstance(set_['repetitions'], int)
        self.assertIsInstance(set_['weight'], dict)
        
        self.assertIn('amount', set_['weight'])
        self.assertIn('unit', set_['weight'])
        self.assertIsInstance(set_['weight']['amount'], (int, float))
        self.assertIsInstance(set_['weight']['unit'], str)
        self.assertIn(set_['weight']['unit'], ['kg', 'lb'])
    
    def test_schema_compliance_required_fields(self) -> None:
        exercises = [
            Exercise('Overhead Press', [
                Set_(8, Weight(40.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertIsNotNone(result.get('workout_id'))
        self.assertIsNotNone(result.get('date'))
        self.assertIsNotNone(result.get('exercises'))
        
        exercise = result['exercises'][0]
        self.assertIsNotNone(exercise.get('name'))
        self.assertIsNotNone(exercise.get('sets'))
        
        set_ = exercise['sets'][0]
        self.assertIsNotNone(set_.get('setNumber'))
        self.assertIsNotNone(set_.get('repetitions'))
        self.assertIsNotNone(set_.get('weight'))
    
    def test_schema_compliance_with_jsonschema_validation(self) -> None:
        with open('schema/set-centric.schema.json', 'r') as f:
            schema_content = json.load(f)
        
        with open('schema/common-definitions.schema.json', 'r') as f:
            common_defs = json.load(f)
        
        schema_store = {
            'https://example.com/schemas/common-definitions.json': common_defs
        }
        resolver = jsonschema.RefResolver.from_schema(schema_content, store=schema_store)
        
        exercises = [
            Exercise('Bench Press', [
                Set_(10, Weight(60.0, 'kg')),
                Set_(8, Weight(70.0, 'kg')),
            ]),
            Exercise('Squat', [
                Set_(12, Weight(100.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        jsonschema.validate(instance=result, schema=schema_content, resolver=resolver)
    
    def test_empty_location_and_notes(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['location'], '')
        self.assertEqual(result['notes'], '')
    
    def test_empty_statistics(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['statistics'], {})
    
    def test_type_field_value(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['type'], 'set-centric')
    
    def test_date_format_iso8601(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 7, 22, 15, 30, 45, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['date'], '2024-07-22T15:30:45+00:00')
        parsed_date = datetime.fromisoformat(result['date'])
        self.assertEqual(parsed_date, timestamp)
    
    def test_equipment_field_default_value(self) -> None:
        exercises = [
            Exercise('Test Exercise', [
                Set_(10, Weight(50.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['exercises'][0]['equipment'], 'other')
    
    def test_floating_point_weight_preservation(self) -> None:
        exercises = [
            Exercise('Dumbbell Curl', [
                Set_(12, Weight(12.5, 'kg')),
                Set_(10, Weight(15.0, 'kg')),
                Set_(8, Weight(17.5, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        sets = result['exercises'][0]['sets']
        self.assertEqual(sets[0]['weight']['amount'], 12.5)
        self.assertEqual(sets[1]['weight']['amount'], 15.0)
        self.assertEqual(sets[2]['weight']['amount'], 17.5)
    
    def test_zero_weight_preservation(self) -> None:
        exercises = [
            Exercise('Bodyweight Exercise', [
                Set_(20, Weight(0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['exercises'][0]['sets'][0]['weight']['amount'], 0)
    
    def test_large_repetition_count(self) -> None:
        exercises = [
            Exercise('Calf Raise', [
                Set_(100, Weight(20.0, 'kg')),
            ])
        ]
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        result = serialize_to_set_centric(exercises, timestamp)
        
        self.assertEqual(result['exercises'][0]['sets'][0]['repetitions'], 100)


if __name__ == '__main__':
    unittest.main()

# Quick Start: Grammar Formats

A simple guide to get started with the training log grammar formats.

## 5-Minute Overview

The parser supports recording workouts in plain text. Here are the main formats:

### 1. Whole Set Format: `NxNxweight`
Most compact notation for consistent sets.

```
Overhead press: 5x6x40k
```
→ 5 sets of 6 reps at 40kg

### 2. Weight First Format: `weight NxN`
Specify weight, then sets × reps.

```
Squat 70k: 5x10
```
→ 5 sets of 10 reps at 70kg

### 3. Progressive Weight Format: `Nxxweight,weight,...`
Same reps, different weights (note the double 'xx').

```
Squat: 5xx60k,70k,80k,90k,100k
```
→ 5 reps at each weight: 60kg, 70kg, 80kg, 90kg, 100kg

### 4. Variable Reps Format: `weight: N,N,N`
Same weight, different reps.

```
Deadlift 60k: 20,15,8,8
```
→ 20, 15, 8, 8 reps all at 60kg

## Complete Workout Example

```
Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
Deadlift 60k: 20,15,8,8
Row en máquina 41k: 15,8
```

## Mix and Match

You can combine formats in one exercise:

```
Squat 60k: 10, 3x8x80k, 5xx100k,110k,120k
```

This gives you:
- 1 set of 10 reps at 60kg
- 3 sets of 8 reps at 80kg
- 5 reps at 100kg, 110kg, and 120kg

## Key Rules

✅ **DO:**
- End each exercise with a newline
- Use 'k' for kilograms (or omit, both work)
- Mix formats as needed
- Use accents in exercise names (máquina)
- Use hyphens in names (Cable-fly)

❌ **DON'T:**
- Use single 'x' for progressive weights (use 'xx')
- Forget newlines between exercises
- Try to use lbs (only kg supported)

## Weight Options

All of these work:
- `100k` - Integer with k (recommended)
- `100` - Integer without k
- `62.5k` - Decimal with k
- `62.5` - Decimal without k

## Learn More

- **Quick reference**: [GRAMMAR_FORMATS.md](GRAMMAR_FORMATS.md)
- **Detailed syntax**: [SYNTAX.md](SYNTAX.md)
- **All documentation**: [GRAMMAR_DOCUMENTATION_INDEX.md](GRAMMAR_DOCUMENTATION_INDEX.md)

## Try It Out

See all formats in action:
```bash
make test-grammar-formats
```

Or test with your own text:
```python
from parser import Parser

text = """
Squat 100k: 5
Bench press: 3x8x75k
"""

result = Parser.from_string(text).parse_sessions()
print(result)
```

## Common Patterns

### Strength Training (5x5)
```
Squat: 5x5x100k
Bench press: 5x5x80k
Deadlift: 5x5x120k
```

### Bodybuilding (3x8-12)
```
Bench press 75k: 12,10,8
Squat 80k: 3x10
Leg press: 10xx100k,120k,140k
```

### Progressive Overload
```
Squat: 5xx60k,70k,80k,90k,100k
Bench press: 5xx40k,50k,60k,70k,80k
```

### AMRAP (As Many Reps As Possible)
```
Deadlift 100k: 15,12,10,8,6
```

### Pyramid Training
```
Bench press: 12xx40k,50k,60k,70k 10xx80k 12xx70k,60k,50k,40k
```

---

That's it! You now know all the basic formats. Check the full documentation for more details.

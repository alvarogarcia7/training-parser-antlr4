---
id: decision-1
title: Format for Storage of Data
date: '2026-04-28 03:37'
status: accepted
published: true
---

Based on [Doc-1](documentation/1)

## Context

Excerpt from [doc-1 - research-on-storage.md](../docs/doc-1%20-%20research-on-storage.md) / [2026-01-23_research-data-storage.pdf](../docs/2026-01-23_research-data-storage.pdf)

>The 3 common data models that actually work
>1. Set-centric (most common, most flexible)
>
>This is the closest thing to a de-facto standard.
>
>Each set is a row/object.
>
>[Data/Schema has been omitted]
>
>Used by
>
>Strong, Hevy, TrainerRoad strength beta
>Most coach spreadsheets
>Wearables that export strength data
>
>Pros
>
>Handles everything
>Easy to query and analyze
>Scales well
>
>Cons
>
>Verbose
>Slightly annoying for manual entry
>
>👉 If you want longevity and interoperability, this is the safest choice.
>
>2. Exercise-block (human-friendly, semi-structured)
>
>This is what most people write, even if machines later normalize it.
>
>Example
>
>
>Supersets
>
>"superset": ["Bench Press", "Barbell Row"]
>
>Pros
>
>Easy for humans
>Compact
>Mirrors training logs
>
>Cons
>
>Harder to analyze at scale
>Superset timing/rest gets fuzzy
>
>👉 Good for apps and UX, usually converted internally to set-centric.
>
>3. Workout graph model (most expressive, least adopted)
>
>This treats training as a DAG (directed graph).
>
>Nodes = sets
>Edges = order, rest, or dependency
>Supersets are parallel branches
>
>Pros
>
>Perfectly models real training
>Handles circuits, EMOMs, complexes
>
>Cons
>
>Overkill for 95% of use cases
>Almost no consumer tools support it
>
>👉 Used in research or advanced coaching systems only.
>
>What about existing “standards”?
>
>There are attempts, but none won:
>
>FIT / FIT-SDK → strength support is weak
>Open mHealth → too abstract
>TrainingPeaks / Intervals.icu → endurance-centric
>GymML datasets → research-focused, not practical
>
>No equivalent of GPX for lifting exists.

----

>My blunt recommendation
>
>If you’re designing anything serious (app, analysis pipeline, long-term log):
>
>Store everything as individual sets with optional grouping IDs
>
>Minimum viable schema:
>
>workout_id
>timestamp
>exercise_id
>set_index
>reps
>load
>unit
>superset_id (nullable)
>rpe (optional)
>tempo (optional)
>rest_sec (optional)
>
>You can always:
>
>Render it nicely for humans
>Export it to text formats
>Extend it later without breaking history



## Decision

The format for storage of data will be JSON.

The schema will be the Set-Centric Schema: [set-centric.schema.json](../../schema/set-centric.schema.json)


## Consequences

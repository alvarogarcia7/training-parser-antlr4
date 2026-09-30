"""One-repetition maximum (1RM) estimation.

Brzycki formula::

    1RM = weight * 36 / (37 - repetitions)

The formula is undefined for 37 or more repetitions, and becomes less
accurate as repetitions grow (it is most reliable below ~10 repetitions).
"""

BRZYCKI_MAX_REPS = 36


def brzycki_1rm(weight: float, repetitions: int) -> float:
    """Estimate the 1RM from a set of `repetitions` performed with `weight`."""
    if weight < 0:
        raise ValueError(f"weight must be non-negative, got {weight}")
    if not 1 <= repetitions <= BRZYCKI_MAX_REPS:
        raise ValueError(
            f"Brzycki formula requires 1..{BRZYCKI_MAX_REPS} repetitions, got {repetitions}"
        )
    return weight * 36 / (37 - repetitions)


def percentage_of_1rm(weight: float, one_rep_max: float) -> float:
    """Weight as a percentage of the 1RM (e.g., 50 kg of a 100 kg 1RM -> 50.0)."""
    if one_rep_max <= 0:
        raise ValueError(f"one_rep_max must be positive, got {one_rep_max}")
    return weight / one_rep_max * 100

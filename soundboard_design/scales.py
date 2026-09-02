"""Scales and tuning constants shared by the whole system.

Tokens address notes by scale degree, never by frequency. Everything that
turns a degree into a pitch lives here, so changing the scale or the
temperament rewrites the entire sound set at once and no token can fall
out of tune with another.
"""

from .domain import Scale


# Frequency ratios of the twelve semitones in just intonation. Whole number
# ratios make the harmonics of two notes coincide exactly, which is why
# superposed tokens do not beat against each other in this temperament.
JUST_RATIOS: tuple[float, ...] = (
    1.0,
    16.0 / 15.0,
    9.0 / 8.0,
    6.0 / 5.0,
    5.0 / 4.0,
    4.0 / 3.0,
    45.0 / 32.0,
    3.0 / 2.0,
    8.0 / 5.0,
    5.0 / 3.0,
    9.0 / 5.0,
    15.0 / 8.0,
)


PENTATONIC = Scale(
    key="pentatonique",
    label="Pentatonique",
    description="Aucun de ses intervalles ne peut sonner faux, même joué en désordre.",
    steps=(0, 2, 4, 7, 9),
)

MAJOR = Scale(
    key="majeur",
    label="Majeur",
    description="Sept degrés, plus de nuances disponibles, un caractère franchement positif.",
    steps=(0, 2, 4, 5, 7, 9, 11),
)

MINOR = Scale(
    key="mineur",
    label="Mineur",
    description="Assombrit tout le système sans le rendre triste. Bon pour les outils sérieux.",
    steps=(0, 3, 5, 7, 10),
)

LYDIAN = Scale(
    key="lydien",
    label="Lydien",
    description="La quarte augmentée ouvre et éclaire. Un peu rêveur, jamais neutre.",
    steps=(0, 2, 4, 6, 7, 9, 11),
)

HARMONIC = Scale(
    key="harmoniques",
    label="Harmoniques",
    description="Les partiels naturels d'une seule note. Très consonant, presque instrumental.",
    steps=(0, 7, 12, 16, 19, 24),
)

WHOLE_TONE = Scale(
    key="tons",
    label="Tons entiers",
    description="Six degrés équidistants, sans point d'appui. Flottant et abstrait.",
    steps=(0, 2, 4, 6, 8, 10),
)


SCALES: tuple[Scale, ...] = (
    PENTATONIC,
    MAJOR,
    MINOR,
    LYDIAN,
    HARMONIC,
    WHOLE_TONE,
)


def get_scale(key: str) -> Scale:
    """Return the scale registered under the given key.

    Args:
        key: Stable identifier of the scale.

    Returns:
        The matching scale.

    Raises:
        KeyError: If no scale is registered under that key.
    """
    for scale in SCALES:
        if scale.key == key:
            return scale

    raise KeyError(f"Unknown scale: {key}")

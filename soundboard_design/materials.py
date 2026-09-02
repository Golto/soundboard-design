"""The catalogue of sounding bodies available to the design system.

Each material is a physical model rather than a waveform: its partials,
their individual extinction times, its impact noise and its natural
duration are chosen so that the name matches what a listener actually
hears. Wood knocks and stops. Metal rings. A bubble sweeps upward.
"""

from .domain import (
    ChirpShape,
    ChirpVoice,
    FilterKind,
    FmVoice,
    Material,
    MaterialFamily,
    ModalVoice,
    NoiseVoice,
    Partial,
    Transient,
    WaveVoice,
    Waveform,
)


# ----------------------------------------------------------------
# Percussive bodies
# ----------------------------------------------------------------

WOOD = Material(
    key="bois",
    label="Bois",
    family=MaterialFamily.PERCUSSIVE,
    description=(
        "Un poc sec sur un bloc plein. Frappe sourde vers 1,2 kHz, modes "
        "inharmoniques 1 / 2,71 / 4,90 qui s'éteignent en cascade, tout est "
        "fini en une centaine de millisecondes."
    ),
    voice=ModalVoice(
        waveform=Waveform.TRIANGLE,
        partials=(
            Partial(ratio=1.0, gain=1.0, decay=1.0),
            Partial(ratio=2.71, gain=0.45, decay=0.40),
            Partial(ratio=4.90, gain=0.16, decay=0.22),
        ),
    ),
    duration_factor=0.30,
    attack_factor=0.50,
    cutoff_ratio=5.0,
    transient=Transient(tone_hz=1250.0, amount=1.5, resonance=1.0, decay_seconds=0.028),
    gain_trim=1.0,
)

MARIMBA = Material(
    key="marimba",
    label="Bois creux",
    family=MaterialFamily.PERCUSSIVE,
    description=(
        "Une lame de marimba accordée. Les modes 1 / 3,9 / 10,8 sont ceux "
        "d'une barre évidée : plus chantant que le bois plein, sans jamais "
        "traîner."
    ),
    voice=ModalVoice(
        waveform=Waveform.SINE,
        partials=(
            Partial(ratio=1.0, gain=1.0, decay=1.0),
            Partial(ratio=3.90, gain=0.35, decay=0.45),
            Partial(ratio=10.80, gain=0.12, decay=0.18),
        ),
    ),
    duration_factor=0.50,
    attack_factor=0.60,
    cutoff_ratio=4.5,
    transient=Transient(tone_hz=900.0, amount=0.70, resonance=1.2, decay_seconds=0.020),
    gain_trim=1.05,
)

PLASTIC = Material(
    key="plastique",
    label="Plastique",
    family=MaterialFamily.PERCUSSIVE,
    description=(
        "Le tac d'un boîtier qui s'encliquette. Frappe très brève et haute, "
        "corps quasi inexistant : neutre et industriel, sans résonance."
    ),
    voice=ModalVoice(
        waveform=Waveform.TRIANGLE,
        partials=(
            Partial(ratio=1.0, gain=1.0, decay=1.0),
            Partial(ratio=2.14, gain=0.50, decay=0.35),
            Partial(ratio=3.42, gain=0.28, decay=0.20),
        ),
    ),
    duration_factor=0.16,
    attack_factor=0.35,
    cutoff_ratio=8.0,
    transient=Transient(tone_hz=2900.0, amount=1.7, resonance=1.6, decay_seconds=0.012),
    gain_trim=0.95,
)

SKIN = Material(
    key="peau",
    label="Peau",
    family=MaterialFamily.PERCUSSIVE,
    description=(
        "Une membrane tendue. La hauteur plonge de deux octaves en "
        "cinquante millisecondes au moment de la frappe, puis seul le grave "
        "subsiste : la matière la plus corporelle du jeu."
    ),
    voice=ModalVoice(
        waveform=Waveform.SINE,
        partials=(
            Partial(ratio=1.0, gain=1.0, decay=1.0),
            Partial(ratio=1.59, gain=0.28, decay=0.35),
        ),
        pitch_drop=2.30,
        pitch_drop_seconds=0.05,
    ),
    duration_factor=0.60,
    attack_factor=0.70,
    cutoff_ratio=2.6,
    transient=Transient(tone_hz=420.0, amount=0.90, resonance=0.8, decay_seconds=0.035),
    gain_trim=1.0,
)


# ----------------------------------------------------------------
# Resonant bodies
# ----------------------------------------------------------------

GLASS = Material(
    key="verre",
    label="Verre",
    family=MaterialFamily.RESONANT,
    description=(
        "Une cloche de verre frappée. Modulation de fréquence au rapport "
        "3,51 : attaque claire et froide, longue résonance cristalline."
    ),
    voice=FmVoice(modulator_ratio=3.51, modulation_index=2.2),
    duration_factor=1.35,
    attack_factor=1.0,
    cutoff_ratio=9.0,
    transient=Transient(tone_hz=3600.0, amount=0.50, resonance=1.3, decay_seconds=0.018),
    gain_trim=0.95,
)

METAL = Material(
    key="metal",
    label="Métal",
    family=MaterialFamily.RESONANT,
    description=(
        "Une lame libre qui vibre. Les rapports 2,76 / 5,40 / 8,93 sont ceux "
        "d'une barre d'acier : traîne longue et brillante, à manier avec "
        "parcimonie."
    ),
    voice=ModalVoice(
        waveform=Waveform.SINE,
        partials=(
            Partial(ratio=1.0, gain=1.0, decay=1.0),
            Partial(ratio=2.76, gain=0.55, decay=0.80),
            Partial(ratio=5.40, gain=0.30, decay=0.55),
            Partial(ratio=8.93, gain=0.12, decay=0.35),
        ),
    ),
    duration_factor=1.70,
    attack_factor=0.70,
    cutoff_ratio=13.0,
    transient=Transient(tone_hz=4200.0, amount=0.45, resonance=1.4, decay_seconds=0.020),
    gain_trim=0.80,
)

# NOTE: this used to be a Karplus-Strong feedback loop. The Web Audio
# specification clamps any DelayNode inside a cycle to a full render quantum,
# so every note above roughly 340 Hz was detuned onto the same pitch and the
# loop gain was impossible to stage. The additive model below is exactly in
# tune, silent at rest, and renders identically offline.
STRING = Material(
    key="corde",
    label="Corde",
    family=MaterialFamily.RESONANT,
    description=(
        "Une corde pincée près du chevalet. Les partiels sont harmoniques, "
        "avec le creux caractéristique du cinquième dû à la position du "
        "pincement, et les aigus s'éteignent bien avant le fondamental."
    ),
    voice=ModalVoice(
        waveform=Waveform.SINE,
        partials=(
            Partial(ratio=1.0, gain=1.0, decay=1.0),
            Partial(ratio=2.002, gain=0.62, decay=0.60),
            Partial(ratio=3.008, gain=0.34, decay=0.42),
            Partial(ratio=4.020, gain=0.16, decay=0.28),
            Partial(ratio=6.050, gain=0.09, decay=0.16),
        ),
    ),
    duration_factor=1.05,
    attack_factor=0.30,
    cutoff_ratio=5.0,
    transient=Transient(tone_hz=1600.0, amount=0.30, resonance=1.2, decay_seconds=0.010),
    gain_trim=0.85,
)


# ----------------------------------------------------------------
# Liquid bodies
# ----------------------------------------------------------------

BUBBLE = Material(
    key="bulle",
    label="Bulle",
    family=MaterialFamily.LIQUID,
    description=(
        "Une bulle d'air qui remonte. La fréquence monte pendant toute la "
        "durée du son, comme une poche d'air dont le rayon diminue : "
        "quatre-vingts millisecondes, presque aucune frappe."
    ),
    voice=ChirpVoice(
        waveform=Waveform.SINE,
        shape=ChirpShape.RISE,
        depth=2.60,
        time_ratio=0.85,
    ),
    duration_factor=0.22,
    attack_factor=0.80,
    cutoff_ratio=7.0,
    transient=Transient(tone_hz=1800.0, amount=0.12, resonance=1.0, decay_seconds=0.008),
    gain_trim=1.15,
)

# NOTE: the droplet arrives on its scale degree instead of leaving from it.
# It keeps ringing after the sweep, so the pitch a listener retains is the
# one it settles on. Sweeping away from the degree meant the audible pitch
# belonged to no degree at all, and it clashed with everything else.
DROPLET = Material(
    key="goutte",
    label="Goutte",
    family=MaterialFamily.LIQUID,
    description=(
        "Une goutte qui tombe dans l'eau. La hauteur monte en soixante "
        "millisecondes jusqu'à la note, puis celle-ci résonne et s'éteint "
        "lentement : ce ploc suspendu est ce qui la distingue de la bulle."
    ),
    voice=ChirpVoice(
        waveform=Waveform.SINE,
        shape=ChirpShape.RISE_TO,
        depth=2.20,
        time_ratio=0.26,
    ),
    duration_factor=0.55,
    attack_factor=0.70,
    cutoff_ratio=6.0,
    transient=Transient(tone_hz=2000.0, amount=0.22, resonance=1.5, decay_seconds=0.008),
    gain_trim=1.0,
)


# ----------------------------------------------------------------
# Organic bodies
# ----------------------------------------------------------------

# NOTE: the level is held across the sweep rather than decaying from the
# first millisecond. Without the hold, all the energy sits at the bottom of
# the arc and the sweep happens in silence, which is why the syllable read
# as a dull blip instead of a call.
BIRD = Material(
    key="oiseau",
    label="Oiseau",
    family=MaterialFamily.ORGANIC,
    description=(
        "Un cuicui de deux syllabes, deux octaves au-dessus du reste du "
        "système. Chaque syllabe dure soixante millisecondes, monte d'une "
        "octave et redescend plus bas qu'elle n'est partie, le niveau tenu "
        "tout du long ; la seconde est plus basse et plus discrète, comme "
        "dans un vrai appel."
    ),
    voice=ChirpVoice(
        waveform=Waveform.SINE,
        shape=ChirpShape.ARCH,
        depth=2.40,
        time_ratio=0.95,
        hold_ratio=0.55,
        harmonic_gain=0.22,
        vibrato_hz=55.0,
        vibrato_cents=12.0,
        repeats=2,
        repeat_gap=0.45,
    ),
    duration_factor=0.15,
    attack_factor=3.0,
    cutoff_ratio=10.0,
    transient=Transient(tone_hz=5000.0, amount=0.04, resonance=1.2, decay_seconds=0.005),
    gain_trim=0.85,
    octave_shift=2,
)

PAPER = Material(
    key="papier",
    label="Papier",
    family=MaterialFamily.ORGANIC,
    description=(
        "Un froissement bref. Pas de hauteur stable : du bruit filtré dont "
        "la bande suit quand même la gamme, avec un grain irrégulier. Parfait "
        "pour les balayages et les disparitions."
    ),
    voice=NoiseVoice(
        filter_kind=FilterKind.BANDPASS,
        center_ratio=5.0,
        resonance=0.9,
        sweep=0.40,
        density=0.70,
    ),
    duration_factor=0.55,
    attack_factor=3.0,
    cutoff_ratio=6.0,
    transient=Transient(tone_hz=5000.0, amount=0.25, resonance=0.8, decay_seconds=0.012),
    gain_trim=1.10,
)

AIR = Material(
    key="air",
    label="Air",
    family=MaterialFamily.ORGANIC,
    description=(
        "Un sinus et du souffle, avec une attaque de trente millisecondes. "
        "Rien ne cogne, le son s'installe : la matière la plus discrète du "
        "jeu."
    ),
    voice=WaveVoice(
        waveform=Waveform.SINE,
        partial_ratio=2.0,
        partial_gain=0.14,
        breath=0.50,
    ),
    duration_factor=1.15,
    attack_factor=9.0,
    cutoff_ratio=6.0,
    transient=Transient(tone_hz=2200.0, amount=0.05, resonance=0.9, decay_seconds=0.020),
    gain_trim=1.20,
)


# ----------------------------------------------------------------
# Synthetic bodies
# ----------------------------------------------------------------

CHIP = Material(
    key="puce",
    label="Puce",
    family=MaterialFamily.SYNTHETIC,
    description=(
        "Une onde carrée filtrée, franchement électronique. Aucune "
        "prétention matérielle : c'est le son d'une machine qui répond."
    ),
    voice=WaveVoice(
        waveform=Waveform.SQUARE,
        partial_ratio=2.0,
        partial_gain=0.12,
    ),
    duration_factor=0.60,
    attack_factor=0.40,
    cutoff_ratio=3.6,
    transient=Transient(tone_hz=2700.0, amount=0.30, resonance=1.0, decay_seconds=0.020),
    gain_trim=0.85,
)


MATERIALS: tuple[Material, ...] = (
    WOOD,
    MARIMBA,
    PLASTIC,
    SKIN,
    GLASS,
    METAL,
    STRING,
    BUBBLE,
    DROPLET,
    BIRD,
    PAPER,
    AIR,
    CHIP,
)


def get_material(key: str) -> Material:
    """Return the material registered under the given key.

    Args:
        key: Stable identifier of the material.

    Returns:
        The matching material.

    Raises:
        KeyError: If no material is registered under that key.
    """
    for material in MATERIALS:
        if material.key == key:
            return material

    raise KeyError(f"Unknown material: {key}")

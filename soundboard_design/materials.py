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
    StringVoice,
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

STRING = Material(
    key="corde",
    label="Corde",
    family=MaterialFamily.RESONANT,
    description=(
        "Une corde pincée, synthétisée par une ligne à retard bouclée. Un "
        "souffle de six millisecondes excite la boucle et le filtre éteint "
        "les aigus en premier, exactement comme une vraie corde."
    ),
    voice=StringVoice(excitation_seconds=0.006, damping_ratio=7.0, max_frequency=2200.0),
    duration_factor=1.10,
    attack_factor=0.40,
    cutoff_ratio=6.0,
    transient=Transient(tone_hz=2400.0, amount=0.35, resonance=1.0, decay_seconds=0.012),
    gain_trim=0.90,
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

DROPLET = Material(
    key="goutte",
    label="Goutte",
    family=MaterialFamily.LIQUID,
    description=(
        "Une goutte qui tombe dans l'eau. Même montée que la bulle mais plus "
        "ample et plus rapide, suivie d'une petite résonance qui reste dans "
        "la pièce."
    ),
    voice=ChirpVoice(
        waveform=Waveform.SINE,
        shape=ChirpShape.RISE,
        depth=3.40,
        time_ratio=0.45,
        tail_gain=0.25,
    ),
    duration_factor=0.40,
    attack_factor=0.80,
    cutoff_ratio=8.0,
    transient=Transient(tone_hz=2600.0, amount=0.30, resonance=1.4, decay_seconds=0.010),
    gain_trim=1.05,
)


# ----------------------------------------------------------------
# Organic bodies
# ----------------------------------------------------------------

BIRD = Material(
    key="oiseau",
    label="Oiseau",
    family=MaterialFamily.ORGANIC,
    description=(
        "Un petit cri d'oiseau. La hauteur monte puis redescend en arc, avec "
        "un vibrato à 24 Hz qui lui donne son côté vivant. À réserver aux "
        "événements rares : c'est un son qui attire l'oreille."
    ),
    voice=ChirpVoice(
        waveform=Waveform.SINE,
        shape=ChirpShape.ARCH,
        depth=1.90,
        time_ratio=0.80,
        vibrato_hz=24.0,
        vibrato_cents=40.0,
    ),
    duration_factor=0.45,
    attack_factor=1.20,
    cutoff_ratio=10.0,
    transient=Transient(tone_hz=3000.0, amount=0.08, resonance=1.2, decay_seconds=0.008),
    gain_trim=1.0,
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

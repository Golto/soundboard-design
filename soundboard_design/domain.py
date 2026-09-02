"""Core domain model for the soundboard design system.

Every sound in the system is described declaratively here: a material
(how a body vibrates), a token (which degrees of the scale are played and
when), and a palette (the global settings applied to all tokens). The
browser engine is a pure interpreter of these structures, so this module
is the single source of truth for the sound design.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar


# NOTE: json payloads are arbitrarily nested by nature. A recursive alias keeps
# the shape honest without falling back to Any.
type JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


# ----------------------------------------------------------------
# Enumerations
# ----------------------------------------------------------------


class Waveform(Enum):
    """Oscillator shapes available in the Web Audio API."""

    SINE = "sine"
    TRIANGLE = "triangle"
    SAWTOOTH = "sawtooth"
    SQUARE = "square"


class MaterialEngine(Enum):
    """Synthesis engine used to render a material."""

    MODAL = "modal"
    FM = "fm"
    CHIRP = "chirp"
    NOISE = "noise"
    WAVE = "wave"


class MaterialFamily(Enum):
    """Perceptual grouping used to organise materials in the interface."""

    PERCUSSIVE = "percussif"
    RESONANT = "résonant"
    LIQUID = "liquide"
    ORGANIC = "organique"
    SYNTHETIC = "synthétique"


class ChirpShape(Enum):
    """Direction of the pitch sweep, relative to the note being played.

    Which end of the sweep lands on the scale degree matters. The pitch a
    listener actually hears is the one the sweep settles on, so a body that
    keeps ringing after its sweep must arrive on the note rather than leave
    from it, otherwise it plays a frequency that belongs to no degree.
    """

    RISE = "rise"
    RISE_TO = "rise_to"
    FALL = "fall"
    ARCH = "arch"


class FilterKind(Enum):
    """Filter type applied to noise materials."""

    LOWPASS = "lowpass"
    BANDPASS = "bandpass"
    HIGHPASS = "highpass"


class Temperament(Enum):
    """Tuning system used to turn a scale degree into a frequency."""

    JUST = "just"
    EQUAL = "equal"


class TokenBehaviour(Enum):
    """How a token is triggered, which changes how the engine schedules it.

    ONE_SHOT tokens fire once. REPEATABLE tokens may fire many times per
    second and receive pitch and gain variation so they do not sound
    mechanical. SUSTAINED tokens are held open by the interface and driven
    by a progress value until they are committed or cancelled.
    """

    ONE_SHOT = "one_shot"
    REPEATABLE = "repeatable"
    SUSTAINED = "sustained"


# ----------------------------------------------------------------
# Voice specifications
# ----------------------------------------------------------------


@dataclass(frozen=True)
class Partial:
    """One vibration mode of a modal body.

    Args:
        ratio: Frequency of the mode relative to the fundamental. Values
            that are not whole numbers produce inharmonic, physical timbres.
        gain: Level of the mode relative to the fundamental.
        decay: Extinction time of the mode as a fraction of the voice
            duration. Higher modes usually die out faster.
    """

    ratio: float
    gain: float
    decay: float

    def to_payload(self) -> dict[str, JsonValue]:
        return {"ratio": self.ratio, "gain": self.gain, "decay": self.decay}


@dataclass(frozen=True)
class ModalVoice:
    """A struck or plucked body described by its vibration modes.

    Args:
        waveform: Shape of every mode oscillator.
        partials: Vibration modes, fundamental first.
        pitch_drop: Multiplier applied to the fundamental at the moment of
            impact, sliding back to 1 over pitch_drop_seconds. A value above
            1 reproduces the pitch dive of a struck membrane.
        pitch_drop_seconds: Duration of that slide.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.MODAL

    waveform: Waveform
    partials: tuple[Partial, ...]
    pitch_drop: float = 1.0
    pitch_drop_seconds: float = 0.05

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "waveform": self.waveform.value,
            "partials": [partial.to_payload() for partial in self.partials],
            "pitchDrop": self.pitch_drop,
            "pitchDropSeconds": self.pitch_drop_seconds,
        }


@dataclass(frozen=True)
class FmVoice:
    """Two-operator frequency modulation, used for bell-like bodies.

    Args:
        modulator_ratio: Modulator frequency relative to the carrier. Values
            far from whole numbers give metallic, glassy spectra.
        modulation_index: Depth of modulation at the attack, decaying with
            the note.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.FM

    modulator_ratio: float
    modulation_index: float

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "modulatorRatio": self.modulator_ratio,
            "modulationIndex": self.modulation_index,
        }


@dataclass(frozen=True)
class ChirpVoice:
    """A sweeping tone, used for bubbles, droplets and bird calls.

    A rising sweep over a very short window is what makes a bubble read as
    a bubble: the frequency of a collapsing air pocket climbs as its radius
    shrinks.

    The amplitude envelope decides which part of the sweep is audible. With
    no hold, the level collapses immediately and only the departure pitch
    is heard, which is right for a bubble and wrong for a bird call: a call
    needs its level held across the whole arc, otherwise the sweep happens
    in silence and the syllable reads as a dull blip.

    Args:
        waveform: Shape of the sweeping oscillator.
        shape: Direction of the sweep, relative to the note.
        depth: Frequency ratio between the two ends of the sweep.
        time_ratio: Fraction of the voice duration spent sweeping.
        hold_ratio: Fraction of the duration during which the level stays
            up before the release begins. Zero gives a plain decay.
        harmonic_gain: Level of a second oscillator tracking the sweep an
            octave above. A pure sine whistles; a touch of octave gives the
            voice a throat.
        vibrato_hz: Rate of an optional pitch vibrato, 0 to disable.
        vibrato_cents: Depth of that vibrato.
        repeats: Number of syllables. Each one is quieter and slightly
            lower than the last, which is how a real call is phrased.
        repeat_gap: Silence between syllables, as a fraction of the
            syllable duration.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.CHIRP

    waveform: Waveform
    shape: ChirpShape
    depth: float
    time_ratio: float = 0.7
    hold_ratio: float = 0.0
    harmonic_gain: float = 0.0
    vibrato_hz: float = 0.0
    vibrato_cents: float = 0.0
    repeats: int = 1
    repeat_gap: float = 0.0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "waveform": self.waveform.value,
            "shape": self.shape.value,
            "depth": self.depth,
            "timeRatio": self.time_ratio,
            "holdRatio": self.hold_ratio,
            "harmonicGain": self.harmonic_gain,
            "vibratoHz": self.vibrato_hz,
            "vibratoCents": self.vibrato_cents,
            "repeats": self.repeats,
            "repeatGap": self.repeat_gap,
        }


@dataclass(frozen=True)
class NoiseVoice:
    """Filtered noise with no stable pitch, used for paper and friction.

    Args:
        filter_kind: Filter applied to the noise source.
        center_ratio: Filter frequency relative to the note frequency, so
            that even an unpitched texture follows the scale.
        resonance: Filter Q.
        sweep: Ratio between the final and initial filter frequency.
        density: Amount of amplitude flutter, which turns a smooth hiss
            into a granular rustle.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.NOISE

    filter_kind: FilterKind
    center_ratio: float
    resonance: float
    sweep: float = 1.0
    density: float = 0.0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "filterKind": self.filter_kind.value,
            "centerRatio": self.center_ratio,
            "resonance": self.resonance,
            "sweep": self.sweep,
            "density": self.density,
        }


@dataclass(frozen=True)
class WaveVoice:
    """A plain filtered oscillator pair, deliberately electronic.

    Args:
        waveform: Shape of both oscillators.
        partial_ratio: Frequency of the second oscillator relative to the
            first.
        partial_gain: Level of the second oscillator.
        breath: Amount of steady filtered noise mixed under the tone.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.WAVE

    waveform: Waveform
    partial_ratio: float = 2.0
    partial_gain: float = 0.12
    breath: float = 0.0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "waveform": self.waveform.value,
            "partialRatio": self.partial_ratio,
            "partialGain": self.partial_gain,
            "breath": self.breath,
        }


type VoiceSpec = ModalVoice | FmVoice | ChirpVoice | NoiseVoice | WaveVoice


# ----------------------------------------------------------------
# Materials
# ----------------------------------------------------------------


@dataclass(frozen=True)
class Transient:
    """The impact noise that precedes the body of a sound.

    The transient is what the ear uses to identify a material. A wooden
    knock and a plastic click share almost the same body: they differ
    mostly here.

    Args:
        tone_hz: Centre frequency of the impact.
        amount: Level multiplier applied on top of each note transient value.
        resonance: Q of the bandpass shaping the impact.
        decay_seconds: Extinction time of the impact.
    """

    tone_hz: float
    amount: float
    resonance: float = 1.0
    decay_seconds: float = 0.025

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "toneHz": self.tone_hz,
            "amount": self.amount,
            "resonance": self.resonance,
            "decaySeconds": self.decay_seconds,
        }


@dataclass(frozen=True)
class Material:
    """A sounding body, independent of any note it plays.

    A material owns its own natural duration: wood dies out in a tenth of a
    second whatever the palette says, and metal rings for a second. The
    palette hold setting multiplies that value rather than replacing it, so
    the relative character of the materials survives every global change.

    Args:
        key: Stable identifier used by the interface and the exports.
        label: French display name.
        family: Perceptual group used to sort materials in the interface.
        description: One sentence explaining what the listener will hear.
        voice: Engine-specific synthesis parameters.
        duration_factor: Multiplier applied to every note duration.
        attack_factor: Multiplier applied to every note attack time.
        cutoff_ratio: Low-pass cutoff relative to the note frequency.
        transient: Impact noise description.
        gain_trim: Level correction so that materials match each other.
        octave_shift: Whole octaves added to every note. Bodies that only
            exist in one register, such as a bird call, use this to sit
            where they belong; since an octave belongs to every scale, the
            harmony of the system is preserved.
    """

    key: str
    label: str
    family: MaterialFamily
    description: str
    voice: VoiceSpec
    duration_factor: float
    attack_factor: float
    cutoff_ratio: float
    transient: Transient
    gain_trim: float = 1.0
    octave_shift: int = 0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "key": self.key,
            "label": self.label,
            "family": self.family.value,
            "description": self.description,
            "engine": type(self.voice).engine.value,
            "voice": self.voice.to_payload(),
            "durationFactor": self.duration_factor,
            "attackFactor": self.attack_factor,
            "cutoffRatio": self.cutoff_ratio,
            "transient": self.transient.to_payload(),
            "gainTrim": self.gain_trim,
            "octaveShift": self.octave_shift,
        }


# ----------------------------------------------------------------
# Tokens
# ----------------------------------------------------------------


@dataclass(frozen=True)
class Note:
    """One note inside a token, expressed as a scale degree.

    Degrees rather than frequencies are what keeps the whole system in
    tune: changing the root or the scale rewrites every token at once.

    Args:
        degree: Index in the current scale. Negative values and values
            beyond the scale length wrap into lower and higher octaves.
        offset_seconds: Delay from the start of the token.
        duration_seconds: Base duration, before the material and palette
            factors are applied.
        gain: Level of this note, from 0 to 1.
        transient: Amount of impact noise, from 0 to about 1.5.
        brightness: Local multiplier on the palette brightness.
        attack_seconds: Base attack time before material and weight factors.
    """

    degree: int
    offset_seconds: float = 0.0
    duration_seconds: float = 0.35
    gain: float = 0.6
    transient: float = 0.5
    brightness: float = 1.0
    attack_seconds: float = 0.003

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "degree": self.degree,
            "offsetSeconds": self.offset_seconds,
            "durationSeconds": self.duration_seconds,
            "gain": self.gain,
            "transient": self.transient,
            "brightness": self.brightness,
            "attackSeconds": self.attack_seconds,
        }


@dataclass(frozen=True)
class SoundToken:
    """A named sound bound to one interaction of the design system.

    Args:
        token_id: Dotted identifier used in code and in the exports.
        label: French display name.
        usage: One sentence telling a designer when to fire this token.
        behaviour: How the token is triggered.
        notes: Notes making up the sound, in play order.
        tracks_value: When true, the interface adds a degree offset derived
            from the widget value, so the pitch follows the slider position
            or the carousel index.
        variation: Amount of random pitch and level variation applied on
            each trigger, from 0 to 1. Only meaningful for repeatable
            tokens, where identical repeats sound mechanical.
    """

    token_id: str
    label: str
    usage: str
    behaviour: TokenBehaviour
    notes: tuple[Note, ...]
    tracks_value: bool = False
    variation: float = 0.0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "tokenId": self.token_id,
            "label": self.label,
            "usage": self.usage,
            "behaviour": self.behaviour.value,
            "notes": [note.to_payload() for note in self.notes],
            "tracksValue": self.tracks_value,
            "variation": self.variation,
        }


@dataclass(frozen=True)
class Category:
    """A group of tokens covering one family of interactions.

    Args:
        key: Stable identifier.
        label: French display name.
        description: One sentence stating which interactions belong here.
        tokens: Tokens in display order.
    """

    key: str
    label: str
    description: str
    tokens: tuple[SoundToken, ...]

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "key": self.key,
            "label": self.label,
            "description": self.description,
            "tokens": [token.to_payload() for token in self.tokens],
        }


# ----------------------------------------------------------------
# Scales and palettes
# ----------------------------------------------------------------


@dataclass(frozen=True)
class Scale:
    """An ordered set of semitone offsets repeated at every octave.

    Args:
        key: Stable identifier.
        label: French display name.
        description: One sentence on the mood the scale carries.
        steps: Semitone offsets from the root, ascending.
    """

    key: str
    label: str
    description: str
    steps: tuple[int, ...]

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "key": self.key,
            "label": self.label,
            "description": self.description,
            "steps": list(self.steps),
        }


@dataclass(frozen=True)
class Palette:
    """The global settings applied to every token of the system.

    Args:
        material_key: Key of the sounding body in use.
        scale_key: Key of the scale in use.
        root_hz: Frequency of scale degree zero.
        temperament: Tuning system used to derive the other degrees.
        grain: Roughness, from perfectly smooth to saturated and noisy.
        weight: Perceived mass, from weightless to heavy and slow.
        brightness: Multiplier on the low-pass cutoff of every note.
        hold: Multiplier on the natural duration of the material.
        space: Reverberation send level shared by every token.
        level: Bus gain before the compressor.
    """

    material_key: str
    scale_key: str
    root_hz: float
    temperament: Temperament
    grain: float
    weight: float
    brightness: float
    hold: float
    space: float
    level: float = 0.8

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "materialKey": self.material_key,
            "scaleKey": self.scale_key,
            "rootHz": self.root_hz,
            "temperament": self.temperament.value,
            "grain": self.grain,
            "weight": self.weight,
            "brightness": self.brightness,
            "hold": self.hold,
            "space": self.space,
            "level": self.level,
        }


@dataclass(frozen=True)
class Preset:
    """A named palette with an explanation of the product it suits.

    Args:
        key: Stable identifier.
        label: French display name.
        summary: One sentence describing the feel and the intended product.
        palette: The settings applied when the preset is selected.
    """

    key: str
    label: str
    summary: str
    palette: Palette

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "key": self.key,
            "label": self.label,
            "summary": self.summary,
            "palette": self.palette.to_payload(),
        }


@dataclass(frozen=True)
class DesignSystem:
    """The complete payload handed to the browser engine.

    Args:
        version: Version of the sound system definition.
        materials: Every available sounding body.
        scales: Every available scale.
        categories: Every token, grouped by interaction family.
        presets: Ready-made palettes.
        default_preset_key: Preset applied when the interface starts.
        just_ratios: Frequency ratios for the twelve semitones, used by the
            just temperament.
    """

    version: str
    materials: tuple[Material, ...]
    scales: tuple[Scale, ...]
    categories: tuple[Category, ...]
    presets: tuple[Preset, ...]
    default_preset_key: str
    just_ratios: tuple[float, ...] = field(default_factory=tuple)

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "version": self.version,
            "materials": [material.to_payload() for material in self.materials],
            "scales": [scale.to_payload() for scale in self.scales],
            "categories": [category.to_payload() for category in self.categories],
            "presets": [preset.to_payload() for preset in self.presets],
            "defaultPresetKey": self.default_preset_key,
            "justRatios": list(self.just_ratios),
        }

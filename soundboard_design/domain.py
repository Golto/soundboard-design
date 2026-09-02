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
    STRING = "string"
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
    """Direction of the pitch sweep for chirp materials."""

    RISE = "rise"
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
    """A struck body described by its vibration modes.

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
class StringVoice:
    """Plucked string built as a Karplus-Strong feedback delay line.

    Args:
        excitation_seconds: Length of the noise burst that excites the loop.
        damping_ratio: Cutoff of the loop filter relative to the note
            frequency. Lower values dampen the high modes faster and give a
            duller, shorter string.
        max_frequency: Upper frequency bound. Above it the delay line gets
            too short to be stable, so the note is folded down an octave.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.STRING

    excitation_seconds: float = 0.006
    damping_ratio: float = 7.0
    max_frequency: float = 2200.0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "excitationSeconds": self.excitation_seconds,
            "dampingRatio": self.damping_ratio,
            "maxFrequency": self.max_frequency,
        }


@dataclass(frozen=True)
class ChirpVoice:
    """A sweeping tone, used for bubbles, droplets and bird calls.

    A rising sweep over a very short window is what makes a bubble read as
    a bubble: the frequency of a collapsing air pocket climbs as its radius
    shrinks.

    Args:
        waveform: Shape of the sweeping oscillator.
        shape: Direction of the sweep.
        depth: Frequency multiplier reached at the far end of the sweep.
        time_ratio: Fraction of the voice duration spent sweeping.
        vibrato_hz: Rate of an optional pitch vibrato, 0 to disable.
        vibrato_cents: Depth of that vibrato.
        tail_gain: Level of a short resonant tail left once the sweep ends.
    """

    engine: ClassVar[MaterialEngine] = MaterialEngine.CHIRP

    waveform: Waveform
    shape: ChirpShape
    depth: float
    time_ratio: float = 0.7
    vibrato_hz: float = 0.0
    vibrato_cents: float = 0.0
    tail_gain: float = 0.0

    def to_payload(self) -> dict[str, JsonValue]:
        return {
            "waveform": self.waveform.value,
            "shape": self.shape.value,
            "depth": self.depth,
            "timeRatio": self.time_ratio,
            "vibratoHz": self.vibrato_hz,
            "vibratoCents": self.vibrato_cents,
            "tailGain": self.tail_gain,
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


type VoiceSpec = ModalVoice | FmVoice | StringVoice | ChirpVoice | NoiseVoice | WaveVoice


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

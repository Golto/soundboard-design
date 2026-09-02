"""Assembly and validation of the complete design system.

The browser trusts this payload entirely, so every cross reference is
checked here rather than in the interface: a preset that points at a
material which no longer exists must fail at startup, not silently
produce silence.
"""

from .catalog import CATEGORIES, iter_tokens
from .domain import DesignSystem, JsonValue, TokenBehaviour
from .materials import MATERIALS
from .presets import DEFAULT_PRESET_KEY, PRESETS
from .scales import JUST_RATIOS, SCALES

SYSTEM_VERSION = "1.0.0"


def validate_design_system(system: DesignSystem) -> None:
    """Check every cross reference and structural invariant of the system.

    Args:
        system: The assembled design system to check.

    Raises:
        ValueError: If a token identifier is duplicated, a preset points at
            an unknown material or scale, the default preset is missing, or
            a sustained token does not carry exactly one note.
    """
    material_keys = {material.key for material in system.materials}
    scale_keys = {scale.key for scale in system.scales}
    preset_keys = {preset.key for preset in system.presets}

    seen_token_ids: set[str] = set()
    for category in system.categories:
        for token in category.tokens:
            if token.token_id in seen_token_ids:
                raise ValueError(f"Duplicate token identifier: {token.token_id}")
            seen_token_ids.add(token.token_id)

            if not token.notes:
                raise ValueError(f"Token has no notes: {token.token_id}")

            # NOTE: a sustained voice is held open and driven by a progress
            # value, so a second note would have no moment at which to start.
            if token.behaviour is TokenBehaviour.SUSTAINED and len(token.notes) != 1:
                raise ValueError(
                    f"Sustained token must carry exactly one note: {token.token_id}"
                )

    for preset in system.presets:
        if preset.palette.material_key not in material_keys:
            raise ValueError(
                f"Preset {preset.key} points at unknown material "
                f"{preset.palette.material_key}"
            )
        if preset.palette.scale_key not in scale_keys:
            raise ValueError(
                f"Preset {preset.key} points at unknown scale {preset.palette.scale_key}"
            )

    if system.default_preset_key not in preset_keys:
        raise ValueError(f"Unknown default preset: {system.default_preset_key}")

    if len(system.just_ratios) != 12:
        raise ValueError(
            f"Just intonation table must hold 12 ratios, got {len(system.just_ratios)}"
        )


def build_design_system() -> DesignSystem:
    """Assemble the design system from the module level definitions.

    Returns:
        A validated design system ready to be serialized.

    Raises:
        ValueError: If the definitions are inconsistent.
    """
    system = DesignSystem(
        version=SYSTEM_VERSION,
        materials=MATERIALS,
        scales=SCALES,
        categories=CATEGORIES,
        presets=PRESETS,
        default_preset_key=DEFAULT_PRESET_KEY,
        just_ratios=JUST_RATIOS,
    )
    validate_design_system(system)
    return system


def build_design_system_payload() -> dict[str, JsonValue]:
    """Assemble the design system and serialize it for the browser.

    Returns:
        A JSON-ready mapping describing materials, scales, tokens and presets.

    Raises:
        ValueError: If the definitions are inconsistent.
    """
    return build_design_system().to_payload()


def count_tokens() -> int:
    """Return the number of tokens defined across every category.

    Returns:
        The total token count.
    """
    return len(iter_tokens())

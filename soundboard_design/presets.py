"""Ready-made palettes, named after the product they suit.

A preset is a complete answer to the question "what should this product
sound like", not a collection of settings. Each one names a kind of
product and states the trade-off it makes, so that picking one is a design
decision rather than a lucky draw.
"""

from .domain import Palette, Preset, Temperament


QUIET = Preset(
    key="discret",
    label="Discret",
    summary=(
        "Presque inaudible, pour un outil de travail où le son ne doit jamais "
        "interrompre. Souffle aérien, aigu, sans frappe."
    ),
    palette=Palette(
        material_key="air",
        scale_key="pentatonique",
        root_hz=740.0,
        temperament=Temperament.JUST,
        grain=0.0,
        weight=0.05,
        brightness=0.85,
        hold=0.75,
        space=0.14,
    ),
)

TACTILE = Preset(
    key="tactile",
    label="Tactile",
    summary=(
        "Un poc de bois sec à chaque geste. Chaque action a une réponse "
        "physique immédiate, rien ne traîne."
    ),
    palette=Palette(
        material_key="bois",
        scale_key="pentatonique",
        root_hz=466.0,
        temperament=Temperament.EQUAL,
        grain=0.25,
        weight=0.25,
        brightness=1.0,
        hold=1.0,
        space=0.05,
    ),
)

BUBBLES = Preset(
    key="bulles",
    label="Bulles",
    summary=(
        "Léger et ludique. Des bulles qui remontent, très courtes, pour un "
        "produit grand public qui assume d'être agréable."
    ),
    palette=Palette(
        material_key="bulle",
        scale_key="pentatonique",
        root_hz=392.0,
        temperament=Temperament.JUST,
        grain=0.0,
        weight=0.15,
        brightness=1.15,
        hold=1.0,
        space=0.20,
    ),
)

NATURE = Preset(
    key="nature",
    label="Nature",
    summary=(
        "Des cuicuis de deux syllabes sur une gamme ouverte. Chaleureux et "
        "vivant, mais à réserver aux interfaces peu sonorisées : ce timbre "
        "attire l'oreille à chaque fois."
    ),
    palette=Palette(
        material_key="oiseau",
        scale_key="lydien",
        root_hz=392.0,
        temperament=Temperament.JUST,
        grain=0.05,
        weight=0.08,
        brightness=1.10,
        hold=0.90,
        space=0.24,
    ),
)

GLASSHOUSE = Preset(
    key="verre",
    label="Verre",
    summary=(
        "Cristallin et haut de gamme. Longues résonances, peu de gestes "
        "sonorisés, chaque son compte."
    ),
    palette=Palette(
        material_key="verre",
        scale_key="pentatonique",
        root_hz=660.0,
        temperament=Temperament.JUST,
        grain=0.05,
        weight=0.15,
        brightness=1.25,
        hold=1.0,
        space=0.30,
    ),
)

CASING = Preset(
    key="plastique",
    label="Plastique",
    summary=(
        "Le clic net d'un boîtier qui s'encliquette. Neutre, industriel, sans "
        "aucune résonance : le choix sûr pour une interface dense."
    ),
    palette=Palette(
        material_key="plastique",
        scale_key="mineur",
        root_hz=523.0,
        temperament=Temperament.EQUAL,
        grain=0.15,
        weight=0.12,
        brightness=1.10,
        hold=1.0,
        space=0.04,
    ),
)

WORKSHOP = Preset(
    key="atelier",
    label="Atelier",
    summary=(
        "Corde pincée dans le médium, très peu de grain. Chaud et artisanal, "
        "pour un outil créatif qui veut se sentir manufacturé."
    ),
    palette=Palette(
        material_key="corde",
        scale_key="majeur",
        root_hz=294.0,
        temperament=Temperament.JUST,
        grain=0.18,
        weight=0.30,
        brightness=0.80,
        hold=1.0,
        space=0.16,
    ),
)

ARCADE = Preset(
    key="arcade",
    label="Arcade",
    summary=(
        "Bips carrés assumés. Pour un produit qui joue la carte du jeu et "
        "n'essaie pas de passer pour un objet."
    ),
    palette=Palette(
        material_key="puce",
        scale_key="mineur",
        root_hz=587.0,
        temperament=Temperament.EQUAL,
        grain=0.50,
        weight=0.15,
        brightness=1.50,
        hold=0.90,
        space=0.0,
    ),
)

CINEMA = Preset(
    key="cinema",
    label="Cinéma",
    summary=(
        "Grave et lourd, sur peau tendue. Transitions longues et rares, pour "
        "un lecteur vidéo ou une installation en plein écran."
    ),
    palette=Palette(
        material_key="peau",
        scale_key="harmoniques",
        root_hz=220.0,
        temperament=Temperament.JUST,
        grain=0.20,
        weight=0.85,
        brightness=0.70,
        hold=1.35,
        space=0.30,
    ),
)

FOUNDRY = Preset(
    key="fonderie",
    label="Fonderie",
    summary=(
        "Métal grenu et pesant. Un poste de pilotage industriel, où le son "
        "doit passer au-dessus du bruit ambiant."
    ),
    palette=Palette(
        material_key="metal",
        scale_key="mineur",
        root_hz=262.0,
        temperament=Temperament.EQUAL,
        grain=0.65,
        weight=0.70,
        brightness=0.95,
        hold=1.05,
        space=0.16,
    ),
)

PAPERBACK = Preset(
    key="papier",
    label="Papier",
    summary=(
        "Des froissements sans hauteur stable. Pour une liseuse ou un outil "
        "de lecture, où une note franche serait déplacée."
    ),
    palette=Palette(
        material_key="papier",
        scale_key="tons",
        root_hz=440.0,
        temperament=Temperament.EQUAL,
        grain=0.30,
        weight=0.20,
        brightness=1.05,
        hold=0.90,
        space=0.12,
    ),
)


PRESETS: tuple[Preset, ...] = (
    QUIET,
    TACTILE,
    BUBBLES,
    NATURE,
    GLASSHOUSE,
    CASING,
    WORKSHOP,
    ARCADE,
    CINEMA,
    FOUNDRY,
    PAPERBACK,
)

DEFAULT_PRESET_KEY = "tactile"


def get_preset(key: str) -> Preset:
    """Return the preset registered under the given key.

    Args:
        key: Stable identifier of the preset.

    Returns:
        The matching preset.

    Raises:
        KeyError: If no preset is registered under that key.
    """
    for preset in PRESETS:
        if preset.key == key:
            return preset

    raise KeyError(f"Unknown preset: {key}")

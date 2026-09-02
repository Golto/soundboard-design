"""The token catalogue, grouped by interaction family.

Tokens are named after the interaction a designer is sonifying, not after
the sound they produce, so that the same token keeps its meaning when the
palette changes. Degrees are relative to the current scale: rising
sequences read as opening or confirming, falling ones as closing or
undoing, and repeated degrees as insisting.
"""

from .domain import Category, Note, SoundToken, TokenBehaviour


# ----------------------------------------------------------------
# Buttons and presses
# ----------------------------------------------------------------

BUTTONS = Category(
    key="boutons",
    label="Boutons et appuis",
    description="Tout ce qui répond à un doigt qui touche puis relâche.",
    tokens=(
        SoundToken(
            token_id="button.tap",
            label="Appui",
            usage="Le retour neutre de n'importe quel bouton. Le son le plus joué du système.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=0, duration_seconds=0.42, gain=0.85, transient=1.0),),
            variation=0.25,
        ),
        SoundToken(
            token_id="button.primary",
            label="Action principale",
            usage="Le bouton qui fait avancer l'écran. Deux notes qui montent, légèrement plus longues.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.45, gain=0.80, transient=0.90),
                Note(degree=2, offset_seconds=0.050, duration_seconds=0.60, gain=0.70, transient=0.20),
            ),
        ),
        SoundToken(
            token_id="button.secondary",
            label="Action secondaire",
            usage="Annuler, fermer, revenir. Plus court et plus sombre que l'action principale.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(Note(degree=0, duration_seconds=0.32, gain=0.50, transient=0.60, brightness=0.70),),
        ),
        SoundToken(
            token_id="button.hover",
            label="Survol",
            usage="Le curseur entre dans la zone cliquable. À la limite de l'audible, sinon c'est insupportable.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=4, duration_seconds=0.20, gain=0.16, transient=0.25, brightness=1.35),),
            variation=0.40,
        ),
        SoundToken(
            token_id="button.blocked",
            label="Indisponible",
            usage="L'appui n'a pas d'effet. Une note sous la fondamentale, sourde, sans suite.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(Note(degree=-1, duration_seconds=0.30, gain=0.45, transient=0.55, brightness=0.35),),
        ),
        SoundToken(
            token_id="press.hold",
            label="Appui long, tension",
            usage="Tenu pendant tout l'appui long. La tension monte avec la progression vers le seuil.",
            behaviour=TokenBehaviour.SUSTAINED,
            notes=(Note(degree=0, duration_seconds=1.20, gain=0.32, transient=0.20, brightness=0.55),),
        ),
        SoundToken(
            token_id="press.commit",
            label="Appui long, déclenchement",
            usage="Le seuil est atteint. Résolution nette qui répond à la tension.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=4, duration_seconds=0.35, gain=0.70, transient=0.70),
                Note(degree=7, offset_seconds=0.055, duration_seconds=0.70, gain=0.65, transient=0.15),
            ),
        ),
        SoundToken(
            token_id="press.abort",
            label="Appui long, abandon",
            usage="Le doigt se relève avant le seuil. La tension retombe sans récompense.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(Note(degree=-1, duration_seconds=0.28, gain=0.38, transient=0.30, brightness=0.45),),
        ),
    ),
)


# ----------------------------------------------------------------
# Sliders and numeric values
# ----------------------------------------------------------------

VALUES = Category(
    key="valeurs",
    label="Sliders et valeurs",
    description=(
        "Des sons déclenchés en rafale, dont la hauteur suit la valeur réglée. "
        "Ce sont les plus difficiles à réussir : ils doivent survivre à cent "
        "répétitions d'affilée."
    ),
    tokens=(
        SoundToken(
            token_id="slider.grab",
            label="Saisie de la poignée",
            usage="Le doigt attrape le curseur. Marque le début d'un geste continu.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(Note(degree=0, duration_seconds=0.22, gain=0.40, transient=0.85, brightness=0.90),),
        ),
        SoundToken(
            token_id="slider.tick",
            label="Cran",
            usage="Un pas de valeur franchi. La hauteur suit la position, la variation évite l'effet mitraillette.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=4, duration_seconds=0.09, gain=0.20, transient=1.30, brightness=1.50),),
            tracks_value=True,
            variation=0.45,
        ),
        SoundToken(
            token_id="slider.detent",
            label="Point d'ancrage",
            usage="Une valeur remarquable, comme zéro ou cent pour cent. Plus plein qu'un cran ordinaire.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(
                Note(degree=2, duration_seconds=0.20, gain=0.45, transient=0.95, brightness=1.15),
                Note(degree=4, offset_seconds=0.030, duration_seconds=0.28, gain=0.30, transient=0.0),
            ),
            tracks_value=True,
            variation=0.15,
        ),
        SoundToken(
            token_id="slider.limit",
            label="Butée",
            usage="Le curseur est au bout de sa course. Sourd et mat, il ne doit surtout pas récompenser.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=-2, duration_seconds=0.34, gain=0.50, transient=0.85, brightness=0.30),),
            variation=0.10,
        ),
        SoundToken(
            token_id="slider.release",
            label="Lâcher de la poignée",
            usage="Le geste continu se termine. Referme la parenthèse ouverte par la saisie.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(Note(degree=2, duration_seconds=0.26, gain=0.34, transient=0.45, brightness=1.05),),
            tracks_value=True,
        ),
        SoundToken(
            token_id="stepper.increment",
            label="Incrément",
            usage="Le bouton plus d'un sélecteur numérique. Monte d'un degré à chaque pas.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=2, duration_seconds=0.16, gain=0.42, transient=0.90, brightness=1.20),),
            tracks_value=True,
            variation=0.20,
        ),
        SoundToken(
            token_id="stepper.decrement",
            label="Décrément",
            usage="Le bouton moins. Même frappe, un degré plus bas, pour que la direction s'entende.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=0, duration_seconds=0.16, gain=0.42, transient=0.90, brightness=1.05),),
            tracks_value=True,
            variation=0.20,
        ),
    ),
)


# ----------------------------------------------------------------
# Carousels and navigation
# ----------------------------------------------------------------

NAVIGATION = Category(
    key="navigation",
    label="Carrousels et navigation",
    description=(
        "Se déplacer dans une séquence. La hauteur monte quand on avance et "
        "redescend quand on recule, ce qui donne une position audible dans "
        "la liste."
    ),
    tokens=(
        SoundToken(
            token_id="carousel.next",
            label="Élément suivant",
            usage="Une carte défile vers la gauche. Le degré monte avec l'index affiché.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(
                Note(degree=2, duration_seconds=0.18, gain=0.42, transient=0.50),
                Note(degree=4, offset_seconds=0.050, duration_seconds=0.35, gain=0.45, transient=0.12),
            ),
            tracks_value=True,
            variation=0.12,
        ),
        SoundToken(
            token_id="carousel.previous",
            label="Élément précédent",
            usage="Le même geste dans l'autre sens. Les deux notes sont inversées.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(
                Note(degree=4, duration_seconds=0.18, gain=0.42, transient=0.50),
                Note(degree=2, offset_seconds=0.050, duration_seconds=0.35, gain=0.45, transient=0.12),
            ),
            tracks_value=True,
            variation=0.12,
        ),
        SoundToken(
            token_id="carousel.wrap",
            label="Retour au début",
            usage="La liste boucle. Une octave franchie d'un coup, pour que le saut s'entende.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=7, duration_seconds=0.16, gain=0.35, transient=0.30),
                Note(degree=0, offset_seconds=0.060, duration_seconds=0.45, gain=0.45, transient=0.15),
            ),
        ),
        SoundToken(
            token_id="carousel.end",
            label="Fin de liste",
            usage="Il n'y a rien après. Une note mate qui n'invite pas à insister.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=-2, duration_seconds=0.30, gain=0.42, transient=0.70, brightness=0.35),),
            variation=0.10,
        ),
        SoundToken(
            token_id="nav.forward",
            label="Page suivante",
            usage="Entrer plus profond dans la navigation. Un peu plus ample qu'un élément de carrousel.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.22, gain=0.38, transient=0.35),
                Note(degree=4, offset_seconds=0.065, duration_seconds=0.55, gain=0.45, transient=0.10),
            ),
        ),
        SoundToken(
            token_id="nav.back",
            label="Page précédente",
            usage="Ressortir d'un niveau. Descend là où la page suivante montait.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=4, duration_seconds=0.22, gain=0.38, transient=0.35),
                Note(degree=0, offset_seconds=0.065, duration_seconds=0.55, gain=0.45, transient=0.10, brightness=0.75),
            ),
        ),
        SoundToken(
            token_id="nav.tab",
            label="Changement d'onglet",
            usage="Un déplacement latéral, sans hiérarchie. Une seule note, franche et courte.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=5, duration_seconds=0.20, gain=0.40, transient=0.55, brightness=1.15),),
            tracks_value=True,
            variation=0.15,
        ),
    ),
)


# ----------------------------------------------------------------
# Disclosures and panels
# ----------------------------------------------------------------

PANELS = Category(
    key="panneaux",
    label="Déplis et panneaux",
    description=(
        "Des surfaces qui s'ouvrent et se referment. La durée du son doit "
        "tomber avec la fin de l'animation, sinon le son continue après que "
        "le mouvement s'est arrêté."
    ),
    tokens=(
        SoundToken(
            token_id="disclosure.expand",
            label="Déplier",
            usage="Une section révèle son contenu. Trois notes qui montent le long du déroulé.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.20, gain=0.30, transient=0.22),
                Note(degree=2, offset_seconds=0.045, duration_seconds=0.24, gain=0.32, transient=0.10),
                Note(degree=4, offset_seconds=0.090, duration_seconds=0.55, gain=0.36, transient=0.08),
            ),
        ),
        SoundToken(
            token_id="disclosure.collapse",
            label="Replier",
            usage="La section se referme. Même dessin à l'envers, légèrement plus sombre.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=4, duration_seconds=0.18, gain=0.30, transient=0.18),
                Note(degree=2, offset_seconds=0.045, duration_seconds=0.22, gain=0.30, transient=0.08),
                Note(degree=0, offset_seconds=0.090, duration_seconds=0.48, gain=0.36, transient=0.08, brightness=0.70),
            ),
        ),
        SoundToken(
            token_id="drawer.open",
            label="Ouverture du tiroir",
            usage="Un panneau glisse depuis un bord. Plus lent et plus ample qu'un simple dépli.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.30, gain=0.30, transient=0.15, attack_seconds=0.020),
                Note(degree=4, offset_seconds=0.080, duration_seconds=0.35, gain=0.32, transient=0.06, attack_seconds=0.020),
                Note(degree=7, offset_seconds=0.160, duration_seconds=0.80, gain=0.40, transient=0.05, attack_seconds=0.025),
            ),
        ),
        SoundToken(
            token_id="drawer.close",
            label="Fermeture du tiroir",
            usage="Le panneau repart. Se termine sur la fondamentale, ce qui sonne comme une résolution.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=7, duration_seconds=0.22, gain=0.30, transient=0.12),
                Note(degree=4, offset_seconds=0.060, duration_seconds=0.26, gain=0.32, transient=0.06),
                Note(degree=0, offset_seconds=0.130, duration_seconds=0.65, gain=0.42, transient=0.06, brightness=0.70),
            ),
        ),
        SoundToken(
            token_id="modal.open",
            label="Ouverture de la boîte de dialogue",
            usage="L'écran passe en arrière-plan. Attaque douce, le son doit envelopper plutôt que frapper.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=7, duration_seconds=0.55, gain=0.26, transient=0.04, brightness=1.35, attack_seconds=0.055),
                Note(degree=9, offset_seconds=0.100, duration_seconds=0.85, gain=0.30, transient=0.03, brightness=1.35, attack_seconds=0.070),
            ),
        ),
        SoundToken(
            token_id="modal.close",
            label="Fermeture de la boîte de dialogue",
            usage="On revient à l'écran. Descente rapide vers la fondamentale.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=5, duration_seconds=0.28, gain=0.30, transient=0.08),
                Note(degree=0, offset_seconds=0.070, duration_seconds=0.50, gain=0.34, transient=0.05, brightness=0.65),
            ),
        ),
        SoundToken(
            token_id="tooltip.show",
            label="Apparition d'une bulle d'aide",
            usage="Une information s'affiche sans qu'on l'ait demandée. Le plus discret des sons d'apparition.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=9, duration_seconds=0.30, gain=0.18, transient=0.05, brightness=1.40, attack_seconds=0.030),),
            variation=0.25,
        ),
    ),
)


# ----------------------------------------------------------------
# Switches and selection
# ----------------------------------------------------------------

SELECTION = Category(
    key="selection",
    label="Interrupteurs et sélection",
    description="Deux états, deux sons symétriques. La direction de l'intervalle porte le sens.",
    tokens=(
        SoundToken(
            token_id="toggle.on",
            label="Activer",
            usage="L'interrupteur passe à vrai. L'intervalle monte.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=1, duration_seconds=0.26, gain=0.58, transient=0.70),
                Note(degree=3, offset_seconds=0.055, duration_seconds=0.42, gain=0.66, transient=0.25),
            ),
        ),
        SoundToken(
            token_id="toggle.off",
            label="Désactiver",
            usage="Retour à faux. Exactement le même son à l'envers, ce qui rend la paire lisible.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=3, duration_seconds=0.26, gain=0.58, transient=0.70),
                Note(degree=1, offset_seconds=0.055, duration_seconds=0.38, gain=0.54, transient=0.25),
            ),
        ),
        SoundToken(
            token_id="checkbox.check",
            label="Cocher",
            usage="Une case est cochée. Plus bref qu'un interrupteur : on en coche souvent plusieurs de suite.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=4, duration_seconds=0.16, gain=0.44, transient=0.95, brightness=1.15),),
            variation=0.20,
        ),
        SoundToken(
            token_id="checkbox.uncheck",
            label="Décocher",
            usage="La case se vide. Même frappe, deux degrés plus bas.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=2, duration_seconds=0.16, gain=0.40, transient=0.95, brightness=0.95),),
            variation=0.20,
        ),
        SoundToken(
            token_id="chip.select",
            label="Sélectionner une étiquette",
            usage="Un filtre est ajouté. La hauteur suit le nombre de filtres actifs.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=2, duration_seconds=0.20, gain=0.40, transient=0.70, brightness=1.20),),
            tracks_value=True,
            variation=0.20,
        ),
        SoundToken(
            token_id="chip.deselect",
            label="Retirer une étiquette",
            usage="Le filtre est retiré. Redescend d'autant que la sélection avait monté.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=1, duration_seconds=0.20, gain=0.36, transient=0.70, brightness=0.90),),
            tracks_value=True,
            variation=0.20,
        ),
    ),
)


# ----------------------------------------------------------------
# Text entry
# ----------------------------------------------------------------

TYPING = Category(
    key="saisie",
    label="Saisie",
    description=(
        "Les sons les plus répétés de tous. Une forte variation aléatoire est "
        "indispensable : deux frappes rigoureusement identiques sonnent "
        "comme une machine."
    ),
    tokens=(
        SoundToken(
            token_id="input.key",
            label="Frappe clavier",
            usage="Un caractère est saisi. Doit rester très en dessous du reste du système.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=6, duration_seconds=0.07, gain=0.18, transient=1.20, brightness=1.40),),
            variation=0.60,
        ),
        SoundToken(
            token_id="input.delete",
            label="Effacement",
            usage="Un caractère disparaît. Même brèveté que la frappe, plus sombre.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=4, duration_seconds=0.09, gain=0.20, transient=1.10, brightness=0.80),),
            variation=0.50,
        ),
        SoundToken(
            token_id="input.clear",
            label="Tout effacer",
            usage="Le champ est vidé d'un coup. Une chute jusqu'à la fondamentale.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=4, duration_seconds=0.16, gain=0.35, transient=0.80, brightness=0.70),
                Note(degree=0, offset_seconds=0.060, duration_seconds=0.40, gain=0.40, transient=0.30, brightness=0.50),
            ),
        ),
        SoundToken(
            token_id="input.suggestion",
            label="Suggestion proposée",
            usage="L'autocomplétion propose quelque chose. Deux notes hautes, sans frappe, qui n'interrompent pas la saisie.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(
                Note(degree=7, duration_seconds=0.22, gain=0.20, transient=0.10, brightness=1.50, attack_seconds=0.020),
                Note(degree=9, offset_seconds=0.050, duration_seconds=0.40, gain=0.22, transient=0.08, brightness=1.50, attack_seconds=0.028),
            ),
            variation=0.30,
        ),
        SoundToken(
            token_id="input.submit",
            label="Envoi du formulaire",
            usage="Le contenu part. Deux notes qui montent, plus assurées qu'une simple validation de champ.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=2, duration_seconds=0.32, gain=0.58, transient=0.55),
                Note(degree=5, offset_seconds=0.060, duration_seconds=0.55, gain=0.60, transient=0.15),
            ),
        ),
    ),
)


# ----------------------------------------------------------------
# System feedback
# ----------------------------------------------------------------

FEEDBACK = Category(
    key="retours",
    label="Retours",
    description=(
        "Ce que le système répond de lui-même. Ce sont les seuls jetons qui "
        "ont le droit d'être longs, parce qu'ils ne se déclenchent jamais en "
        "rafale."
    ),
    tokens=(
        SoundToken(
            token_id="feedback.success",
            label="Réussite",
            usage="L'opération a abouti. Trois degrés ascendants, la dernière note tenue.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.32, gain=0.55, transient=0.45),
                Note(degree=2, offset_seconds=0.075, duration_seconds=0.35, gain=0.55, transient=0.15),
                Note(degree=4, offset_seconds=0.150, duration_seconds=0.85, gain=0.62, transient=0.10),
            ),
        ),
        SoundToken(
            token_id="feedback.error",
            label="Échec",
            usage="L'opération a échoué. Descend sous la fondamentale, sans jamais devenir agressif.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=1, duration_seconds=0.32, gain=0.60, transient=0.60, brightness=0.60),
                Note(degree=-1, offset_seconds=0.090, duration_seconds=0.60, gain=0.60, transient=0.20, brightness=0.42),
            ),
        ),
        SoundToken(
            token_id="feedback.warning",
            label="Avertissement",
            usage="Quelque chose demande une vérification. Le même degré répété deux fois : insister sans conclure.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=3, duration_seconds=0.26, gain=0.55, transient=0.50, brightness=0.95),
                Note(degree=3, offset_seconds=0.140, duration_seconds=0.45, gain=0.50, transient=0.40, brightness=0.95),
            ),
        ),
        SoundToken(
            token_id="feedback.notification",
            label="Notification",
            usage="Un message arrive. Doit se distinguer d'une réussite : c'est une information, pas une récompense.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=2, duration_seconds=0.30, gain=0.48, transient=0.30),
                Note(degree=6, offset_seconds=0.090, duration_seconds=0.75, gain=0.55, transient=0.12),
            ),
        ),
        SoundToken(
            token_id="feedback.complete",
            label="Tâche terminée",
            usage="Un traitement long se termine. Plus étalé qu'une réussite, pour un événement qu'on n'attendait plus.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.26, gain=0.45, transient=0.30),
                Note(degree=4, offset_seconds=0.085, duration_seconds=0.28, gain=0.48, transient=0.12),
                Note(degree=7, offset_seconds=0.170, duration_seconds=0.95, gain=0.60, transient=0.10),
            ),
        ),
        SoundToken(
            token_id="feedback.undo",
            label="Annulation",
            usage="L'action précédente est défaite. Un mouvement rétrograde, court et neutre.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=5, duration_seconds=0.20, gain=0.42, transient=0.40),
                Note(degree=2, offset_seconds=0.055, duration_seconds=0.40, gain=0.44, transient=0.15, brightness=0.80),
            ),
        ),
    ),
)


# ----------------------------------------------------------------
# Dragging and pulling
# ----------------------------------------------------------------

DRAGGING = Category(
    key="deplacement",
    label="Glisser et tirer",
    description=(
        "Des gestes qui durent. Le son est tenu pendant le mouvement et "
        "piloté par la progression, au lieu d'être déclenché une fois pour "
        "toutes."
    ),
    tokens=(
        SoundToken(
            token_id="drag.lift",
            label="Prise en main",
            usage="L'élément quitte sa place et suit le doigt. Tenu tant qu'on le déplace.",
            behaviour=TokenBehaviour.SUSTAINED,
            notes=(Note(degree=0, duration_seconds=2.00, gain=0.22, transient=0.60, brightness=0.70),),
        ),
        SoundToken(
            token_id="drag.over",
            label="Survol d'une cible",
            usage="L'élément passe au-dessus d'une zone qui l'accepte. La hauteur suit la cible survolée.",
            behaviour=TokenBehaviour.REPEATABLE,
            notes=(Note(degree=4, duration_seconds=0.14, gain=0.24, transient=0.55, brightness=1.30),),
            tracks_value=True,
            variation=0.30,
        ),
        SoundToken(
            token_id="drag.drop",
            label="Dépôt",
            usage="L'élément se pose. Une note pleine qui ferme le geste.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.30, gain=0.62, transient=0.95),
                Note(degree=4, offset_seconds=0.040, duration_seconds=0.50, gain=0.45, transient=0.10),
            ),
        ),
        SoundToken(
            token_id="drag.reject",
            label="Dépôt refusé",
            usage="La zone n'accepte pas l'élément, qui retourne à sa place. Sourd et sans résolution.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(Note(degree=-2, duration_seconds=0.38, gain=0.48, transient=0.75, brightness=0.32),),
        ),
        SoundToken(
            token_id="refresh.pull",
            label="Tirer pour rafraîchir",
            usage="La liste est tirée vers le bas. La tension monte avec la distance parcourue.",
            behaviour=TokenBehaviour.SUSTAINED,
            notes=(Note(degree=0, duration_seconds=2.00, gain=0.26, transient=0.15, brightness=0.60),),
        ),
        SoundToken(
            token_id="refresh.release",
            label="Déclenchement du rafraîchissement",
            usage="Le seuil est franchi et la liste se recharge. Résout la tension du geste.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=4, duration_seconds=0.28, gain=0.55, transient=0.50),
                Note(degree=9, offset_seconds=0.070, duration_seconds=0.70, gain=0.55, transient=0.12),
            ),
        ),
    ),
)


# ----------------------------------------------------------------
# Application lifecycle
# ----------------------------------------------------------------

SYSTEM = Category(
    key="systeme",
    label="Cycle de vie",
    description="Les rares moments où l'application parle d'elle-même plutôt que d'un geste.",
    tokens=(
        SoundToken(
            token_id="system.start",
            label="Démarrage",
            usage="L'application s'ouvre. Le seul jeton qui a le droit de dépasser une seconde.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.50, gain=0.35, transient=0.15, attack_seconds=0.030),
                Note(degree=4, offset_seconds=0.140, duration_seconds=0.50, gain=0.35, transient=0.10, attack_seconds=0.030),
                Note(degree=7, offset_seconds=0.280, duration_seconds=1.15, gain=0.42, transient=0.08, attack_seconds=0.040),
            ),
        ),
        SoundToken(
            token_id="system.ready",
            label="Prêt",
            usage="Le chargement est fini, l'interface répond. Court et haut, pour libérer l'attention.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=7, duration_seconds=0.28, gain=0.40, transient=0.20),
                Note(degree=9, offset_seconds=0.080, duration_seconds=0.80, gain=0.42, transient=0.10),
            ),
        ),
        SoundToken(
            token_id="system.lock",
            label="Verrouillage",
            usage="La session se ferme. Chute nette vers le grave.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=2, duration_seconds=0.20, gain=0.50, transient=0.90, brightness=0.60),
                Note(degree=-2, offset_seconds=0.070, duration_seconds=0.50, gain=0.55, transient=0.50, brightness=0.35),
            ),
        ),
        SoundToken(
            token_id="system.unlock",
            label="Déverrouillage",
            usage="La session s'ouvre. Le verrouillage joué à l'envers.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=-2, duration_seconds=0.20, gain=0.50, transient=0.70, brightness=0.50),
                Note(degree=2, offset_seconds=0.070, duration_seconds=0.45, gain=0.50, transient=0.30, brightness=0.90),
            ),
        ),
        SoundToken(
            token_id="system.offline",
            label="Perte de connexion",
            usage="Le réseau est tombé. Descend et s'éteint, sans dramatiser.",
            behaviour=TokenBehaviour.ONE_SHOT,
            notes=(
                Note(degree=0, duration_seconds=0.35, gain=0.50, transient=0.40, brightness=0.50),
                Note(degree=-2, offset_seconds=0.120, duration_seconds=0.90, gain=0.50, transient=0.15, brightness=0.30),
            ),
        ),
    ),
)


CATEGORIES: tuple[Category, ...] = (
    BUTTONS,
    VALUES,
    NAVIGATION,
    PANELS,
    SELECTION,
    TYPING,
    FEEDBACK,
    DRAGGING,
    SYSTEM,
)


def iter_tokens() -> list[SoundToken]:
    """Return every token of the catalogue in display order.

    Returns:
        A flat list of tokens across all categories.
    """
    return [token for category in CATEGORIES for token in category.tokens]


def get_token(token_id: str) -> SoundToken:
    """Return the token registered under the given identifier.

    Args:
        token_id: Dotted identifier of the token.

    Returns:
        The matching token.

    Raises:
        KeyError: If no token is registered under that identifier.
    """
    for token in iter_tokens():
        if token.token_id == token_id:
            return token

    raise KeyError(f"Unknown token: {token_id}")

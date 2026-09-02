# Soundboard Design

Générateur de palettes sonores cohérentes pour systèmes de design.

Chaque son de l'interface est une note de la même gamme, jouée sur la même
matière. On règle la palette une fois, on l'essaie sur de vrais composants,
puis on l'exporte.

## Démarrer

```bash
uv sync
uv run main.py
```

L'interface est alors disponible sur http://127.0.0.1:8000.

Options utiles :

```bash
uv run main.py --port 3000
uv run main.py --reload
```

## Architecture

Le partage des rôles est net : Python possède les définitions, le navigateur
fait le son.

```
soundboard_design/
    domain.py          Modèle typé : matières, jetons, gammes, palettes
    materials.py       Les treize corps sonores
    scales.py          Gammes et rapports d'intonation juste
    catalog.py         Les jetons, groupés par famille d'interaction
    presets.py         Ambiances prêtes à l'emploi
    design_system.py   Assemblage et validation croisée
    server.py          FastAPI : /api/design-system et l'interface
    static/
        index.html
        css/app.css
        js/engine.js   Cinq moteurs de synthèse, live et hors ligne
        js/tuning.js   Degré vers fréquence
        js/bench.js    Le banc d'essai interactif
        js/library.js  La bibliothèque de jetons
        js/palette.js  Le panneau de réglages
        js/scope.js    L'oscilloscope
        js/export.js   Encodage WAV et spécification JSON
        js/state.js    Le magasin de palette
        js/main.js     Amorçage
```

La validation au démarrage refuse un préréglage qui pointe vers une matière
inexistante, un identifiant de jeton en double, ou un jeton tenu qui porterait
plusieurs notes. Une définition incohérente échoue au lancement du serveur, pas
dans le navigateur.

## Le modèle sonore

### Une matière est un modèle physique

Pas une forme d'onde. Chaque matière décrit ses modes de vibration, leurs
rapports de fréquence, leurs temps d'extinction individuels, sa frappe et sa
durée naturelle. Le bois s'éteint en une centaine de millisecondes quoi que dise
la palette ; le métal traîne dix fois plus longtemps. Le réglage de tenue
multiplie cette durée, il ne la remplace pas, ce qui préserve le caractère
relatif des matières à travers tous les réglages.

Cinq moteurs couvrent les treize matières :

| Moteur  | Principe                                       | Matières                                        |
| ------- | ---------------------------------------------- | ----------------------------------------------- |
| `modal` | Partiels à extinctions séparées                | bois, bois creux, plastique, peau, métal, corde |
| `fm`    | Modulation de fréquence à deux opérateurs      | verre                                           |
| `chirp` | Balayage de hauteur, vibrato et syllabes       | bulle, goutte, oiseau                           |
| `noise` | Bruit filtré sans hauteur stable               | papier                                          |
| `wave`  | Oscillateurs simples, assumés électroniques    | air, puce                                       |

Deux propriétés de matière méritent d'être signalées. `repeats` découpe une
voix en plusieurs syllabes, chacune plus basse et plus discrète que la
précédente : c'est ce qui distingue un cuicui d'un simple balayage.
`octave_shift` transpose une matière d'octaves entières, pour les corps qui
n'existent que dans un registre ; comme l'octave appartient à toutes les
gammes, l'harmonie du système est préservée.

### Pourquoi la corde n'est pas un Karplus-Strong

La première version bouclait un `DelayNode` sur lui-même. La spécification Web
Audio impose un retard minimal d'un quantum de rendu à tout `DelayNode` placé
dans un cycle, soit 128 échantillons : au-dessus de 340 Hz environ, toutes les
notes s'écrasaient sur la même hauteur pendant que le reste du système
transposait normalement. Le modèle additif actuel reproduit le peigne de
position de pincement et l'extinction plus rapide des aigus, reste exactement
dans la gamme, et se rend hors ligne à l'identique.

### Un jeton stocke un degré, jamais une fréquence

C'est ce qui garantit la cohérence : changer la fondamentale ou la gamme
réécrit tous les jetons d'un coup, et deux sons superposés ne peuvent pas jurer
entre eux.

### Trois comportements de déclenchement

- `one_shot` : joué une fois.
- `repeatable` : peut partir en rafale. Reçoit une variation aléatoire de
  hauteur et de niveau, et un débit maximal, sans quoi vingt répétitions
  identiques sonnent comme une machine.
- `sustained` : maintenu ouvert par l'interface et piloté par une progression,
  pour les appuis longs et les gestes tirés.

## Le banc d'essai

Six composants réels câblés sur la palette : slider, carrousel, déplis, appui
long, interrupteur, tirer pour rafraîchir. Une grille de boutons dit à quoi
ressemble un son ; seul un slider qu'on fait glisser dit s'il survit à quarante
répétitions, et seul un appui long qu'on maintient dit si la tension se résout.

## Export

- **JSON** : fréquences, décalages, durées et gains résolus pour la palette
  courante, plus la définition de la matière. De quoi rejouer la palette dans
  n'importe quel moteur.
- **WAV** : rendu hors ligne par `OfflineAudioContext`, sans normalisation. La
  hiérarchie de volume entre les jetons est justement ce qu'un système de design
  doit conserver : un survol doit rester bien plus discret qu'une erreur.

## API

| Route                    | Rôle                                       |
| ------------------------ | ------------------------------------------ |
| `GET /`                  | L'interface                                |
| `GET /api/design-system` | Le système complet consommé par le moteur  |
| `GET /api/health`        | Version et nombre de jetons                |

## Étendre le système

Ajouter une matière : décrire un `Material` dans `materials.py` et l'ajouter au
tuple `MATERIALS`. Si son moteur existe déjà, rien à écrire côté navigateur.

Ajouter un jeton : décrire un `SoundToken` dans la bonne `Category` de
`catalog.py`. Il apparaît dans la bibliothèque et dans les exports sans autre
intervention.

Ajouter un moteur : définir la dataclass de voix dans `domain.py`, l'ajouter à
l'union `VoiceSpec`, puis écrire le constructeur correspondant dans
`static/js/engine.js` et l'enregistrer dans `VOICE_BUILDERS`.

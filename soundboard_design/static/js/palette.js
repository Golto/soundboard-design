/**
 * The palette panel: presets, materials, tuning and character controls.
 *
 * Every control carries a one line explanation of what it changes, because
 * a sound parameter is only useful to a designer who knows what it will do
 * to the fifty tokens they are not currently listening to.
 *
 * The chips are built once and only their pressed state is synchronised
 * afterwards. Rebuilding them on every change would mean rebuilding the
 * whole panel sixty times a second while a slider is being dragged.
 */

import { noteName } from "./tuning.js";

const CHARACTER_CONTROLS = [
  {
    key: "grain",
    label: "Lissé vers grain",
    minimum: 0,
    maximum: 1,
    step: 0.01,
    lowLabel: "lisse",
    highLabel: "rêche",
    hint:
      "Saturation douce à gain compensé, partiels désaccordés qui battent entre eux, " +
      "frappe plus dure et souffle au-delà de 0,35. C'est le réglage qui se remarque " +
      "le plus vite, et celui qui rend un son bon marché quand on en met trop.",
  },
  {
    key: "weight",
    label: "Léger vers lourd",
    minimum: 0,
    maximum: 1,
    step: 0.01,
    lowLabel: "papier",
    highLabel: "fonte",
    hint:
      "Ajoute une sous-octave, renforce le bas du spectre, adoucit l'attaque et " +
      "allonge la chute. À réserver aux jetons rares : c'est ce qui fatigue le plus vite.",
  },
  {
    key: "brightness",
    label: "Éclat",
    minimum: 0.2,
    maximum: 2,
    step: 0.02,
    lowLabel: "feutré",
    highLabel: "perçant",
    hint:
      "Ouverture du filtre passe-bas, relative à la hauteur de chaque note. Bas, le " +
      "son se fond dans la pièce ; haut, il passe au-dessus du bruit ambiant.",
  },
  {
    key: "hold",
    label: "Tenue",
    minimum: 0.3,
    maximum: 2.2,
    step: 0.02,
    lowLabel: "sec",
    highLabel: "tenu",
    hint:
      "Multiplie la durée propre à la matière sans la remplacer : le bois reste court " +
      "même à fond, le métal reste long même au minimum.",
  },
  {
    key: "space",
    label: "Espace",
    minimum: 0,
    maximum: 0.55,
    step: 0.01,
    lowLabel: "sans",
    highLabel: "vaste",
    hint:
      "Réverbération partagée par tous les jetons : c'est elle qui les place dans la " +
      "même pièce. Trop, et le geste disparaît derrière son propre écho.",
  },
  {
    key: "level",
    label: "Niveau",
    minimum: 0.1,
    maximum: 1,
    step: 0.01,
    lowLabel: "bas",
    highLabel: "haut",
    hint:
      "Gain général avant compresseur. Il déplace toute la palette d'un bloc, donc les " +
      "écarts voulus entre un survol et une erreur restent intacts.",
  },
];

const FAMILY_LABELS = {
  percussif: "Percussif",
  "résonant": "Résonant",
  liquide: "Liquide",
  organique: "Organique",
  "synthétique": "Synthétique",
};

const TEMPERAMENTS = [
  ["just", "Juste"],
  ["equal", "Tempéré"],
];

function createChip(label, onSelect, extraClass = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `chip ${extraClass}`.trim();
  button.textContent = label;
  button.setAttribute("aria-pressed", "false");
  button.addEventListener("click", onSelect);
  return button;
}

export class PalettePanel {
  /**
   * @param {PaletteStore} store Palette store driving the interface.
   * @param {object} controls Play helper used to audition changes.
   */
  constructor(store, controls) {
    this.store = store;
    this.controls = controls;

    this.presetChips = new Map();
    this.materialChips = new Map();
    this.scaleChips = new Map();
    this.temperamentChips = new Map();
    this.sliders = new Map();

    this.presetSummary = document.querySelector("[data-panel='preset-summary']");
    this.materialDescription = document.querySelector("[data-panel='material-description']");
    this.scaleDescription = document.querySelector("[data-panel='scale-description']");
    this.rootInput = document.querySelector("[data-panel='root-input']");
    this.rootValue = document.querySelector("[data-panel='root-value']");
    this.rootNote = document.querySelector("[data-panel='root-note']");

    this.buildPresets();
    this.buildMaterials();
    this.buildTuning();
    this.buildCharacterControls();

    store.subscribe(() => this.sync());
  }

  // --------------------------------------------------------------
  // Construction
  // --------------------------------------------------------------

  buildPresets() {
    const host = document.querySelector("[data-panel='presets']");
    this.store.system.presets.forEach((preset) => {
      const chip = createChip(preset.label, () => {
        this.store.applyPreset(preset.key);
        this.controls.play("button.primary");
      });
      this.presetChips.set(preset.key, chip);
      host.append(chip);
    });
  }

  buildMaterials() {
    const host = document.querySelector("[data-panel='materials']");
    const groups = new Map();

    this.store.system.materials.forEach((material) => {
      if (!groups.has(material.family)) {
        groups.set(material.family, []);
      }
      groups.get(material.family).push(material);
    });

    groups.forEach((materials, family) => {
      const group = document.createElement("div");
      group.className = "chip-group";

      const caption = document.createElement("span");
      caption.className = "chip-group-label";
      caption.textContent = FAMILY_LABELS[family] ?? family;

      const chips = document.createElement("div");
      chips.className = "chips";
      materials.forEach((material) => {
        const chip = createChip(material.label, () => {
          this.store.set("materialKey", material.key);
          this.controls.play("button.tap");
        });
        this.materialChips.set(material.key, chip);
        chips.append(chip);
      });

      group.append(caption, chips);
      host.append(group);
    });
  }

  buildTuning() {
    const scaleHost = document.querySelector("[data-panel='scales']");
    this.store.system.scales.forEach((scale) => {
      const chip = createChip(scale.label, () => {
        this.store.set("scaleKey", scale.key);
        this.controls.play("feedback.success");
      });
      this.scaleChips.set(scale.key, chip);
      scaleHost.append(chip);
    });

    const temperamentHost = document.querySelector("[data-panel='temperaments']");
    TEMPERAMENTS.forEach(([key, label]) => {
      const chip = createChip(label, () => {
        this.store.set("temperament", key);
        this.controls.play("feedback.success");
      });
      this.temperamentChips.set(key, chip);
      temperamentHost.append(chip);
    });

    this.rootInput.addEventListener("input", () => {
      this.store.set("rootHz", Number(this.rootInput.value));
    });
    this.rootInput.addEventListener("change", () => {
      this.controls.play("button.primary");
    });
  }

  buildCharacterControls() {
    const host = document.querySelector("[data-panel='character']");

    CHARACTER_CONTROLS.forEach((control) => {
      const field = document.createElement("div");
      field.className = "field";

      const head = document.createElement("div");
      head.className = "field-head";
      const label = document.createElement("label");
      label.setAttribute("for", `control-${control.key}`);
      label.textContent = control.label;
      const value = document.createElement("span");
      value.className = "value";
      head.append(label, value);

      const hint = document.createElement("p");
      hint.className = "hint";
      hint.textContent = control.hint;

      const input = document.createElement("input");
      input.type = "range";
      input.id = `control-${control.key}`;
      input.min = String(control.minimum);
      input.max = String(control.maximum);
      input.step = String(control.step);
      input.addEventListener("input", () => {
        this.store.set(control.key, Number(input.value));
      });
      input.addEventListener("change", () => {
        this.controls.play("button.tap");
      });

      const ends = document.createElement("div");
      ends.className = "range-ends";
      const low = document.createElement("span");
      low.textContent = control.lowLabel;
      const high = document.createElement("span");
      high.textContent = control.highLabel;
      ends.append(low, high);

      field.append(head, hint, input, ends);
      host.append(field);
      this.sliders.set(control.key, { input, value });
    });
  }

  // --------------------------------------------------------------
  // Synchronisation
  // --------------------------------------------------------------

  static setPressed(chips, activeKey) {
    chips.forEach((chip, key) => {
      chip.setAttribute("aria-pressed", String(key === activeKey));
    });
  }

  /** Bring every control back in line with the current palette. */
  sync() {
    const palette = this.store.palette;

    const presetKey = this.store.matchingPresetKey();
    PalettePanel.setPressed(this.presetChips, presetKey);
    const preset = this.store.system.presets.find((item) => item.key === presetKey);
    this.presetSummary.textContent = preset
      ? preset.summary
      : "Palette personnalisée. Choisissez une ambiance pour repartir d'un point connu.";

    PalettePanel.setPressed(this.materialChips, palette.materialKey);
    this.materialDescription.textContent = this.store.material.description;

    PalettePanel.setPressed(this.scaleChips, palette.scaleKey);
    this.scaleDescription.textContent = this.store.scale.description;
    PalettePanel.setPressed(this.temperamentChips, palette.temperament);

    if (document.activeElement !== this.rootInput) {
      this.rootInput.value = String(palette.rootHz);
    }
    this.rootValue.textContent = String(Math.round(palette.rootHz));
    this.rootNote.textContent = noteName(palette.rootHz);

    CHARACTER_CONTROLS.forEach((control) => {
      const slider = this.sliders.get(control.key);
      const current = palette[control.key];
      if (document.activeElement !== slider.input) {
        slider.input.value = String(current);
      }
      slider.value.textContent = current.toFixed(2);
    });
  }
}

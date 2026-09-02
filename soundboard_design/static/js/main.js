/**
 * Application bootstrap.
 *
 * Loads the design system from the backend, wires the engine to the
 * palette store, and connects the test bench, the library and the export
 * panel to the same playback helpers.
 */

import { initialiseBench } from "./bench.js";
import { SoundEngine, tokenLength } from "./engine.js";
import { buildSpecification, downloadBlob, encodeWav, fileNameForToken } from "./export.js";
import { Library } from "./library.js";
import { PalettePanel } from "./palette.js";
import { Oscilloscope } from "./scope.js";
import { PaletteStore, indexTokens } from "./state.js";

const DEMO_SEQUENCE = [
  ["system.start", 0],
  ["system.ready", 1.3],
  ["button.hover", 2.0],
  ["button.tap", 2.3],
  ["drawer.open", 2.7],
  ["input.key", 3.5],
  ["input.key", 3.62],
  ["input.key", 3.74],
  ["input.suggestion", 4.0],
  ["slider.tick", 4.6],
  ["slider.tick", 4.72],
  ["slider.detent", 4.9],
  ["toggle.on", 5.3],
  ["carousel.next", 5.7],
  ["input.submit", 6.1],
  ["feedback.success", 6.7],
  ["drawer.close", 7.7],
];

const EXPORT_BUTTON_LABEL = "Télécharger tous les WAV";

async function loadDesignSystem() {
  const response = await fetch("/api/design-system");
  if (!response.ok) {
    throw new Error(`Le système de design n'a pas pu être chargé (${response.status}).`);
  }
  return response.json();
}

function formatReadout(token, notes) {
  const frequencies = notes.map((note) => Math.round(note.frequency)).join(" vers ");
  const duration = Math.round(tokenLength(notes) * 1000);
  return `${token.tokenId}   ${frequencies} Hz   ${duration} ms`;
}

function buildControls(engine, tokens, scope, readout) {
  return {
    play: (tokenId, options) => {
      const token = tokens.get(tokenId);
      if (!token) {
        return null;
      }
      const notes = engine.play(token, options);
      scope.attach(engine.analyser);
      return notes;
    },
    sustain: (tokenId, options) => {
      const token = tokens.get(tokenId);
      if (!token) {
        return { update: () => {}, release: () => {} };
      }
      const handle = engine.startSustain(token, options);
      scope.attach(engine.analyser);
      readout.textContent = `${token.tokenId}   son tenu`;
      return handle;
    },
  };
}

function bindExports(system, store, engine) {
  document.querySelector("[data-action='export-json']").addEventListener("click", () => {
    const specification = buildSpecification(system, store.palette, store.material, engine.tuning);
    const blob = new Blob([JSON.stringify(specification, null, 2)], {
      type: "application/json",
    });
    downloadBlob(blob, `palette-${store.palette.materialKey}.json`);
  });

  const exportButton = document.querySelector("[data-action='export-wav']");
  exportButton.addEventListener("click", async () => {
    const renderable = system.categories
      .flatMap((category) => category.tokens)
      .filter((token) => token.behaviour !== "sustained");

    exportButton.disabled = true;
    try {
      for (let index = 0; index < renderable.length; index += 1) {
        const token = renderable[index];
        exportButton.textContent = `Rendu ${index + 1} sur ${renderable.length}`;
        const buffer = await engine.render(token);
        downloadBlob(encodeWav(buffer), `${fileNameForToken(token.tokenId)}.wav`);
        await new Promise((resolve) => window.setTimeout(resolve, 260));
      }
    } finally {
      exportButton.textContent = EXPORT_BUTTON_LABEL;
      exportButton.disabled = false;
    }
  });
}

async function start() {
  const system = await loadDesignSystem();
  const store = new PaletteStore(system);
  const tokens = indexTokens(system);

  const engine = new SoundEngine(system);
  engine.setPalette(store.palette);
  store.subscribe((palette) => engine.setPalette(palette));

  const scope = new Oscilloscope(document.querySelector("[data-panel='scope']"));
  const readout = document.querySelector("[data-panel='readout']");
  engine.onTokenPlayed = (token, notes) => {
    readout.textContent = formatReadout(token, notes);
  };

  const controls = buildControls(engine, tokens, scope, readout);

  // NOTE: the panel synchronises itself on every palette change, and the
  // library never depends on the palette, so it is built once only.
  const panel = new PalettePanel(store, controls);
  panel.sync();
  new Library(store, engine, controls);

  initialiseBench(controls);
  bindExports(system, store, engine);

  document.querySelector("[data-action='demo']").addEventListener("click", () => {
    DEMO_SEQUENCE.forEach(([tokenId, offset]) => {
      window.setTimeout(() => controls.play(tokenId), offset * 1000);
    });
  });

  const tokenCount = system.categories.reduce(
    (total, category) => total + category.tokens.length,
    0,
  );
  document.querySelector("[data-panel='token-count']").textContent = String(tokenCount);
  document.querySelector("[data-panel='material-count']").textContent = String(
    system.materials.length,
  );
}

start().catch((error) => {
  const readout = document.querySelector("[data-panel='readout']");
  if (readout) {
    readout.textContent = error.message;
  }
});

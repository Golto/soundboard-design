/**
 * Exporting a palette: WAV renders and a machine readable specification.
 *
 * Renders are deliberately not normalised. Normalising each token would
 * destroy the level hierarchy of the palette, which is exactly the part a
 * design system needs to keep: a hover must stay far quieter than an error.
 */

import { resolveToken, tokenLength } from "./engine.js";
import { noteName } from "./tuning.js";

const SILENCE_THRESHOLD = 2e-4;

/**
 * Encode a mono audio buffer as a 16 bit PCM WAV blob.
 *
 * Trailing silence is trimmed so that the reverb tail does not leave two
 * dead seconds at the end of every file.
 *
 * @param {AudioBuffer} buffer Rendered audio.
 * @returns {Blob} A WAV file.
 */
export function encodeWav(buffer) {
  const samples = buffer.getChannelData(0);
  const sampleRate = buffer.sampleRate;

  let last = samples.length - 1;
  while (last > 0 && Math.abs(samples[last]) < SILENCE_THRESHOLD) {
    last -= 1;
  }
  const length = Math.min(samples.length, last + Math.floor(sampleRate * 0.03));

  const byteLength = 44 + length * 2;
  const arrayBuffer = new ArrayBuffer(byteLength);
  const view = new DataView(arrayBuffer);

  const writeText = (offset, text) => {
    for (let index = 0; index < text.length; index += 1) {
      view.setUint8(offset + index, text.charCodeAt(index));
    }
  };

  writeText(0, "RIFF");
  view.setUint32(4, byteLength - 8, true);
  writeText(8, "WAVE");
  writeText(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeText(36, "data");
  view.setUint32(40, length * 2, true);

  for (let index = 0; index < length; index += 1) {
    const value = Math.max(-1, Math.min(1, samples[index]));
    view.setInt16(44 + index * 2, value < 0 ? value * 0x8000 : value * 0x7fff, true);
  }

  return new Blob([arrayBuffer], { type: "audio/wav" });
}

/**
 * Trigger a browser download for a blob.
 *
 * @param {Blob} blob Content to download.
 * @param {string} filename Name given to the saved file.
 */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 5000);
}

/**
 * Build the full specification of the current palette.
 *
 * The result holds resolved frequencies, offsets, durations and gains for
 * every token, plus the settings that produced them, so the palette can be
 * replayed in any engine without this application.
 *
 * @param {object} system Design system payload.
 * @param {object} palette Current palette settings.
 * @param {object} material Material in use.
 * @param {object} tuning Tuning descriptor.
 * @returns {object} A JSON ready specification.
 */
export function buildSpecification(system, palette, material, tuning) {
  const specification = {
    generatedAt: new Date().toISOString(),
    systemVersion: system.version,
    tuning: {
      rootHz: Math.round(palette.rootHz * 100) / 100,
      rootNote: noteName(palette.rootHz),
      scale: palette.scaleKey,
      scaleSteps: tuning.steps,
      temperament: palette.temperament,
    },
    material: {
      key: material.key,
      label: material.label,
      engine: material.engine,
      durationFactor: material.durationFactor,
      voice: material.voice,
    },
    character: {
      grain: palette.grain,
      weight: palette.weight,
      brightness: palette.brightness,
      hold: palette.hold,
      space: palette.space,
      level: palette.level,
    },
    categories: {},
  };

  system.categories.forEach((category) => {
    specification.categories[category.key] = {
      label: category.label,
      tokens: category.tokens.map((token) => {
        const notes = resolveToken(token, material, palette, tuning, { variationScale: 0 });
        return {
          tokenId: token.tokenId,
          label: token.label,
          behaviour: token.behaviour,
          tracksValue: token.tracksValue,
          variation: token.variation,
          durationMs: Math.round(tokenLength(notes) * 1000),
          notes: notes.map((note) => ({
            degree: note.degree,
            frequencyHz: Math.round(note.frequency * 100) / 100,
            offsetMs: Math.round(note.offset * 1000),
            durationMs: Math.round(note.duration * 1000),
            gain: Math.round(note.gain * 1000) / 1000,
          })),
        };
      }),
    };
  });

  return specification;
}

/**
 * Turn a token identifier into a safe file name.
 *
 * @param {string} tokenId Dotted token identifier.
 * @returns {string} A hyphenated file name without extension.
 */
export function fileNameForToken(tokenId) {
  return tokenId.replace(/\./g, "-");
}

/**
 * Turning scale degrees into frequencies.
 *
 * Tokens never store a frequency. They store a degree, and everything that
 * maps a degree onto a pitch lives here, so a change of root or scale
 * rewrites the whole sound set at once.
 */

const FRENCH_NOTE_NAMES = [
  "Do", "Do dièse", "Ré", "Mi bémol", "Mi", "Fa",
  "Fa dièse", "Sol", "Sol dièse", "La", "Si bémol", "Si",
];

const FRENCH_NOTE_SYMBOLS = [
  "Do", "Do♯", "Ré", "Mi♭", "Mi", "Fa",
  "Fa♯", "Sol", "Sol♯", "La", "Si♭", "Si",
];

/**
 * Convert a scale degree into a semitone offset from the root.
 *
 * Degrees below zero and beyond the scale length wrap into lower and
 * higher octaves, so a token can reach outside the scale without leaving
 * the harmony.
 *
 * @param {number} degree Index in the scale, possibly negative.
 * @param {number[]} steps Semitone offsets of the scale, ascending.
 * @returns {number} Semitone offset from the root.
 */
export function degreeToSemitones(degree, steps) {
  const length = steps.length;
  const octave = Math.floor(degree / length);
  const index = degree - octave * length;
  return steps[index] + 12 * octave;
}

/**
 * Compute the frequency of a scale degree under the current tuning.
 *
 * @param {number} degree Index in the scale.
 * @param {object} tuning Root frequency, scale steps, temperament and ratios.
 * @returns {number} Frequency in hertz.
 */
export function frequencyForDegree(degree, tuning) {
  const semitones = degreeToSemitones(degree, tuning.steps);

  if (tuning.temperament === "just") {
    const octave = Math.floor(semitones / 12);
    const index = semitones - octave * 12;
    return tuning.rootHz * tuning.justRatios[index] * Math.pow(2, octave);
  }

  return tuning.rootHz * Math.pow(2, semitones / 12);
}

/**
 * Name the nearest note to a frequency, with its deviation in cents.
 *
 * @param {number} frequency Frequency in hertz.
 * @param {boolean} useSymbols Use accidental symbols instead of full words.
 * @returns {string} A French note name such as "Do5" or "La4 +14 ¢".
 */
export function noteName(frequency, useSymbols = true) {
  const midi = Math.round(12 * Math.log2(frequency / 440)) + 69;
  const exact = 440 * Math.pow(2, (midi - 69) / 12);
  const cents = Math.round(1200 * Math.log2(frequency / exact));
  const names = useSymbols ? FRENCH_NOTE_SYMBOLS : FRENCH_NOTE_NAMES;
  const name = names[((midi % 12) + 12) % 12];
  const octave = Math.floor(midi / 12) - 1;

  if (cents === 0) {
    return `${name}${octave}`;
  }
  return `${name}${octave} ${cents > 0 ? "+" : ""}${cents} ¢`;
}

/**
 * Build the tuning object consumed by frequencyForDegree.
 *
 * @param {object} palette Current palette settings.
 * @param {object} scale Scale definition holding its semitone steps.
 * @param {number[]} justRatios Twelve just intonation ratios.
 * @returns {object} A tuning descriptor.
 */
export function buildTuning(palette, scale, justRatios) {
  return {
    rootHz: palette.rootHz,
    steps: scale.steps,
    temperament: palette.temperament,
    justRatios,
  };
}

/**
 * The synthesis engine.
 *
 * Every material is rendered by one of six voice builders. They all share
 * the same output stage so that a change of grain, weight or brightness
 * behaves identically whatever the material, and the same code path is
 * used for live playback and for offline WAV rendering.
 */

import { frequencyForDegree } from "./tuning.js";

const MAX_SATURATION_DRIVE = 3;
const VOICE_BUDGET = 32;
const REPEAT_INTERVAL_SECONDS = 0.035;

function clamp(value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, value));
}

// ----------------------------------------------------------------
// Cached buffers and curves
// ----------------------------------------------------------------

function whiteNoiseBuffer(context) {
  if (!context.cachedNoise) {
    const length = Math.floor(context.sampleRate * 0.5);
    const buffer = context.createBuffer(1, length, context.sampleRate);
    const channel = buffer.getChannelData(0);
    for (let index = 0; index < length; index += 1) {
      channel[index] = Math.random() * 2 - 1;
    }
    context.cachedNoise = buffer;
  }
  return context.cachedNoise;
}

function impactBuffer(context) {
  if (!context.cachedImpact) {
    const length = Math.floor(context.sampleRate * 0.2);
    const buffer = context.createBuffer(1, length, context.sampleRate);
    const channel = buffer.getChannelData(0);
    for (let index = 0; index < length; index += 1) {
      const fade = 1 - index / length;
      channel[index] = (Math.random() * 2 - 1) * fade * fade;
    }
    context.cachedImpact = buffer;
  }
  return context.cachedImpact;
}

function reverbBuffer(context) {
  if (!context.cachedReverb) {
    const length = Math.floor(context.sampleRate * 1.6);
    const buffer = context.createBuffer(1, length, context.sampleRate);
    const channel = buffer.getChannelData(0);
    for (let index = 0; index < length; index += 1) {
      channel[index] = (Math.random() * 2 - 1) * Math.pow(1 - index / length, 3.4);
    }
    context.cachedReverb = buffer;
  }
  return context.cachedReverb;
}

/**
 * Build a soft clipping curve whose gain is compensated.
 *
 * The raw curve has a slope of (1 + drive) at the origin, which would
 * amplify quiet signals enormously and slam the bus compressor. The
 * makeup gain returned alongside restores the level at half amplitude, so
 * raising the grain changes the timbre without changing the loudness.
 *
 * @param {BaseAudioContext} context Audio context owning the curve cache.
 * @param {number} grain Roughness from 0 to 1.
 * @returns {Float32Array} The transfer curve.
 */
function saturationCurve(context, grain) {
  if (!context.cachedCurves) {
    context.cachedCurves = new Map();
  }
  const quantised = Math.round(grain * 20) / 20;
  if (!context.cachedCurves.has(quantised)) {
    const size = 1024;
    const curve = new Float32Array(size);
    const drive = quantised * MAX_SATURATION_DRIVE;
    for (let index = 0; index < size; index += 1) {
      const input = (index * 2) / size - 1;
      curve[index] = ((1 + drive) * input) / (1 + drive * Math.abs(input));
    }
    context.cachedCurves.set(quantised, curve);
  }
  return context.cachedCurves.get(quantised);
}

function saturationMakeup(grain) {
  const drive = grain * MAX_SATURATION_DRIVE;
  return (1 + 0.5 * drive) / (1 + drive);
}

// ----------------------------------------------------------------
// Output bus
// ----------------------------------------------------------------

/**
 * Build the shared output chain: level, reverb send, compressor.
 *
 * @param {BaseAudioContext} context Live or offline audio context.
 * @param {object} palette Current palette settings.
 * @param {boolean} withAnalyser Insert an analyser for the oscilloscope.
 * @returns {object} The bus input, reverb send gain and optional analyser.
 */
export function createBus(context, palette, withAnalyser = false) {
  const input = context.createGain();
  input.gain.value = palette.level * (1 - 0.15 * palette.grain);

  const compressor = context.createDynamicsCompressor();
  compressor.threshold.value = -11;
  compressor.knee.value = 24;
  compressor.ratio.value = 3;
  compressor.attack.value = 0.004;
  compressor.release.value = 0.2;

  const convolver = context.createConvolver();
  convolver.buffer = reverbBuffer(context);
  const send = context.createGain();
  send.gain.value = palette.space;

  input.connect(compressor);
  input.connect(send);
  send.connect(convolver);
  convolver.connect(compressor);

  let analyser = null;
  if (withAnalyser) {
    analyser = context.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.4;
    compressor.connect(analyser);
    analyser.connect(context.destination);
  } else {
    compressor.connect(context.destination);
  }

  return { input, send, analyser };
}

// ----------------------------------------------------------------
// Voice builders
// ----------------------------------------------------------------

function applyDecayEnvelope(parameter, time, attack, peak, duration) {
  parameter.setValueAtTime(0.0001, time);
  parameter.exponentialRampToValueAtTime(Math.max(0.002, peak), time + attack);
  parameter.exponentialRampToValueAtTime(0.0001, time + duration);
}

function buildModalVoice(context, target, spec) {
  const { voice } = spec.material;
  const total = voice.partials.reduce((sum, partial) => sum + partial.gain, 0);
  const normalisation = 1 / (0.55 + 0.45 * total);

  voice.partials.forEach((partial) => {
    const oscillator = context.createOscillator();
    oscillator.type = voice.waveform;
    const partialFrequency = spec.frequency * partial.ratio;

    if (voice.pitchDrop > 1 && partial.ratio === 1) {
      oscillator.frequency.setValueAtTime(partialFrequency * voice.pitchDrop, spec.time);
      oscillator.frequency.exponentialRampToValueAtTime(
        partialFrequency,
        spec.time + voice.pitchDropSeconds,
      );
    } else {
      oscillator.frequency.setValueAtTime(partialFrequency, spec.time);
    }
    if (partial.ratio !== 1) {
      oscillator.detune.setValueAtTime(spec.grain * 18, spec.time);
    }

    const partialDuration = Math.max(0.035, spec.duration * partial.decay);
    const envelope = context.createGain();
    applyDecayEnvelope(
      envelope.gain,
      spec.time,
      Math.min(spec.attack, partialDuration * 0.4),
      spec.gain * partial.gain * normalisation,
      partialDuration,
    );

    oscillator.connect(envelope);
    envelope.connect(target);
    oscillator.start(spec.time);
    oscillator.stop(spec.time + partialDuration + 0.04);
  });
}

function buildFmVoice(context, target, spec) {
  const { voice } = spec.material;

  const envelope = context.createGain();
  applyDecayEnvelope(envelope.gain, spec.time, spec.attack, spec.gain, spec.duration);
  envelope.connect(target);

  const carrier = context.createOscillator();
  carrier.type = "sine";
  carrier.frequency.setValueAtTime(spec.frequency, spec.time);

  const modulator = context.createOscillator();
  modulator.type = "sine";
  modulator.frequency.setValueAtTime(
    spec.frequency * voice.modulatorRatio * (1 + spec.grain * 0.1),
    spec.time,
  );

  const modulationDepth = context.createGain();
  const index =
    spec.frequency * voice.modulationIndex * clamp(spec.brightness, 0.15, 2.2) * (1 + spec.grain * 0.7);
  modulationDepth.gain.setValueAtTime(index, spec.time);
  modulationDepth.gain.exponentialRampToValueAtTime(
    Math.max(1, index * 0.03),
    spec.time + spec.duration * 0.5,
  );

  modulator.connect(modulationDepth);
  modulationDepth.connect(carrier.frequency);
  carrier.connect(envelope);

  carrier.start(spec.time);
  carrier.stop(spec.time + spec.duration + 0.05);
  modulator.start(spec.time);
  modulator.stop(spec.time + spec.duration + 0.05);
}

function buildStringVoice(context, target, spec) {
  const { voice } = spec.material;

  // NOTE: above the material ceiling the delay line gets too short to stay
  // stable, so the note is folded down by octaves instead of being clipped.
  let frequency = spec.frequency;
  while (frequency > voice.maxFrequency) {
    frequency /= 2;
  }

  const delay = context.createDelay(0.05);
  delay.delayTime.value = 1 / frequency;

  const damping = context.createBiquadFilter();
  damping.type = "lowpass";
  damping.frequency.value = clamp(frequency * voice.dampingRatio * spec.brightness, 300, 16000);

  const feedback = context.createGain();
  const periods = Math.max(4, spec.duration * frequency);
  const feedbackGain = Math.min(0.995, Math.pow(0.001, 1 / periods));
  feedback.gain.setValueAtTime(feedbackGain, spec.time);
  feedback.gain.setValueAtTime(feedbackGain, spec.time + spec.duration);
  feedback.gain.linearRampToValueAtTime(0, spec.time + spec.duration + 0.08);

  delay.connect(damping);
  damping.connect(feedback);
  feedback.connect(delay);

  const excitation = context.createBufferSource();
  excitation.buffer = whiteNoiseBuffer(context);
  const excitationGain = context.createGain();
  excitationGain.gain.setValueAtTime(spec.gain * 1.4, spec.time);
  excitationGain.gain.setValueAtTime(0, spec.time + voice.excitationSeconds);
  excitation.connect(excitationGain);
  excitationGain.connect(delay);

  const output = context.createGain();
  output.gain.setValueAtTime(1, spec.time);
  output.gain.setValueAtTime(1, spec.time + spec.duration * 0.85);
  output.gain.exponentialRampToValueAtTime(0.0001, spec.time + spec.duration + 0.06);
  delay.connect(output);
  output.connect(target);

  excitation.start(spec.time);
  excitation.stop(spec.time + voice.excitationSeconds + 0.02);

  return () => {
    feedback.disconnect();
    delay.disconnect();
    damping.disconnect();
    output.disconnect();
  };
}

function buildChirpVoice(context, target, spec) {
  const { voice } = spec.material;
  const sweepSeconds = Math.max(0.01, spec.duration * voice.timeRatio);
  const peak = spec.frequency * voice.depth;

  const oscillator = context.createOscillator();
  oscillator.type = voice.waveform;

  if (voice.shape === "rise") {
    oscillator.frequency.setValueAtTime(spec.frequency, spec.time);
    oscillator.frequency.exponentialRampToValueAtTime(peak, spec.time + sweepSeconds);
  } else if (voice.shape === "fall") {
    oscillator.frequency.setValueAtTime(peak, spec.time);
    oscillator.frequency.exponentialRampToValueAtTime(spec.frequency, spec.time + sweepSeconds);
  } else {
    oscillator.frequency.setValueAtTime(spec.frequency, spec.time);
    oscillator.frequency.exponentialRampToValueAtTime(peak, spec.time + sweepSeconds * 0.4);
    oscillator.frequency.exponentialRampToValueAtTime(
      spec.frequency * 0.85,
      spec.time + sweepSeconds,
    );
  }

  if (voice.vibratoHz > 0 && voice.vibratoCents > 0) {
    const vibrato = context.createOscillator();
    vibrato.type = "sine";
    vibrato.frequency.setValueAtTime(voice.vibratoHz, spec.time);
    const vibratoDepth = context.createGain();
    vibratoDepth.gain.setValueAtTime(voice.vibratoCents, spec.time);
    vibrato.connect(vibratoDepth);
    vibratoDepth.connect(oscillator.detune);
    vibrato.start(spec.time);
    vibrato.stop(spec.time + spec.duration + 0.05);
  }

  const envelope = context.createGain();
  applyDecayEnvelope(envelope.gain, spec.time, spec.attack, spec.gain, spec.duration);
  oscillator.connect(envelope);
  envelope.connect(target);
  oscillator.start(spec.time);
  oscillator.stop(spec.time + spec.duration + 0.05);

  if (voice.tailGain > 0) {
    const tail = context.createOscillator();
    tail.type = "sine";
    tail.frequency.setValueAtTime(peak, spec.time);
    const tailEnvelope = context.createGain();
    const tailDuration = spec.duration * 2.2;
    applyDecayEnvelope(
      tailEnvelope.gain,
      spec.time + sweepSeconds * 0.6,
      0.01,
      spec.gain * voice.tailGain,
      tailDuration,
    );
    tail.connect(tailEnvelope);
    tailEnvelope.connect(target);
    tail.start(spec.time);
    tail.stop(spec.time + sweepSeconds * 0.6 + tailDuration + 0.05);
  }
}

function buildNoiseVoice(context, target, spec) {
  const { voice } = spec.material;

  const source = context.createBufferSource();
  source.buffer = whiteNoiseBuffer(context);
  source.loop = true;

  const filter = context.createBiquadFilter();
  filter.type = voice.filterKind;
  const centre = clamp(spec.frequency * voice.centerRatio * spec.brightness, 120, 16000);
  filter.Q.value = voice.resonance + spec.grain * 1.5;
  filter.frequency.setValueAtTime(centre, spec.time);
  filter.frequency.exponentialRampToValueAtTime(
    clamp(centre * voice.sweep, 120, 16000),
    spec.time + spec.duration,
  );

  const envelope = context.createGain();
  applyDecayEnvelope(envelope.gain, spec.time, spec.attack, spec.gain * 0.9, spec.duration);

  if (voice.density > 0) {
    // NOTE: modulating the envelope gain with slow noise turns a smooth hiss
    // into an irregular rustle, which is what makes paper read as paper.
    const flutter = context.createBufferSource();
    flutter.buffer = whiteNoiseBuffer(context);
    flutter.loop = true;
    const flutterFilter = context.createBiquadFilter();
    flutterFilter.type = "lowpass";
    flutterFilter.frequency.value = 28;
    const flutterDepth = context.createGain();
    flutterDepth.gain.value = spec.gain * voice.density * 0.5;
    flutter.connect(flutterFilter);
    flutterFilter.connect(flutterDepth);
    flutterDepth.connect(envelope.gain);
    flutter.start(spec.time);
    flutter.stop(spec.time + spec.duration + 0.05);
  }

  source.connect(filter);
  filter.connect(envelope);
  envelope.connect(target);
  source.start(spec.time);
  source.stop(spec.time + spec.duration + 0.05);
}

function buildWaveVoice(context, target, spec) {
  const { voice } = spec.material;

  const envelope = context.createGain();
  applyDecayEnvelope(envelope.gain, spec.time, spec.attack, spec.gain, spec.duration);
  envelope.connect(target);

  const fundamental = context.createOscillator();
  fundamental.type = voice.waveform;
  fundamental.frequency.setValueAtTime(spec.frequency, spec.time);
  fundamental.connect(envelope);
  fundamental.start(spec.time);
  fundamental.stop(spec.time + spec.duration + 0.05);

  const partial = context.createOscillator();
  partial.type = voice.waveform;
  partial.frequency.setValueAtTime(spec.frequency * voice.partialRatio, spec.time);
  partial.detune.setValueAtTime(spec.grain * 18, spec.time);
  const partialGain = context.createGain();
  partialGain.gain.value = voice.partialGain;
  partial.connect(partialGain);
  partialGain.connect(envelope);
  partial.start(spec.time);
  partial.stop(spec.time + spec.duration + 0.05);
}

const VOICE_BUILDERS = {
  modal: buildModalVoice,
  fm: buildFmVoice,
  string: buildStringVoice,
  chirp: buildChirpVoice,
  noise: buildNoiseVoice,
  wave: buildWaveVoice,
};

// ----------------------------------------------------------------
// Note scheduling
// ----------------------------------------------------------------

/**
 * Schedule one note of a token onto an audio graph.
 *
 * @param {BaseAudioContext} context Live or offline audio context.
 * @param {AudioNode} destination Bus input to feed.
 * @param {object} spec Fully resolved note parameters.
 * @returns {Function|null} An optional teardown for feedback based voices.
 */
export function scheduleNote(context, destination, spec) {
  const { material } = spec;

  const shelf = context.createBiquadFilter();
  shelf.type = "lowshelf";
  shelf.frequency.value = 190;
  shelf.gain.value = spec.weight * 7;
  shelf.connect(destination);

  let entry = shelf;
  if (spec.grain > 0.02) {
    const shaper = context.createWaveShaper();
    shaper.curve = saturationCurve(context, spec.grain);
    shaper.oversample = "2x";
    const makeup = context.createGain();
    makeup.gain.value = saturationMakeup(spec.grain);
    shaper.connect(makeup);
    makeup.connect(shelf);
    entry = shaper;
  }

  const lowpass = context.createBiquadFilter();
  lowpass.type = "lowpass";
  lowpass.Q.value = 0.7 + spec.grain * 1.4;
  const cutoff = clamp(
    spec.frequency * material.cutoffRatio * spec.brightness * (1 - 0.28 * spec.weight),
    170,
    17000,
  );
  lowpass.frequency.setValueAtTime(cutoff, spec.time);
  lowpass.frequency.exponentialRampToValueAtTime(
    Math.max(130, cutoff * 0.3),
    spec.time + spec.duration,
  );
  lowpass.connect(entry);

  const trim = context.createGain();
  trim.gain.value = material.gainTrim;
  trim.connect(lowpass);

  const teardown = VOICE_BUILDERS[material.engine](context, trim, spec);

  if (spec.weight > 0.02) {
    const sub = context.createOscillator();
    sub.type = "sine";
    sub.frequency.setValueAtTime(spec.frequency / 2, spec.time);
    const subEnvelope = context.createGain();
    applyDecayEnvelope(
      subEnvelope.gain,
      spec.time,
      Math.max(spec.attack, 0.006),
      spec.gain * spec.weight * 0.6,
      spec.duration,
    );
    sub.connect(subEnvelope);
    subEnvelope.connect(trim);
    sub.start(spec.time);
    sub.stop(spec.time + spec.duration + 0.05);
  }

  const impactAmount = spec.transient * material.transient.amount * (1 + spec.grain * 1.1);
  if (impactAmount > 0.01) {
    const impact = context.createBufferSource();
    impact.buffer = impactBuffer(context);
    const band = context.createBiquadFilter();
    band.type = "bandpass";
    band.frequency.value = clamp(
      material.transient.toneHz * spec.brightness * (1 - 0.45 * spec.weight),
      200,
      13000,
    );
    band.Q.value = material.transient.resonance + spec.grain * 1.2;
    const impactGain = context.createGain();
    const impactDecay = material.transient.decaySeconds * (1 + spec.grain * 0.8) * (1 + spec.weight * 0.5);
    impactGain.gain.setValueAtTime(0.0001, spec.time);
    impactGain.gain.exponentialRampToValueAtTime(
      Math.max(0.002, 0.2 * impactAmount * spec.gain),
      spec.time + 0.0015,
    );
    impactGain.gain.exponentialRampToValueAtTime(0.0001, spec.time + impactDecay);
    impact.connect(band);
    band.connect(impactGain);
    impactGain.connect(entry);
    impact.start(spec.time);
    impact.stop(spec.time + impactDecay + 0.03);
  }

  const materialBreath = material.voice.breath ?? 0;
  const breath = materialBreath + Math.max(0, (spec.grain - 0.35) / 0.65) * 0.45;
  if (breath > 0.01) {
    const source = context.createBufferSource();
    source.buffer = whiteNoiseBuffer(context);
    source.loop = true;
    const band = context.createBiquadFilter();
    band.type = "bandpass";
    band.frequency.value = clamp(spec.frequency * 2.5, 200, 9000);
    band.Q.value = 1.4;
    const breathGain = context.createGain();
    const breathDuration = Math.min(spec.duration, 0.45);
    applyDecayEnvelope(
      breathGain.gain,
      spec.time,
      Math.max(spec.attack, 0.008),
      0.05 * breath * spec.gain,
      breathDuration,
    );
    source.connect(band);
    band.connect(breathGain);
    breathGain.connect(entry);
    source.start(spec.time);
    source.stop(spec.time + breathDuration + 0.04);
  }

  return teardown ?? null;
}

/**
 * Resolve a token into fully specified notes for the current palette.
 *
 * @param {object} token Token definition from the design system.
 * @param {object} material Material in use.
 * @param {object} palette Current palette settings.
 * @param {object} tuning Tuning descriptor.
 * @param {object} options Degree offset, gain scale and variation seed.
 * @returns {object[]} Resolved note specifications.
 */
export function resolveToken(token, material, palette, tuning, options = {}) {
  const degreeOffset = options.degreeOffset ?? 0;
  const gainScale = options.gainScale ?? 1;
  const variation = token.variation * (options.variationScale ?? 1);

  return token.notes.map((note) => {
    const detuneRatio = 1 + (Math.random() - 0.5) * variation * 0.03;
    const gainRatio = 1 + (Math.random() - 0.5) * variation * 0.25;
    const duration =
      note.durationSeconds * material.durationFactor * palette.hold * (1 + palette.weight * 1.05);
    const attack = clamp(
      note.attackSeconds * material.attackFactor * (1 + palette.weight * 2.6) * (1 - palette.grain * 0.3),
      0.0015,
      duration * 0.5,
    );

    return {
      material,
      offset: note.offsetSeconds,
      degree: note.degree + degreeOffset,
      frequency: frequencyForDegree(note.degree + degreeOffset, tuning) * detuneRatio,
      duration: Math.max(0.04, duration),
      gain: clamp(note.gain * gainRatio * gainScale, 0.005, 1),
      transient: note.transient,
      brightness: note.brightness * palette.brightness,
      attack,
      grain: palette.grain,
      weight: palette.weight,
      time: 0,
    };
  });
}

/**
 * Total audible length of a token, transient tail included.
 *
 * @param {object[]} notes Resolved notes.
 * @returns {number} Duration in seconds.
 */
export function tokenLength(notes) {
  return Math.max(...notes.map((note) => note.offset + note.duration)) + 0.05;
}

// ----------------------------------------------------------------
// Engine
// ----------------------------------------------------------------

/**
 * Live playback engine, owning the audio context and the output bus.
 */
export class SoundEngine {
  /**
   * @param {object} system Design system payload served by the backend.
   */
  constructor(system) {
    this.system = system;
    this.context = null;
    this.bus = null;
    this.palette = null;
    this.tuning = null;
    this.material = null;
    this.lastTriggerByToken = new Map();
    this.activeVoices = 0;
    this.onTokenPlayed = null;
  }

  /**
   * Apply a palette, rebuilding the tuning and resolving the material.
   *
   * @param {object} palette Palette settings.
   */
  setPalette(palette) {
    this.palette = palette;
    this.material = this.system.materials.find((item) => item.key === palette.materialKey);
    const scale = this.system.scales.find((item) => item.key === palette.scaleKey);
    this.tuning = {
      rootHz: palette.rootHz,
      steps: scale.steps,
      temperament: palette.temperament,
      justRatios: this.system.justRatios,
    };

    if (this.bus) {
      this.bus.input.gain.value = palette.level * (1 - 0.15 * palette.grain);
      this.bus.send.gain.value = palette.space;
    }
  }

  /** Create the audio context on the first user gesture. */
  ensureContext() {
    if (!this.context) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.context = new AudioContextClass();
      this.bus = createBus(this.context, this.palette, true);
    }
    if (this.context.state === "suspended") {
      this.context.resume();
    }
  }

  /** @returns {AnalyserNode|null} The analyser feeding the oscilloscope. */
  get analyser() {
    return this.bus ? this.bus.analyser : null;
  }

  /**
   * Play a token immediately.
   *
   * Repeatable tokens are throttled so that a fast drag cannot stack
   * dozens of overlapping voices and duck the whole bus.
   *
   * @param {object} token Token definition.
   * @param {object} options Degree offset and gain scale.
   * @returns {object[]|null} The resolved notes, or null when throttled.
   */
  play(token, options = {}) {
    this.ensureContext();
    const now = this.context.currentTime;

    if (token.behaviour === "repeatable") {
      const last = this.lastTriggerByToken.get(token.tokenId) ?? 0;
      if (now - last < REPEAT_INTERVAL_SECONDS) {
        return null;
      }
      this.lastTriggerByToken.set(token.tokenId, now);
    }

    if (this.activeVoices > VOICE_BUDGET) {
      return null;
    }

    const notes = resolveToken(token, this.material, this.palette, this.tuning, options);
    const start = now + 0.015;
    const teardowns = [];

    notes.forEach((note) => {
      const teardown = scheduleNote(this.context, this.bus.input, { ...note, time: start + note.offset });
      if (teardown) {
        teardowns.push(teardown);
      }
    });

    this.activeVoices += notes.length;
    const lifetime = tokenLength(notes);
    window.setTimeout(() => {
      this.activeVoices = Math.max(0, this.activeVoices - notes.length);
      teardowns.forEach((teardown) => teardown());
    }, (lifetime + 0.4) * 1000);

    if (this.onTokenPlayed) {
      this.onTokenPlayed(token, notes);
    }
    return notes;
  }

  /**
   * Open a held voice driven by a progress value.
   *
   * Used for long presses and pull gestures, where the sound has to follow
   * the gesture instead of being fired once at its start.
   *
   * @param {object} token Token definition with the sustained behaviour.
   * @param {object} options Degree offset.
   * @returns {object} A handle exposing update and release.
   */
  startSustain(token, options = {}) {
    this.ensureContext();
    const context = this.context;
    const time = context.currentTime + 0.01;
    const note = token.notes[0];
    const degree = note.degree + (options.degreeOffset ?? 0);
    const baseFrequency = frequencyForDegree(degree, this.tuning);

    const output = context.createGain();
    output.gain.setValueAtTime(0.0001, time);
    output.gain.exponentialRampToValueAtTime(note.gain * 0.35, time + 0.05);
    output.connect(this.bus.input);

    const lowpass = context.createBiquadFilter();
    lowpass.type = "lowpass";
    lowpass.Q.value = 1.2;
    lowpass.frequency.setValueAtTime(baseFrequency * 2.2, time);
    lowpass.connect(output);

    const fundamental = context.createOscillator();
    fundamental.type = "sine";
    fundamental.frequency.setValueAtTime(baseFrequency, time);
    fundamental.connect(lowpass);

    const upper = context.createOscillator();
    upper.type = "sine";
    upper.frequency.setValueAtTime(baseFrequency * 1.5, time);
    const upperGain = context.createGain();
    upperGain.gain.setValueAtTime(0.0001, time);
    upper.connect(upperGain);
    upperGain.connect(lowpass);

    // NOTE: the tremolo speeds up as the gesture approaches its threshold.
    // A rising rate reads as tension far more clearly than a rising level.
    const tremolo = context.createOscillator();
    tremolo.type = "sine";
    tremolo.frequency.setValueAtTime(4, time);
    const tremoloDepth = context.createGain();
    tremoloDepth.gain.setValueAtTime(0.0001, time);
    tremolo.connect(tremoloDepth);
    tremoloDepth.connect(output.gain);

    fundamental.start(time);
    upper.start(time);
    tremolo.start(time);

    const stopAll = (at) => {
      fundamental.stop(at);
      upper.stop(at);
      tremolo.stop(at);
    };

    return {
      update: (progress) => {
        const clamped = clamp(progress, 0, 1);
        const at = context.currentTime;
        lowpass.frequency.setTargetAtTime(baseFrequency * (2.2 + clamped * 9), at, 0.05);
        output.gain.setTargetAtTime(note.gain * (0.35 + clamped * 0.75), at, 0.05);
        upperGain.gain.setTargetAtTime(0.05 + clamped * 0.4, at, 0.08);
        tremolo.frequency.setTargetAtTime(4 + clamped * 16, at, 0.1);
        tremoloDepth.gain.setTargetAtTime(note.gain * clamped * 0.35, at, 0.1);
        fundamental.detune.setTargetAtTime(clamped * 30, at, 0.12);
      },
      release: () => {
        const at = context.currentTime;
        output.gain.cancelScheduledValues(at);
        output.gain.setValueAtTime(Math.max(0.0002, output.gain.value), at);
        output.gain.exponentialRampToValueAtTime(0.0001, at + 0.08);
        stopAll(at + 0.12);
        window.setTimeout(() => output.disconnect(), 400);
      },
    };
  }

  /**
   * Render a token offline, ready to be encoded as a WAV file.
   *
   * @param {object} token Token definition.
   * @returns {Promise<AudioBuffer>} The rendered mono buffer.
   */
  async render(token) {
    const OfflineContextClass = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    const sampleRate = 44100;
    const notes = resolveToken(token, this.material, this.palette, this.tuning, {
      variationScale: 0,
    });
    const seconds = tokenLength(notes) + 1.9;
    const context = new OfflineContextClass(1, Math.ceil(seconds * sampleRate), sampleRate);
    const bus = createBus(context, this.palette, false);

    notes.forEach((note) => {
      scheduleNote(context, bus.input, { ...note, time: 0.02 + note.offset });
    });

    return context.startRendering();
  }
}

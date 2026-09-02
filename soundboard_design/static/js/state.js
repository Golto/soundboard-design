/**
 * The palette store.
 *
 * A single mutable palette drives the whole interface. Every panel
 * subscribes to it rather than reading each other, so a change made from
 * the test bench, a preset or a slider reaches everything at once.
 */

/** Ordered keys of the numeric palette settings exposed as sliders. */
export const SLIDER_KEYS = ["rootHz", "grain", "weight", "brightness", "hold", "space", "level"];

export class PaletteStore {
  /**
   * @param {object} system Design system payload served by the backend.
   */
  constructor(system) {
    this.system = system;
    this.listeners = new Set();
    const preset = system.presets.find((item) => item.key === system.defaultPresetKey);
    this.palette = { ...preset.palette };
  }

  /**
   * Register a listener called after every change.
   *
   * @param {Function} listener Callback receiving the current palette.
   * @returns {Function} An unsubscribe function.
   */
  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    this.listeners.forEach((listener) => listener(this.palette));
  }

  /**
   * Update one palette field.
   *
   * @param {string} key Field name.
   * @param {number|string} value New value.
   */
  set(key, value) {
    this.palette = { ...this.palette, [key]: value };
    this.notify();
  }

  /**
   * Replace the whole palette with the one carried by a preset.
   *
   * @param {string} key Preset identifier.
   */
  applyPreset(key) {
    const preset = this.system.presets.find((item) => item.key === key);
    if (!preset) {
      return;
    }
    this.palette = { ...preset.palette };
    this.notify();
  }

  /**
   * Identify the preset matching the current palette exactly.
   *
   * @returns {string|null} The preset key, or null once the palette has
   *     been edited away from every preset.
   */
  matchingPresetKey() {
    const match = this.system.presets.find((preset) =>
      Object.entries(preset.palette).every(([key, value]) => {
        const current = this.palette[key];
        if (typeof value === "number") {
          return Math.abs(current - value) < 1e-6;
        }
        return current === value;
      }),
    );
    return match ? match.key : null;
  }

  /** @returns {object} The material currently selected. */
  get material() {
    return this.system.materials.find((item) => item.key === this.palette.materialKey);
  }

  /** @returns {object} The scale currently selected. */
  get scale() {
    return this.system.scales.find((item) => item.key === this.palette.scaleKey);
  }
}

/**
 * Build a flat index of every token, keyed by identifier.
 *
 * @param {object} system Design system payload.
 * @returns {Map<string, object>} Tokens by identifier.
 */
export function indexTokens(system) {
  const index = new Map();
  system.categories.forEach((category) => {
    category.tokens.forEach((token) => index.set(token.tokenId, token));
  });
  return index;
}

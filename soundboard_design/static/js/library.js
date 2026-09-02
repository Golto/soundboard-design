/**
 * The token library.
 *
 * Tokens are listed by interaction family, each with the sentence that
 * tells a designer when to fire it. Behaviour tags only appear when they
 * carry information: a tag on every tile would be decoration.
 */

import { downloadBlob, encodeWav, fileNameForToken } from "./export.js";

const BEHAVIOUR_TAGS = {
  repeatable: "rafale",
  sustained: "tenu",
};

export class Library {
  /**
   * @param {PaletteStore} store Palette store.
   * @param {SoundEngine} engine Engine used for playback and rendering.
   * @param {object} controls Play helper bound to the engine.
   */
  constructor(store, engine, controls) {
    this.store = store;
    this.engine = engine;
    this.controls = controls;
    this.host = document.querySelector("[data-panel='library']");
    this.render();
  }

  createTile(token) {
    const tile = document.createElement("div");
    tile.className = "tile";

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "tile-trigger";

    const heading = document.createElement("span");
    heading.className = "tile-label";
    heading.textContent = token.label;

    const identifier = document.createElement("span");
    identifier.className = "tile-id";
    identifier.textContent = token.tokenId;

    const usage = document.createElement("span");
    usage.className = "tile-usage";
    usage.textContent = token.usage;

    trigger.append(heading, identifier, usage);

    const tags = [];
    if (BEHAVIOUR_TAGS[token.behaviour]) {
      tags.push(BEHAVIOUR_TAGS[token.behaviour]);
    }
    if (token.tracksValue) {
      tags.push("suit la valeur");
    }
    if (tags.length > 0) {
      const tagRow = document.createElement("span");
      tagRow.className = "tile-tags";
      tags.forEach((text) => {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = text;
        tagRow.append(tag);
      });
      trigger.append(tagRow);
    }

    trigger.addEventListener("click", () => {
      if (token.behaviour === "sustained") {
        this.auditionSustained(token, trigger);
        return;
      }
      this.controls.play(token.tokenId);
      trigger.classList.add("is-hit");
      window.setTimeout(() => trigger.classList.remove("is-hit"), 180);
    });

    const download = document.createElement("button");
    download.type = "button";
    download.className = "tile-download";
    download.textContent = "WAV";
    download.setAttribute("aria-label", `Télécharger ${token.tokenId} en WAV`);
    download.disabled = token.behaviour === "sustained";
    download.addEventListener("click", async () => {
      download.disabled = true;
      try {
        const buffer = await this.engine.render(token);
        downloadBlob(encodeWav(buffer), `${fileNameForToken(token.tokenId)}.wav`);
      } finally {
        download.disabled = false;
      }
    });

    tile.append(trigger, download);
    return tile;
  }

  /**
   * Audition a sustained token by sweeping its progress automatically.
   *
   * @param {object} token Sustained token definition.
   * @param {HTMLElement} trigger Tile button to mark as active.
   */
  auditionSustained(token, trigger) {
    const handle = this.engine.startSustain(token);
    const startedAt = performance.now();
    trigger.classList.add("is-hit");

    const step = () => {
      const progress = (performance.now() - startedAt) / 1400;
      if (progress >= 1) {
        handle.release();
        trigger.classList.remove("is-hit");
        return;
      }
      handle.update(progress);
      window.requestAnimationFrame(step);
    };
    window.requestAnimationFrame(step);
  }

  render() {
    const sections = this.store.system.categories.map((category) => {
      const section = document.createElement("section");
      section.className = "category";

      const header = document.createElement("header");
      header.className = "category-head";

      const title = document.createElement("h3");
      title.textContent = category.label;

      const count = document.createElement("span");
      count.className = "category-count";
      count.textContent = String(category.tokens.length);

      const description = document.createElement("p");
      description.className = "category-description";
      description.textContent = category.description;

      const row = document.createElement("div");
      row.className = "category-title-row";
      row.append(title, count);
      header.append(row, description);

      const grid = document.createElement("div");
      grid.className = "tile-grid";
      category.tokens.forEach((token) => grid.append(this.createTile(token)));

      section.append(header, grid);
      return section;
    });

    this.host.replaceChildren(...sections);
  }
}

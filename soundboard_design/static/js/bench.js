/**
 * The test bench.
 *
 * Real components wired to the palette. A grid of one shot buttons tells
 * you what a sound is; only a slider you can actually drag tells you
 * whether its tick survives forty repeats, and only a long press you have
 * to hold tells you whether the tension resolves.
 */

const SLIDER_STEPS = 20;
const SLIDER_DETENTS = [0, 10, 20];
const CAROUSEL_LABELS = ["Aperçu", "Matières", "Gammes", "Jetons", "Banc d'essai", "Export"];
const LONG_PRESS_MILLISECONDS = 800;
const PULL_THRESHOLD_PIXELS = 78;
const PULL_MAX_PIXELS = 120;

/**
 * Wire every component of the test bench.
 *
 * @param {object} controls Play and sustain helpers bound to the engine.
 */
export function initialiseBench(controls) {
  initialiseSlider(controls);
  initialiseCarousel(controls);
  initialiseDisclosure(controls);
  initialiseLongPress(controls);
  initialiseToggle(controls);
  initialisePull(controls);
}

// ----------------------------------------------------------------
// Slider
// ----------------------------------------------------------------

function initialiseSlider(controls) {
  const track = document.querySelector("[data-bench='slider']");
  const fill = track.querySelector(".bench-slider-fill");
  const handle = track.querySelector(".bench-slider-handle");
  const readout = document.querySelector("[data-bench-readout='slider']");

  let step = 8;
  let dragging = false;

  const render = () => {
    const ratio = step / SLIDER_STEPS;
    fill.style.width = `${ratio * 100}%`;
    handle.style.left = `${ratio * 100}%`;
    readout.textContent = `${step * 5} %`;
    track.setAttribute("aria-valuenow", String(step * 5));
  };

  const moveTo = (nextStep) => {
    const clamped = Math.max(0, Math.min(SLIDER_STEPS, nextStep));
    if (clamped === step) {
      if (dragging && (clamped === 0 || clamped === SLIDER_STEPS)) {
        controls.play("slider.limit");
      }
      return;
    }
    step = clamped;
    render();

    const offset = Math.round((step / SLIDER_STEPS) * 7);
    if (SLIDER_DETENTS.includes(step)) {
      controls.play("slider.detent", { degreeOffset: offset });
    } else {
      controls.play("slider.tick", { degreeOffset: offset });
    }
  };

  const stepFromEvent = (event) => {
    const bounds = track.getBoundingClientRect();
    const ratio = (event.clientX - bounds.left) / bounds.width;
    return Math.round(Math.max(0, Math.min(1, ratio)) * SLIDER_STEPS);
  };

  track.addEventListener("pointerdown", (event) => {
    dragging = true;
    track.setPointerCapture(event.pointerId);
    track.classList.add("is-active");
    controls.play("slider.grab");
    moveTo(stepFromEvent(event));
  });

  track.addEventListener("pointermove", (event) => {
    if (dragging) {
      moveTo(stepFromEvent(event));
    }
  });

  const endDrag = () => {
    if (!dragging) {
      return;
    }
    dragging = false;
    track.classList.remove("is-active");
    controls.play("slider.release", { degreeOffset: Math.round((step / SLIDER_STEPS) * 7) });
  };

  track.addEventListener("pointerup", endDrag);
  track.addEventListener("pointercancel", endDrag);

  track.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight" || event.key === "ArrowUp") {
      event.preventDefault();
      dragging = true;
      moveTo(step + 1);
      dragging = false;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowDown") {
      event.preventDefault();
      dragging = true;
      moveTo(step - 1);
      dragging = false;
    }
  });

  render();
}

// ----------------------------------------------------------------
// Carousel
// ----------------------------------------------------------------

function initialiseCarousel(controls) {
  const viewport = document.querySelector("[data-bench='carousel']");
  const strip = viewport.querySelector(".bench-carousel-strip");
  const readout = document.querySelector("[data-bench-readout='carousel']");
  const previousButton = document.querySelector("[data-bench-action='carousel-previous']");
  const nextButton = document.querySelector("[data-bench-action='carousel-next']");
  const loopToggle = document.querySelector("[data-bench-action='carousel-loop']");

  let index = 0;
  let looping = true;

  strip.innerHTML = CAROUSEL_LABELS.map(
    (label, position) =>
      `<div class="bench-card"><span class="bench-card-index">${position + 1}</span>${label}</div>`,
  ).join("");

  const render = () => {
    strip.style.transform = `translateX(calc(${-index} * (var(--card-width) + var(--card-gap))))`;
    readout.textContent = `${index + 1} / ${CAROUSEL_LABELS.length}`;
    loopToggle.setAttribute("aria-pressed", String(looping));
  };

  const goTo = (nextIndex, direction) => {
    const last = CAROUSEL_LABELS.length - 1;

    if (nextIndex < 0 || nextIndex > last) {
      if (!looping) {
        controls.play("carousel.end");
        return;
      }
      index = nextIndex < 0 ? last : 0;
      render();
      controls.play("carousel.wrap");
      return;
    }

    index = nextIndex;
    render();
    const token = direction > 0 ? "carousel.next" : "carousel.previous";
    controls.play(token, { degreeOffset: index });
  };

  previousButton.addEventListener("click", () => goTo(index - 1, -1));
  nextButton.addEventListener("click", () => goTo(index + 1, 1));
  loopToggle.addEventListener("click", () => {
    looping = !looping;
    render();
  });

  render();
}

// ----------------------------------------------------------------
// Disclosure
// ----------------------------------------------------------------

function initialiseDisclosure(controls) {
  const items = document.querySelectorAll("[data-bench='disclosure'] .bench-disclosure-item");

  items.forEach((item) => {
    const trigger = item.querySelector(".bench-disclosure-trigger");
    trigger.addEventListener("click", () => {
      const isOpen = item.classList.toggle("is-open");
      trigger.setAttribute("aria-expanded", String(isOpen));
      controls.play(isOpen ? "disclosure.expand" : "disclosure.collapse");
    });
  });
}

// ----------------------------------------------------------------
// Long press
// ----------------------------------------------------------------

function initialiseLongPress(controls) {
  const button = document.querySelector("[data-bench='long-press']");
  const ring = button.querySelector(".bench-press-fill");
  const label = button.querySelector(".bench-press-label");

  let handle = null;
  let startedAt = 0;
  let frame = 0;
  let committed = false;

  const stop = () => {
    window.cancelAnimationFrame(frame);
    if (handle) {
      handle.release();
      handle = null;
    }
    ring.style.width = "0%";
    button.classList.remove("is-pressing");
  };

  const tick = () => {
    const progress = Math.min(1, (performance.now() - startedAt) / LONG_PRESS_MILLISECONDS);
    ring.style.width = `${progress * 100}%`;
    if (handle) {
      handle.update(progress);
    }

    if (progress >= 1 && !committed) {
      committed = true;
      stop();
      controls.play("press.commit");
      label.textContent = "Déclenché";
      window.setTimeout(() => {
        label.textContent = "Maintenir pour supprimer";
      }, 1100);
      return;
    }
    frame = window.requestAnimationFrame(tick);
  };

  button.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    button.setPointerCapture(event.pointerId);
    committed = false;
    startedAt = performance.now();
    button.classList.add("is-pressing");
    label.textContent = "Continuez…";
    handle = controls.sustain("press.hold");
    frame = window.requestAnimationFrame(tick);
  });

  const cancel = () => {
    if (committed || !handle) {
      return;
    }
    stop();
    controls.play("press.abort");
    label.textContent = "Maintenir pour supprimer";
  };

  button.addEventListener("pointerup", cancel);
  button.addEventListener("pointercancel", cancel);
  button.addEventListener("pointerleave", cancel);
}

// ----------------------------------------------------------------
// Toggle
// ----------------------------------------------------------------

function initialiseToggle(controls) {
  const toggle = document.querySelector("[data-bench='toggle']");

  toggle.addEventListener("click", () => {
    const isOn = toggle.getAttribute("aria-checked") !== "true";
    toggle.setAttribute("aria-checked", String(isOn));
    controls.play(isOn ? "toggle.on" : "toggle.off");
  });
}

// ----------------------------------------------------------------
// Pull to refresh
// ----------------------------------------------------------------

function initialisePull(controls) {
  const zone = document.querySelector("[data-bench='pull']");
  const sheet = zone.querySelector(".bench-pull-sheet");
  const label = zone.querySelector(".bench-pull-label");

  let handle = null;
  let origin = 0;
  let distance = 0;
  let dragging = false;

  const reset = () => {
    dragging = false;
    distance = 0;
    sheet.style.transform = "translateY(0px)";
    if (handle) {
      handle.release();
      handle = null;
    }
  };

  zone.addEventListener("pointerdown", (event) => {
    dragging = true;
    origin = event.clientY;
    zone.setPointerCapture(event.pointerId);
    handle = controls.sustain("refresh.pull");
    label.textContent = "Tirez vers le bas";
  });

  zone.addEventListener("pointermove", (event) => {
    if (!dragging) {
      return;
    }
    distance = Math.max(0, Math.min(PULL_MAX_PIXELS, event.clientY - origin));
    sheet.style.transform = `translateY(${distance}px)`;
    if (handle) {
      handle.update(distance / PULL_THRESHOLD_PIXELS);
    }
    label.textContent =
      distance >= PULL_THRESHOLD_PIXELS ? "Relâchez pour rafraîchir" : "Tirez vers le bas";
  });

  const release = () => {
    if (!dragging) {
      return;
    }
    const reached = distance >= PULL_THRESHOLD_PIXELS;
    reset();
    if (reached) {
      controls.play("refresh.release");
      label.textContent = "Actualisé";
      window.setTimeout(() => {
        label.textContent = "Tirez vers le bas";
      }, 1100);
    } else {
      label.textContent = "Tirez vers le bas";
    }
  };

  zone.addEventListener("pointerup", release);
  zone.addEventListener("pointercancel", release);
}

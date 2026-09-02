/**
 * The oscilloscope.
 *
 * The only graphic on the page is the signal itself, read straight from
 * the analyser. It idles as a flat line and only moves when something is
 * actually playing, which makes it a live confirmation that a gesture
 * produced sound rather than a decoration.
 */

const IDLE_THRESHOLD = 0.002;
const IDLE_FRAMES_BEFORE_REST = 45;

export class Oscilloscope {
  /**
   * @param {HTMLCanvasElement} canvas Canvas to draw into.
   */
  constructor(canvas) {
    this.canvas = canvas;
    this.drawingContext = canvas.getContext("2d");
    this.analyser = null;
    this.samples = null;
    this.idleFrames = IDLE_FRAMES_BEFORE_REST;
    this.running = false;
    this.resize();
    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    const ratio = window.devicePixelRatio || 1;
    const bounds = this.canvas.getBoundingClientRect();
    this.canvas.width = Math.max(1, Math.floor(bounds.width * ratio));
    this.canvas.height = Math.max(1, Math.floor(bounds.height * ratio));
    this.drawingContext.setTransform(ratio, 0, 0, ratio, 0, 0);
    this.width = bounds.width;
    this.height = bounds.height;
    this.draw();
  }

  /**
   * Attach the engine analyser and start the drawing loop.
   *
   * @param {AnalyserNode} analyser Analyser sitting after the compressor.
   */
  attach(analyser) {
    if (!analyser || this.analyser === analyser) {
      return;
    }
    this.analyser = analyser;
    this.samples = new Float32Array(analyser.fftSize);
    if (!this.running) {
      this.running = true;
      this.loop();
    }
  }

  loop() {
    this.draw();
    window.requestAnimationFrame(() => this.loop());
  }

  readPeak() {
    if (!this.analyser) {
      return 0;
    }
    this.analyser.getFloatTimeDomainData(this.samples);
    let peak = 0;
    for (let index = 0; index < this.samples.length; index += 1) {
      const value = Math.abs(this.samples[index]);
      if (value > peak) {
        peak = value;
      }
    }
    return peak;
  }

  draw() {
    const context = this.drawingContext;
    const styles = getComputedStyle(document.documentElement);
    const line = styles.getPropertyValue("--line").trim() || "#2E2B29";
    const accent = styles.getPropertyValue("--accent").trim() || "#FF6A1F";
    const middle = this.height / 2;

    context.clearRect(0, 0, this.width, this.height);

    context.strokeStyle = line;
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(0, middle);
    context.lineTo(this.width, middle);
    context.stroke();

    const peak = this.readPeak();
    if (peak < IDLE_THRESHOLD) {
      this.idleFrames += 1;
    } else {
      this.idleFrames = 0;
    }
    if (!this.samples || this.idleFrames > IDLE_FRAMES_BEFORE_REST) {
      return;
    }

    const amplitude = middle * 0.86;
    context.strokeStyle = accent;
    context.lineWidth = 1.5;
    context.lineJoin = "round";
    context.beginPath();

    const step = this.samples.length / this.width;
    for (let column = 0; column < this.width; column += 1) {
      const value = this.samples[Math.floor(column * step)];
      const y = middle - value * amplitude;
      if (column === 0) {
        context.moveTo(column, y);
      } else {
        context.lineTo(column, y);
      }
    }
    context.stroke();
  }
}

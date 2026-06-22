// Slide 08: Model architecture - 4 encoders + 3 decoders
// Layout: Process / Architecture diagram

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("THE MODEL", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Multi-encoder in, split-decoder out", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Input side: 4 encoders stacked vertically
  slide.addText("INPUT  /  4 ENCODERS", {
    x: 0.5, y: 1.65, w: 2.2, h: 0.35,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "center", valign: "middle", charSpacing: 2, bold: true, margin: 0
  });

  const encoders = [
    { tag: "CURRENT", desc: "starting pose" },
    { tag: "TARGET", desc: "ending pose" },
    { tag: "OFFSET", desc: "diff between them" },
    { tag: "FUTURE", desc: "trajectory past target" }
  ];

  encoders.forEach((e, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: 2.05 + i * 0.65, w: 2.2, h: 0.55,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.06
    });
    slide.addText(e.tag, {
      x: 0.5, y: 2.05 + i * 0.65, w: 2.2, h: 0.3,
      fontSize: 10, fontFace: "Arial Black", color: theme.accent,
      align: "center", valign: "middle", bold: true, charSpacing: 2, margin: 0
    });
    slide.addText(e.desc, {
      x: 0.5, y: 2.32 + i * 0.65, w: 2.2, h: 0.25,
      fontSize: 9, fontFace: "Arial", color: theme.primary,
      align: "center", valign: "middle", margin: 0
    });
  });

  // Middle: LSTM core
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.7, y: 2.4, w: 2.6, h: 1.5,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("LSTM CORE", {
    x: 3.7, y: 2.5, w: 2.6, h: 0.35,
    fontSize: 12, fontFace: "Arial Black", color: theme.accent,
    align: "center", valign: "middle", bold: true, charSpacing: 3, margin: 0
  });
  slide.addText("frame-by-frame", {
    x: 3.7, y: 2.85, w: 2.6, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: "FFFFFF",
    align: "center", valign: "middle", margin: 0
  });
  slide.addText("sequential inference", {
    x: 3.7, y: 3.15, w: 2.6, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: "FFFFFF",
    align: "center", valign: "middle", margin: 0
  });
  slide.addText("80% of weights", {
    x: 3.7, y: 3.45, w: 2.6, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.light,
    align: "center", valign: "middle", italic: true, margin: 0
  });

  // Connector arrows encoders -> LSTM (just two sample arrows)
  slide.addShape(pres.shapes.LINE, {
    x: 2.7, y: 2.95, w: 1.0, h: 0,
    line: { color: theme.accent, width: 2 }
  });
  slide.addShape(pres.shapes.LINE, {
    x: 2.7, y: 3.45, w: 1.0, h: 0,
    line: { color: theme.accent, width: 2 }
  });

  // Output side: 3 decoders
  slide.addText("OUTPUT  /  3 DECODERS", {
    x: 7.3, y: 1.65, w: 2.2, h: 0.35,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "center", valign: "middle", charSpacing: 2, bold: true, margin: 0
  });

  const decoders = [
    { tag: "MoE", desc: "transition frames" },
    { tag: "LOWER", desc: "legs - kills sliding" },
    { tag: "UPPER + FACE", desc: "torso, arms, expression" }
  ];

  decoders.forEach((d, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 7.3, y: 2.05 + i * 0.85, w: 2.2, h: 0.75,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
      rectRadius: 0.06
    });
    slide.addText(d.tag, {
      x: 7.3, y: 2.1 + i * 0.85, w: 2.2, h: 0.35,
      fontSize: 12, fontFace: "Arial Black", color: theme.primary,
      align: "center", valign: "middle", bold: true, margin: 0
    });
    slide.addText(d.desc, {
      x: 7.3, y: 2.45 + i * 0.85, w: 2.2, h: 0.3,
      fontSize: 9, fontFace: "Arial", color: theme.primary,
      align: "center", valign: "middle", margin: 0
    });
  });

  // Connector arrow LSTM -> decoders
  slide.addShape(pres.shapes.LINE, {
    x: 6.3, y: 3.15, w: 1.0, h: 0,
    line: { color: theme.accent, width: 2 }
  });

  // Bottom callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.85, w: 9.0, h: 0.55,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.06
  });
  slide.addText("Key trick: the lower-body decoder is specialized - it's the only one that knows about foot contact.", {
    x: 0.7, y: 4.85, w: 8.6, h: 0.55,
    fontSize: 11, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "middle", italic: true, margin: 0
  });

  slide.addText("08", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
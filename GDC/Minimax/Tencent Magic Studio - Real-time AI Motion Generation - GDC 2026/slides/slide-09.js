// Slide 09: Performance numbers - Data viz
// Layout: Comparison stats + table

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("PERFORMANCE", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("It fits in the frame budget", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Big stat callouts (3 of them in a row)
  const stats = [
    { num: "0.4 ms", label: "Inference time per frame after INT8 quantization" },
    { num: "6 MB", label: "Model size on disk (down from 15 MB FP32)" },
    { num: "< 1", label: "Position error in game units - invisible to players" }
  ];

  stats.forEach((s, i) => {
    const x = 0.5 + i * 3.05;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.7, w: 2.9, h: 1.6,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.08
    });
    slide.addText(s.num, {
      x: x + 0.1, y: 1.8, w: 2.7, h: 0.85,
      fontSize: 40, fontFace: "Arial Black", color: theme.accent,
      align: "center", valign: "middle", bold: true, margin: 0
    });
    slide.addText(s.label, {
      x: x + 0.15, y: 2.65, w: 2.6, h: 0.6,
      fontSize: 10, fontFace: "Arial", color: theme.primary,
      align: "center", valign: "middle", margin: 0
    });
  });

  // FP32 vs INT8 comparison bar
  slide.addText("FP32  vs  INT8 (quantized)", {
    x: 0.5, y: 3.5, w: 9, h: 0.35,
    fontSize: 13, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // FP32 row
  slide.addText("FP32", {
    x: 0.5, y: 3.95, w: 0.7, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.3, y: 4.0, w: 6.0, h: 0.25,
    fill: { color: theme.secondary }, line: { color: theme.secondary, width: 0 },
    rectRadius: 0.03
  });
  slide.addText("15 MB  /  0.75 ms", {
    x: 7.4, y: 3.95, w: 2.1, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", margin: 0
  });

  // INT8 row
  slide.addText("INT8", {
    x: 0.5, y: 4.4, w: 0.7, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.3, y: 4.45, w: 2.4, h: 0.25,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
    rectRadius: 0.03
  });
  slide.addText("6 MB  /  0.4 ms  (60% smaller, ~2x faster)", {
    x: 3.85, y: 4.4, w: 5.7, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Footnote
  slide.addText("Quantization targets the LSTM layers (80% of weights) where it preserves quality best.", {
    x: 0.5, y: 4.95, w: 9.0, h: 0.3,
    fontSize: 9, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  slide.addText("09", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
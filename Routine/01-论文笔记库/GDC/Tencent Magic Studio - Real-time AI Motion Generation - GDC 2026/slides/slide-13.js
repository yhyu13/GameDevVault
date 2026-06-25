// Slide 13: Closing - Takeaways
// Layout: Split recap (key takeaways + bigger picture)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("TAKEAWAYS", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("What to steal for your own pipeline", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Left column: 5 takeaways
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.65, w: 5.5, h: 3.4,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.1
  });
  slide.addText("For developers", {
    x: 0.75, y: 1.78, w: 5.0, h: 0.4,
    fontSize: 16, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  const takeaways = [
    "Replace mocap stages with 7 cameras + IMU + triangulation. The data does not need a studio.",
    "Quantize the LSTM-heavy model to INT8 - 60% smaller, 2x faster, quality intact.",
    "Split the decoder: one specialized lower-body branch kills the sliding-foot artifact for good.",
    "Run inference async - the render thread must never block on the model.",
    "Treat the model as a reference-set multiplier, not a replacement for hero animation."
  ];

  takeaways.forEach((t, i) => {
    slide.addShape(pres.shapes.OVAL, {
      x: 0.85, y: 2.35 + i * 0.5, w: 0.18, h: 0.18,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
    });
    slide.addText(t, {
      x: 1.15, y: 2.27 + i * 0.5, w: 4.7, h: 0.45,
      fontSize: 11, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "middle", margin: 0
    });
  });

  // Right column: the bigger picture
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.2, y: 1.65, w: 3.3, h: 3.4,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.1
  });
  slide.addText("The bigger picture", {
    x: 6.45, y: 1.78, w: 2.9, h: 0.4,
    fontSize: 16, fontFace: "Arial Black", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  const points = [
    { num: "01", text: "AI in production is no longer a research prototype - it's shipping in a free-to-play fighting game in 2026." },
    { num: "02", text: "The animation pipeline's biggest win was not in quality alone - it was asset-coverage math going from 1:1 to 0.48:1." },
    { num: "03", text: "Tencent's AI team is built around products, not papers. Every project picks its AI direction from its own pain points." }
  ];

  points.forEach((p, i) => {
    slide.addText(p.num, {
      x: 6.45, y: 2.3 + i * 0.95, w: 0.6, h: 0.4,
      fontSize: 16, fontFace: "Arial Black", color: theme.accent,
      align: "left", valign: "middle", bold: true, margin: 0
    });
    slide.addText(p.text, {
      x: 7.05, y: 2.3 + i * 0.95, w: 2.4, h: 0.85,
      fontSize: 10, fontFace: "Arial", color: "FFFFFF",
      align: "left", valign: "top", margin: 0
    });
  });

  // Footer quote
  slide.addText('"The path shifts from the engine playing back motion to the engine generating motion in real time."', {
    x: 0.5, y: 5.15, w: 8.5, h: 0.35,
    fontSize: 11, fontFace: "Georgia", color: theme.secondary,
    align: "center", valign: "middle", italic: true, margin: 0
  });

  slide.addText("13", {
    x: 9.3, y: 5.15, w: 0.5, h: 0.35,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
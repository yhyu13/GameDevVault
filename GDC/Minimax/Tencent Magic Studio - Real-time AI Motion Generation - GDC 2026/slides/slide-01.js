// Slide 01: Cover Page
// Topic: Real-time AI Motion Generation for fighting games at GDC 2026
// Layout: Asymmetric Left-Right

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Right-side accent panel
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.2, y: 0, w: 3.8, h: 5.625,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 }
  });

  // Stylized "transition" diagram on right (start pose -> AI -> end pose)
  // Start pose box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.55, y: 1.4, w: 1.2, h: 1.2,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("A", {
    x: 6.55, y: 1.4, w: 1.2, h: 1.2,
    fontSize: 48, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // AI arrow box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 7.9, y: 1.4, w: 1.4, h: 1.2,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("AI", {
    x: 7.9, y: 1.4, w: 1.4, h: 0.6,
    fontSize: 22, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });
  slide.addText("0.4 ms", {
    x: 7.9, y: 1.95, w: 1.4, h: 0.55,
    fontSize: 12, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", margin: 0
  });

  // End pose box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 9.45, y: 1.4, w: 0.5, h: 1.2,
    fill: { color: "FFFFFF" }, line: { color: theme.accent, width: 1.5 },
    rectRadius: 0.08
  });

  // Tag label
  slide.addText("GDC 2026  /  MAIN FORUM", {
    x: 6.55, y: 0.5, w: 3.3, h: 0.4,
    fontSize: 11, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", charSpacing: 4, margin: 0
  });

  // Subtitle on right
  slide.addText("The first real-time", {
    x: 6.55, y: 3.0, w: 3.3, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", margin: 0
  });
  slide.addText("AI motion system", {
    x: 6.55, y: 3.35, w: 3.3, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", margin: 0
  });
  slide.addText("in a shipped fighting game", {
    x: 6.55, y: 3.7, w: 3.3, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Left side: eyebrow + main title
  slide.addText("TENCENT MAGIC STUDIO  /  GDC 2026", {
    x: 0.5, y: 0.5, w: 5.5, h: 0.4,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 3, bold: true, margin: 0
  });

  slide.addText("Real-time AI", {
    x: 0.5, y: 1.4, w: 5.5, h: 0.9,
    fontSize: 44, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("Motion Generation", {
    x: 0.5, y: 2.25, w: 5.5, h: 0.9,
    fontSize: 44, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Accent underline
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.2, w: 0.7, h: 0.06,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  // Subtitle
  slide.addText("Building a kung fu animation pipeline where the engine generates motion on demand instead of playing it back.", {
    x: 0.5, y: 3.4, w: 5.5, h: 0.7,
    fontSize: 14, fontFace: "Georgia", color: theme.secondary,
    align: "left", valign: "top", italic: true, margin: 0
  });

  // Speaker block
  slide.addText("Speaker:  Liao Shiyang", {
    x: 0.5, y: 4.4, w: 5.5, h: 0.3,
    fontSize: 13, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("AI Lead  /  Tencent Magic Studio Group", {
    x: 0.5, y: 4.7, w: 5.5, h: 0.3,
    fontSize: 11, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", margin: 0
  });
  slide.addText("Game referenced:  Yi Ren Zhi Xia  /  March 2026", {
    x: 0.5, y: 5.05, w: 5.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
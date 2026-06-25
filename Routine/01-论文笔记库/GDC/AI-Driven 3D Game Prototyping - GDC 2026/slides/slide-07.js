// Slide 07: C - Code Reuse
// Layout: Mixed (left = definition + diagram, right = how it works)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Letter badge
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.4, w: 0.9, h: 0.9,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("C", {
    x: 0.5, y: 0.4, w: 0.9, h: 0.9,
    fontSize: 44, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Title
  slide.addText("PRINCIPLE 01", {
    x: 1.6, y: 0.4, w: 6, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Code Reuse", {
    x: 1.6, y: 0.7, w: 6, h: 0.55,
    fontSize: 30, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Tagline
  slide.addText("Share as much code as possible between the Web layer and the 3D engine layer.", {
    x: 0.5, y: 1.5, w: 9, h: 0.5,
    fontSize: 14, fontFace: "Georgia", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Left panel: How
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.2, w: 5.7, h: 2.7,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("How it works", {
    x: 0.7, y: 2.3, w: 5.3, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Diagram: Web <-> Engine with shared code in middle
  // Web box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.85, y: 2.85, w: 1.5, h: 1.0,
    fill: { color: "FFFFFF" }, line: { color: theme.accent, width: 1.5 },
    rectRadius: 0.06
  });
  slide.addText("Web", {
    x: 0.85, y: 2.95, w: 1.5, h: 0.35,
    fontSize: 13, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });
  slide.addText("TypeScript", {
    x: 0.85, y: 3.3, w: 1.5, h: 0.45,
    fontSize: 9, fontFace: "Arial", color: theme.secondary,
    align: "center", valign: "middle", margin: 0
  });

  // Engine box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 4.35, y: 2.85, w: 1.7, h: 1.0,
    fill: { color: "FFFFFF" }, line: { color: theme.accent, width: 1.5 },
    rectRadius: 0.06
  });
  slide.addText("Engine", {
    x: 4.35, y: 2.95, w: 1.7, h: 0.35,
    fontSize: 13, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });
  slide.addText("Unreal / Unity", {
    x: 4.35, y: 3.3, w: 1.7, h: 0.45,
    fontSize: 9, fontFace: "Arial", color: theme.secondary,
    align: "center", valign: "middle", margin: 0
  });

  // Connector lines with shared code label
  slide.addShape(pres.shapes.LINE, {
    x: 2.35, y: 3.35, w: 2.0, h: 0,
    line: { color: theme.accent, width: 2 }
  });
  slide.addText("shared code", {
    x: 2.3, y: 3.0, w: 2.1, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", italic: true, margin: 0
  });

  // Description below diagram
  slide.addText("The same TypeScript source runs in both places - the Web browser and the in-engine browser widget. Logic ships once, runs everywhere.", {
    x: 0.7, y: 4.05, w: 5.3, h: 0.7,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "top", margin: 0
  });

  // Right panel: Why it matters
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 2.2, w: 3.1, h: 2.7,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("Why it matters", {
    x: 6.6, y: 2.3, w: 2.7, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText([
    { text: "Single source of truth for game logic", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Pixel-perfect UI parity with Web prototype", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "AI learns one codebase, not two", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Smaller context window = lower cost", options: { bullet: { code: "25A0" } } }
  ], {
    x: 6.6, y: 2.75, w: 2.7, h: 2.1,
    fontSize: 11, fontFace: "Arial", color: "FFFFFF",
    paraSpaceAfter: 8, margin: 0
  });

  // Page number badge
  slide.addText("07", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
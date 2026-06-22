// Slide 08: A - Adapter Design
// Layout: Mixed (definition + diagram showing core vs adapter split)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Letter badge
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.4, w: 0.9, h: 0.9,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("A", {
    x: 0.5, y: 0.4, w: 0.9, h: 0.9,
    fontSize: 44, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Title
  slide.addText("PRINCIPLE 02", {
    x: 1.6, y: 0.4, w: 6, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Adapter Design", {
    x: 1.6, y: 0.7, w: 6, h: 0.55,
    fontSize: 30, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Tagline
  slide.addText("Extract a shared interface. Let each platform keep its own native implementation.", {
    x: 0.5, y: 1.5, w: 9, h: 0.5,
    fontSize: 14, fontFace: "Georgia", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Diagram: Three-layer onion (Core in center, then Web adapter, then Engine adapter)
  // Outer ring label
  slide.addText("PLATFORM ADAPTERS", {
    x: 0.5, y: 2.2, w: 5.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "center", valign: "middle", charSpacing: 3, bold: true, margin: 0
  });

  // Web adapter (top)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 2.55, w: 3.5, h: 0.55,
    fill: { color: theme.light }, line: { color: theme.accent, width: 1 },
    rectRadius: 0.06
  });
  slide.addText("Web adapter  /  DOM + Canvas", {
    x: 1.5, y: 2.55, w: 3.5, h: 0.55,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Core (middle)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 3.25, w: 3.5, h: 0.75,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
    rectRadius: 0.06
  });
  slide.addText("Core rules", {
    x: 1.5, y: 3.3, w: 3.5, h: 0.35,
    fontSize: 14, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });
  slide.addText("game logic, state, data updates", {
    x: 1.5, y: 3.6, w: 3.5, h: 0.4,
    fontSize: 10, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", margin: 0
  });

  // Engine adapter (bottom)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 4.15, w: 3.5, h: 0.55,
    fill: { color: theme.light }, line: { color: theme.accent, width: 1 },
    rectRadius: 0.06
  });
  slide.addText("Engine adapter  /  Unreal ECS + Puerts", {
    x: 1.5, y: 4.15, w: 3.5, h: 0.55,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Right panel: what AI sees vs what platform handles
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 2.2, w: 3.1, h: 2.7,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("Split of labor", {
    x: 6.6, y: 2.3, w: 2.7, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // AI's job
  slide.addText("AI writes", {
    x: 6.6, y: 2.75, w: 2.7, h: 0.3,
    fontSize: 11, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("Core rules, data updates, behaviour trees.", {
    x: 6.6, y: 3.05, w: 2.7, h: 0.6,
    fontSize: 11, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "top", margin: 0
  });

  // Platform's job
  slide.addText("Platform handles", {
    x: 6.6, y: 3.7, w: 2.7, h: 0.3,
    fontSize: 11, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("Rendering, physics, engine-specific I/O. AI never touches this.", {
    x: 6.6, y: 4.0, w: 2.7, h: 0.8,
    fontSize: 11, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "top", margin: 0
  });

  // Page number badge
  slide.addText("08", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
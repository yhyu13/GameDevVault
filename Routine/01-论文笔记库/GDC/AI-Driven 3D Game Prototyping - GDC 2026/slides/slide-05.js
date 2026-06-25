// Slide 05: The 3D Prototyping Bottleneck - Comparison content slide
// Layout: Two-column comparison (Web AI vs 3D Engine AI)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText("THE PROBLEM", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("AI is great at 2D. It struggles at 3D.", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Subtitle / context
  slide.addText("Existing AI tools can ship small Web games end-to-end. They cannot cross the boundary into a 3D game engine - which is where the real money is.", {
    x: 0.5, y: 1.5, w: 9, h: 0.5,
    fontSize: 12, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "top", italic: true, margin: 0
  });

  // Two comparison columns
  const colW = 4.2, colH = 3.0;
  const col1X = 0.5, col2X = 5.3, colY = 2.15;

  // Left column: Web 2D (works)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: col1X, y: colY, w: colW, h: colH,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.1
  });
  // Status pill
  slide.addShape(pres.shapes.RECTANGLE, {
    x: col1X + 0.25, y: colY + 0.25, w: 1.0, h: 0.32,
    fill: { color: "00B4D8" }, line: { color: "00B4D8", width: 0 },
    rectRadius: 0.15
  });
  slide.addText("WORKS", {
    x: col1X + 0.25, y: colY + 0.25, w: 1.0, h: 0.32,
    fontSize: 10, fontFace: "Arial", color: "FFFFFF",
    align: "center", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });
  // Title
  slide.addText("Web 2D games", {
    x: col1X + 0.25, y: colY + 0.7, w: colW - 0.5, h: 0.5,
    fontSize: 20, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  // Bullets
  slide.addText([
    { text: "Standardized DOM, CSS, and JS specs", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "AI reads text and writes text natively", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Iterations are cheap and immediate", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Examples: vibe-coded prototypes, p5.js demos", options: { bullet: { code: "25A0" } } }
  ], {
    x: col1X + 0.25, y: colY + 1.25, w: colW - 0.5, h: 1.6,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    paraSpaceAfter: 6, margin: 0
  });

  // Right column: 3D engines (breaks)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: col2X, y: colY, w: colW, h: colH,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.1
  });
  // Status pill
  slide.addShape(pres.shapes.RECTANGLE, {
    x: col2X + 0.25, y: colY + 0.25, w: 1.2, h: 0.32,
    fill: { color: "EF233C" }, line: { color: "EF233C", width: 0 },
    rectRadius: 0.15
  });
  slide.addText("BREAKS", {
    x: col2X + 0.25, y: colY + 0.25, w: 1.2, h: 0.32,
    fontSize: 10, fontFace: "Arial", color: "FFFFFF",
    align: "center", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });
  // Title
  slide.addText("3D game engines", {
    x: col2X + 0.25, y: colY + 0.7, w: colW - 0.5, h: 0.5,
    fontSize: 20, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  // Bullets
  slide.addText([
    { text: "No standardized rendering layer across engines", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Decades of GUI tooling aimed at human artists", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Physics, collisions, lighting - too many non-textual surfaces", options: { bullet: { code: "25A0" }, breakLine: true } },
    { text: "Every studio's codebase is a custom snowflake", options: { bullet: { code: "25A0" } } }
  ], {
    x: col2X + 0.25, y: colY + 1.25, w: colW - 0.5, h: 1.6,
    fontSize: 11, fontFace: "Arial", color: theme.primary,
    paraSpaceAfter: 6, margin: 0
  });

  // Page number badge
  slide.addText("05", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
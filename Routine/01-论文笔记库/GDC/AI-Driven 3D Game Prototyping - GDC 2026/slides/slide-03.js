// Slide 03: Section Divider 01 - "Why now"
// Layout: Left-Aligned with Accent Block

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  // Large left accent block
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 3.5, h: 5.625,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  // Big "01" on the accent block
  slide.addText("01", {
    x: 0.5, y: 1.5, w: 2.5, h: 2.5,
    fontSize: 180, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Section label on left block
  slide.addText("SECTION", {
    x: 0.5, y: 4.2, w: 2.5, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", charSpacing: 6, bold: true, margin: 0
  });

  // Section title on right
  slide.addText("Why now", {
    x: 4.0, y: 1.8, w: 5.5, h: 1.0,
    fontSize: 48, fontFace: "Arial Black", color: "FFFFFF",
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Intro line
  slide.addText("AI has moved from concept to production tool, but 3D game prototyping remains stubbornly hard for language models to touch.", {
    x: 4.0, y: 2.9, w: 5.5, h: 1.2,
    fontSize: 15, fontFace: "Georgia", color: theme.light,
    align: "left", valign: "top", italic: true, margin: 0
  });

  // Accent line under title
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 4.0, y: 2.8, w: 0.6, h: 0.05,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  // Page number badge
  slide.addText("03", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.light,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
// Slide 10: Section Divider 04 - "Production gains"

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.5, y: 0, w: 3.5, h: 5.625,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  slide.addText("04", {
    x: 6.5, y: 1.5, w: 3.5, h: 2.5,
    fontSize: 180, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  slide.addText("SECTION", {
    x: 6.5, y: 4.2, w: 3.5, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", charSpacing: 6, bold: true, margin: 0
  });

  slide.addText("Production gains", {
    x: 0.5, y: 1.8, w: 5.7, h: 1.0,
    fontSize: 44, fontFace: "Arial Black", color: "FFFFFF",
    align: "left", valign: "middle", bold: true, fit: "shrink", margin: 0
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.8, w: 0.6, h: 0.05,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  slide.addText("From 90 minutes per transition to 20. From 1:1 asset coverage to 0.48:1. Shipping numbers, not vibes.", {
    x: 0.5, y: 2.95, w: 5.7, h: 1.4,
    fontSize: 14, fontFace: "Georgia", color: theme.light,
    align: "left", valign: "top", italic: true, margin: 0
  });

  slide.addText("10", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.light,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
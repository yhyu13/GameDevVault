// Slide 07: Section Divider 03 - "The model"

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 3.5, h: 5.625,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  slide.addText("03", {
    x: 0, y: 1.5, w: 3.5, h: 2.5,
    fontSize: 180, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  slide.addText("SECTION", {
    x: 0, y: 4.2, w: 3.5, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", charSpacing: 6, bold: true, margin: 0
  });

  slide.addText("The model", {
    x: 4.0, y: 1.8, w: 5.5, h: 1.0,
    fontSize: 48, fontFace: "Arial Black", color: "FFFFFF",
    align: "left", valign: "middle", bold: true, margin: 0
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 4.0, y: 2.8, w: 0.6, h: 0.05,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  slide.addText("Four input encoders. Three decoders. One Mixture-of-Experts. Designed to fit a 0.4 ms inference budget.", {
    x: 4.0, y: 2.95, w: 5.5, h: 1.4,
    fontSize: 14, fontFace: "Georgia", color: theme.light,
    align: "left", valign: "top", italic: true, margin: 0
  });

  slide.addText("07", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.light,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
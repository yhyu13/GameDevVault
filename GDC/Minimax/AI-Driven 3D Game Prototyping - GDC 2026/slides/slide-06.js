// Slide 06: Section Divider 02 - "The C.A.T Framework"
// Layout: Bold Center (mirror of slide 03 with different number)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  // Large right accent block (mirrored from slide 03)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.5, y: 0, w: 3.5, h: 5.625,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  // Big "02" on the accent block
  slide.addText("02", {
    x: 6.5, y: 1.5, w: 3.5, h: 2.5,
    fontSize: 180, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Section label on right block
  slide.addText("SECTION", {
    x: 6.5, y: 4.2, w: 3.5, h: 0.4,
    fontSize: 14, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", charSpacing: 6, bold: true, margin: 0
  });

  // Section title on left
  slide.addText("The C.A.T framework", {
    x: 0.5, y: 1.8, w: 5.7, h: 1.0,
    fontSize: 44, fontFace: "Arial Black", color: "FFFFFF",
    align: "left", valign: "middle", bold: true, fit: "shrink", margin: 0
  });

  // Accent line under title
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.8, w: 0.6, h: 0.05,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
  });

  // Intro line
  slide.addText("Three guiding principles that turn a language model into a productive 3D engine collaborator - named for code reuse, adapter design, and being token-friendly.", {
    x: 0.5, y: 2.95, w: 5.7, h: 1.4,
    fontSize: 14, fontFace: "Georgia", color: theme.light,
    align: "left", valign: "top", italic: true, margin: 0
  });

  // Page number badge
  slide.addText("06", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.light,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
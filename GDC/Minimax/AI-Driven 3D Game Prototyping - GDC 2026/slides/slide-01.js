// Slide 01: Cover Page
// Topic: AI-Driven 3D Game Prototyping at GDC 2026
// Layout: Asymmetric Left-Right (text left, motif right)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Right-side accent panel (full-bleed vertical band)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.2, y: 0, w: 3.8, h: 5.625,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 }
  });

  // Geometric "C.A.T" motif on the right band
  // Three stacked hex-ish blocks representing C, A, T
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.7, y: 1.0, w: 0.9, h: 0.9,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
    rectRadius: 0.1
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 7.75, y: 1.0, w: 0.9, h: 0.9,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.1
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.8, y: 1.0, w: 0.9, h: 0.9,
    fill: { color: theme.secondary }, line: { color: theme.secondary, width: 0 },
    rectRadius: 0.1
  });

  // Big "C.A.T" letters over the motif blocks
  slide.addText("C", {
    x: 6.7, y: 1.0, w: 0.9, h: 0.9,
    fontSize: 36, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });
  slide.addText("A", {
    x: 7.75, y: 1.0, w: 0.9, h: 0.9,
    fontSize: 36, fontFace: "Arial Black", color: theme.primary,
    align: "center", valign: "middle", bold: true, margin: 0
  });
  slide.addText("T", {
    x: 8.8, y: 1.0, w: 0.9, h: 0.9,
    fontSize: 36, fontFace: "Arial Black", color: "FFFFFF",
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // Tag label
  slide.addText("GDC 2026  /  AI SUMMIT", {
    x: 6.7, y: 0.4, w: 3.0, h: 0.4,
    fontSize: 12, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", charSpacing: 4, margin: 0
  });

  // Three principles listed on right panel
  slide.addText("Code Reuse", {
    x: 6.7, y: 2.2, w: 3.0, h: 0.35,
    fontSize: 14, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "middle", margin: 0
  });
  slide.addText("Adapter Design", {
    x: 6.7, y: 2.6, w: 3.0, h: 0.35,
    fontSize: 14, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "middle", margin: 0
  });
  slide.addText("Token-Friendly", {
    x: 6.7, y: 3.0, w: 3.0, h: 0.35,
    fontSize: 14, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Quote at bottom of right panel
  slide.addText('"Tokens, not pixels."', {
    x: 6.7, y: 4.3, w: 3.0, h: 0.5,
    fontSize: 18, fontFace: "Georgia", color: theme.light,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Left side: eyebrow + main title
  slide.addText("TENCENT PHOTON STUDIO  /  GDC 2026", {
    x: 0.5, y: 0.5, w: 5.5, h: 0.4,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 3, bold: true, margin: 0
  });

  // Main title (split into two lines for impact)
  slide.addText("AI-Driven 3D Game", {
    x: 0.5, y: 1.4, w: 5.5, h: 0.9,
    fontSize: 44, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("Prototyping", {
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
  slide.addText("How the C.A.T Principle Lets Language Models Ship Playable 3D Prototypes", {
    x: 0.5, y: 3.4, w: 5.5, h: 0.6,
    fontSize: 16, fontFace: "Georgia", color: theme.secondary,
    align: "left", valign: "top", italic: true, margin: 0
  });

  // Presenter + meta block
  slide.addText("Speaker:  Hao Yang", {
    x: 0.5, y: 4.4, w: 5.5, h: 0.3,
    fontSize: 13, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("Senior Engineer  /  Tencent Photon Studio Group", {
    x: 0.5, y: 4.7, w: 5.5, h: 0.3,
    fontSize: 11, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", margin: 0
  });
  slide.addText("March 2026  /  Moscone Center, San Francisco", {
    x: 0.5, y: 5.05, w: 5.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
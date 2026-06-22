// Slide 13: Closing - Takeaways and Implications
// Layout: Split Recap (key takeaways + why it matters)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText("TAKEAWAYS", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("What this talk actually means", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Left column: Key takeaways
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

  // Checkmark-style takeaways using circles
  const takeaways = [
    "Build a shared codebase between Web and engine - one source, two runtimes.",
    "Extract a clean core that the AI is allowed to touch; keep platform I/O behind an adapter.",
    "Tokenize the 3D world before the AI touches it - bounding boxes, markers, domain rules.",
    "Use TypeScript (Puerts) over C++ for engine scripting - AI is fluent in text.",
    "Ship small, iterate fast - 70% of an RPG prototype from a single prompt is the new baseline."
  ];

  takeaways.forEach((t, i) => {
    // Bullet circle
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

  // Right column: Industry implications
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.2, y: 1.65, w: 3.3, h: 3.4,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.1
  });
  slide.addText("For the industry", {
    x: 6.45, y: 1.78, w: 2.9, h: 0.4,
    fontSize: 16, fontFace: "Arial Black", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Three implications stacked
  const implications = [
    { num: "01", text: "Internal: prototyping cost collapses - small teams validate mechanics in hours, not weeks." },
    { num: "02", text: "External: amateur creators can build playable 3D prototypes from a sentence." },
    { num: "03", text: "Strategic: tooling must shift from GUI-first to token-first. Old GUIs become optional." }
  ];

  implications.forEach((imp, i) => {
    slide.addText(imp.num, {
      x: 6.45, y: 2.3 + i * 0.95, w: 0.6, h: 0.4,
      fontSize: 16, fontFace: "Arial Black", color: theme.accent,
      align: "left", valign: "middle", bold: true, margin: 0
    });
    slide.addText(imp.text, {
      x: 7.05, y: 2.3 + i * 0.95, w: 2.4, h: 0.85,
      fontSize: 10, fontFace: "Arial", color: "FFFFFF",
      align: "left", valign: "top", margin: 0
    });
  });

  // Footer quote
  slide.addText('"Game tools were built for humans. Stop expecting AI to see pixels."', {
    x: 0.5, y: 5.15, w: 8.5, h: 0.35,
    fontSize: 11, fontFace: "Georgia", color: theme.secondary,
    align: "center", valign: "middle", italic: true, margin: 0
  });

  // Page number badge
  slide.addText("13", {
    x: 9.3, y: 5.15, w: 0.5, h: 0.35,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
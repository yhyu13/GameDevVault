// Slide 11: Architecture / Stack
// Layout: Timeline / Process showing the full pipeline

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText("THE STACK", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Prompt in, prototype out", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Process flow: 5 steps
  const steps = [
    { tag: "INPUT", title: "Natural language", desc: "Designer describes a game in plain text" },
    { tag: "PUERTS", title: "TypeScript bridge", desc: "Open-source Tencent plugin calls engine APIs without C++ or blueprints" },
    { tag: "ECS", title: "Data-driven engine", desc: "Component-entity-system core, decoupled from rendering" },
    { tag: "WEB", title: "In-engine browser", desc: "Unreal's Web Browser widget renders the same Web UI pixel-for-pixel" },
    { tag: "OUTPUT", title: "Playable prototype", desc: "Designer plays and iterates without leaving the engine" }
  ];

  const boxW = 1.7, boxH = 2.4;
  const gap = 0.15;
  const startX = 0.4, startY = 1.85;

  steps.forEach((s, i) => {
    const x = startX + i * (boxW + gap);

    // Box
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: startY, w: boxW, h: boxH,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.08
    });

    // Top tag pill
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.15, y: startY + 0.2, w: boxW - 0.3, h: 0.3,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
      rectRadius: 0.15
    });
    slide.addText(s.tag, {
      x: x + 0.15, y: startY + 0.2, w: boxW - 0.3, h: 0.3,
      fontSize: 9, fontFace: "Arial", color: theme.primary,
      align: "center", valign: "middle", bold: true, charSpacing: 2, margin: 0
    });

    // Title
    slide.addText(s.title, {
      x: x + 0.15, y: startY + 0.6, w: boxW - 0.3, h: 0.5,
      fontSize: 13, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Description
    slide.addText(s.desc, {
      x: x + 0.15, y: startY + 1.15, w: boxW - 0.3, h: boxH - 1.25,
      fontSize: 9, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "top", margin: 0
    });

    // Arrow between boxes (except after the last one)
    if (i < steps.length - 1) {
      slide.addText(">", {
        x: x + boxW, y: startY + boxH / 2 - 0.15, w: gap, h: 0.3,
        fontSize: 14, fontFace: "Arial Black", color: theme.accent,
        align: "center", valign: "middle", bold: true, margin: 0
      });
    }
  });

  // Bottom callout: Why Puerts matters
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.55, w: 9.0, h: 0.55,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.06
  });
  slide.addText("Key insight:  Puerts replaces C++ with TypeScript. AI thinks in text, so the engine should expose text too.", {
    x: 0.7, y: 4.55, w: 8.6, h: 0.55,
    fontSize: 11, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Page number badge
  slide.addText("11", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
// Slide 11: Production efficiency - data table style
// Layout: Comparison table

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("EFFICIENCY", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("The numbers that ship", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Header row
  const headerY = 1.7;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: headerY, w: 9.0, h: 0.5,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.06
  });
  slide.addText("METRIC", {
    x: 0.7, y: headerY, w: 3.0, h: 0.5,
    fontSize: 10, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });
  slide.addText("TRADITIONAL", {
    x: 3.8, y: headerY, w: 2.5, h: 0.5,
    fontSize: 10, fontFace: "Arial", color: theme.light,
    align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });
  slide.addText("AI PIPELINE", {
    x: 6.5, y: headerY, w: 2.5, h: 0.5,
    fontSize: 10, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });

  // Data rows
  const rows = [
    { metric: "Time per transition", trad: "30 min mocap + 60 min cleanup = 90 min", ai: "5 min mocap + 15 min cleanup = 20 min" },
    { metric: "Asset-to-action ratio", trad: "930 clips / 930 actions = 1.00 : 1", ai: "445 clips / 930 actions = 0.48 : 1" },
    { metric: "Action coverage", trad: "Finite, gaps between states", ai: "Generated on demand from reference set" },
    { metric: "New character cost", trad: "Re-capture + re-key everything", ai: "Shoot small reference set, model adapts" }
  ];

  rows.forEach((r, i) => {
    const y = headerY + 0.6 + i * 0.7;
    const bg = i % 2 === 0 ? theme.light : theme.bg;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: y, w: 9.0, h: 0.6,
      fill: { color: bg }, line: { color: bg, width: 0 }
    });
    slide.addText(r.metric, {
      x: 0.7, y: y, w: 3.0, h: 0.6,
      fontSize: 11, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });
    slide.addText(r.trad, {
      x: 3.8, y: y, w: 2.5, h: 0.6,
      fontSize: 10, fontFace: "Arial", color: theme.secondary,
      align: "left", valign: "middle", margin: 0
    });
    slide.addText(r.ai, {
      x: 6.5, y: y, w: 2.5, h: 0.6,
      fontSize: 10, fontFace: "Arial", color: theme.accent,
      align: "left", valign: "middle", bold: true, margin: 0
    });
  });

  // Bottom callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.85, w: 9.0, h: 0.45,
    fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
    rectRadius: 0.06
  });
  slide.addText("Net: 78% time saved per transition. 52% fewer assets. Artists focus on hero poses, not auxiliary fill.", {
    x: 0.7, y: 4.85, w: 8.6, h: 0.45,
    fontSize: 11, fontFace: "Arial", color: "FFFFFF",
    align: "left", valign: "middle", italic: true, margin: 0
  });

  slide.addText("11", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
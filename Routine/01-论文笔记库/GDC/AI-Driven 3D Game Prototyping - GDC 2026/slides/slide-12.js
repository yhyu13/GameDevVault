// Slide 12: Three Prototype Cases
// Layout: Comparison - 3 case study cards

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText("RESULTS", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Three prototypes, all built by AI", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Three case cards
  const cases = [
    {
      tag: "01",
      title: "8-Ball Pool",
      sub: "Physics simulation",
      desc: "Simple rules, predictable physics, deterministic outcomes. Ideal sandbox for stress-testing the AI tooling.",
      stat: "100%",
      statLabel: "of features functional"
    },
    {
      tag: "02",
      title: "Top-down RPG",
      sub: "Single-prompt build",
      desc: "Most features generated from a single prompt. AI processed for ~40 minutes and delivered roughly 70% of the final game.",
      stat: "70%",
      statLabel: "of final game from one prompt"
    },
    {
      tag: "03",
      title: "Action Combat",
      sub: "Multi-mechanic demo",
      desc: "Multiple characters, varied abilities, distinct boss attack patterns. The most ambitious of the three test cases.",
      stat: "Most",
      statLabel: "boss mechanics implemented"
    }
  ];

  const cardW = 3.0, cardH = 3.4;
  const gapX = 0.15;
  const startX = 0.5, startY = 1.7;

  cases.forEach((c, i) => {
    const x = startX + i * (cardW + gapX);

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: startY, w: cardW, h: cardH,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.1
    });

    // Tag
    slide.addText(c.tag, {
      x: x + 0.25, y: startY + 0.2, w: 0.8, h: 0.4,
      fontSize: 14, fontFace: "Arial Black", color: theme.accent,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Title
    slide.addText(c.title, {
      x: x + 0.25, y: startY + 0.6, w: cardW - 0.5, h: 0.5,
      fontSize: 19, fontFace: "Arial Black", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Subtitle
    slide.addText(c.sub, {
      x: x + 0.25, y: startY + 1.05, w: cardW - 0.5, h: 0.3,
      fontSize: 10, fontFace: "Arial", color: theme.secondary,
      align: "left", valign: "middle", italic: true, margin: 0
    });

    // Divider line
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.25, y: startY + 1.45, w: 0.4, h: 0.03,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
    });

    // Description
    slide.addText(c.desc, {
      x: x + 0.25, y: startY + 1.55, w: cardW - 0.5, h: 1.0,
      fontSize: 10, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "top", margin: 0
    });

    // Stat
    slide.addText(c.stat, {
      x: x + 0.25, y: startY + 2.55, w: cardW - 0.5, h: 0.5,
      fontSize: 26, fontFace: "Arial Black", color: theme.secondary,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Stat label
    slide.addText(c.statLabel, {
      x: x + 0.25, y: startY + 3.05, w: cardW - 0.5, h: 0.3,
      fontSize: 9, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "middle", margin: 0
    });
  });

  // Bottom caption
  slide.addText("Source: Hao Yang, GDC 2026. Three prototypes were shown live in the talk.", {
    x: 0.5, y: 5.2, w: 8.7, h: 0.3,
    fontSize: 9, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Page number badge
  slide.addText("12", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
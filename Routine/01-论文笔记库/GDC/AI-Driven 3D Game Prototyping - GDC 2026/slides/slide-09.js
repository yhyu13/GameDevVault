// Slide 09: T - Token-Friendly (the most important principle)
// Layout: Text + visual motif (the heart of the talk)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Letter badge (highlighted because it's the headline principle)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.4, w: 0.9, h: 0.9,
    fill: { color: theme.secondary }, line: { color: theme.secondary, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("T", {
    x: 0.5, y: 0.4, w: 0.9, h: 0.9,
    fontSize: 44, fontFace: "Arial Black", color: "FFFFFF",
    align: "center", valign: "middle", bold: true, margin: 0
  });

  // "Most important" tag
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.0, y: 0.55, w: 1.5, h: 0.32,
    fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
    rectRadius: 0.15
  });
  slide.addText("MOST CRITICAL", {
    x: 8.0, y: 0.55, w: 1.5, h: 0.32,
    fontSize: 9, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", bold: true, charSpacing: 2, margin: 0
  });

  // Title
  slide.addText("PRINCIPLE 03", {
    x: 1.6, y: 0.4, w: 6, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Token-Friendly", {
    x: 1.6, y: 0.7, w: 6, h: 0.55,
    fontSize: 30, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Tagline
  slide.addText('"Game tools were built for humans. AI reads tokens. Stop expecting AI to see pixels."', {
    x: 0.5, y: 1.45, w: 9, h: 0.55,
    fontSize: 14, fontFace: "Georgia", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Three tokenization tactics as horizontal cards
  const tactics = [
    {
      tag: "01",
      title: "Inject domain rules",
      desc: "Feed the AI common game knowledge - standard pool table dimensions, ball trajectories, physics constants. Knowledge it cannot Google."
    },
    {
      tag: "02",
      title: "Expose asset metadata",
      desc: "Give the AI the bounding boxes, colliders, tags, and labels of every asset. Spatial data as text, not as 3D primitives."
    },
    {
      tag: "03",
      title: "Designer markers",
      desc: "Provide placement tools so designers can leave named markers. The AI reads the marker names and transforms like any other token."
    }
  ];

  const cardW = 3.0, cardH = 2.85;
  const gapX = 0.15;
  const startX = 0.5, startY = 2.15;

  tactics.forEach((t, i) => {
    const x = startX + i * (cardW + gapX);

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: startY, w: cardW, h: cardH,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.08
    });

    // Top color band
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: startY, w: cardW, h: 0.5,
      fill: { color: theme.secondary }, line: { color: theme.secondary, width: 0 }
    });

    // Tag number on band
    slide.addText(t.tag, {
      x: x + 0.2, y: startY, w: 0.6, h: 0.5,
      fontSize: 18, fontFace: "Arial Black", color: "FFFFFF",
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Tactic title
    slide.addText(t.title, {
      x: x + 0.2, y: startY + 0.65, w: cardW - 0.4, h: 0.5,
      fontSize: 15, fontFace: "Arial Black", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Description
    slide.addText(t.desc, {
      x: x + 0.2, y: startY + 1.2, w: cardW - 0.4, h: cardH - 1.3,
      fontSize: 10, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "top", margin: 0
    });
  });

  // Bottom note
  slide.addText("Net effect: AI manipulates a textual representation of the 3D world - the same way a programmer works through console commands.", {
    x: 0.5, y: 5.1, w: 8.7, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Page number badge
  slide.addText("09", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
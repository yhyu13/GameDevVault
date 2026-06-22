// Slide 12: Game integration details
// Layout: 3 cards - async inference, weapon clipping, multi-character

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("INTEGRATION", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Three integration tricks", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Three integration cards
  const cards = [
    {
      tag: "01  /  ASYNC INFERENCE",
      title: "Never block the renderer",
      desc: "Inference runs off the render thread. The animation system reads results from a buffer; the engine never waits on the model."
    },
    {
      tag: "02  /  WEAPON CLIPPING",
      title: "Split transitions in two",
      desc: "Reframe transition targets into intermediate poses. A Physics Motion Controller (PMC) handles weapon positioning to prevent swords and staffs from piercing the body."
    },
    {
      tag: "03  /  MULTI-CHARACTER",
      title: "Bone-ratio remap",
      desc: "Train one model on a unified skeleton. Map it to each character via bone-length ratio - same model covers tall, short, weapon-wielding variants."
    }
  ];

  const cardW = 3.0, cardH = 3.4;
  const gapX = 0.15;
  const startX = 0.5, startY = 1.65;

  cards.forEach((c, i) => {
    const x = startX + i * (cardW + gapX);

    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: startY, w: cardW, h: cardH,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.1
    });

    // Top color band
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: startY, w: cardW, h: 0.45,
      fill: { color: theme.secondary }, line: { color: theme.secondary, width: 0 }
    });

    slide.addText(c.tag, {
      x: x + 0.15, y: startY, w: cardW - 0.3, h: 0.45,
      fontSize: 10, fontFace: "Arial", color: "FFFFFF",
      align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
    });

    slide.addText(c.title, {
      x: x + 0.2, y: startY + 0.6, w: cardW - 0.4, h: 0.6,
      fontSize: 15, fontFace: "Arial Black", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    slide.addText(c.desc, {
      x: x + 0.2, y: startY + 1.25, w: cardW - 0.4, h: cardH - 1.35,
      fontSize: 11, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "top", margin: 0
    });
  });

  // Bottom note
  slide.addText("All three are post-processing - the model itself never sees weapons or character-specific bone lengths.", {
    x: 0.5, y: 5.15, w: 8.7, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  slide.addText("12", {
    x: 9.3, y: 5.15, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
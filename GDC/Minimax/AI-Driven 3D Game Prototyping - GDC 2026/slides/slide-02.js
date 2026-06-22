// Slide 02: Table of Contents
// 4 sections in a 2x2 card grid

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText("CONTENTS", {
    x: 0.5, y: 0.4, w: 9, h: 0.4,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("What we'll cover", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 32, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // 4 section cards arranged 2x2
  const sections = [
    { num: "01", title: "Why now", desc: "GDC 2026's AI moment and the prototyping bottleneck in 3D games." },
    { num: "02", title: "The C.A.T framework", desc: "Three principles that make AI productive inside a game engine." },
    { num: "03", title: "How it's built", desc: "Web UI, Unreal, ECS, and tokenizing 3D space." },
    { num: "04", title: "Cases & takeaways", desc: "Three prototypes, the results, and what it means for studios." }
  ];

  const cardW = 4.2, cardH = 1.7;
  const gapX = 0.3, gapY = 0.25;
  const startX = 0.5, startY = 1.7;

  sections.forEach((sec, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = startX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);

    // Card background
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: cardW, h: cardH,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.1
    });

    // Left accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 0.1, h: cardH,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
    });

    // Section number
    slide.addText(sec.num, {
      x: x + 0.3, y: y + 0.15, w: 1.2, h: 0.6,
      fontSize: 32, fontFace: "Arial Black", color: theme.accent,
      align: "left", valign: "top", bold: true, margin: 0
    });

    // Section title
    slide.addText(sec.title, {
      x: x + 1.4, y: y + 0.2, w: cardW - 1.5, h: 0.5,
      fontSize: 18, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });

    // Section description
    slide.addText(sec.desc, {
      x: x + 1.4, y: y + 0.75, w: cardW - 1.6, h: cardH - 0.85,
      fontSize: 11, fontFace: "Arial", color: theme.secondary,
      align: "left", valign: "top", margin: 0
    });
  });

  // Page number badge
  slide.addText("02", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
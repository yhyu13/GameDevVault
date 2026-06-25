// Slide 04: The Problem + Three Goals
// Layout: Mixed media - problem on left, three goals on right

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("THE PROBLEM", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Transitions are the bottleneck", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Left side: pain points
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.65, w: 5.5, h: 3.5,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.1
  });
  slide.addText("What breaks", {
    x: 0.7, y: 1.78, w: 5.0, h: 0.4,
    fontSize: 16, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  const pains = [
    { title: "Combinatorial explosion", desc: "States multiply: idle / attack / sprint / hit / get-up x dozens of characters x dozens of weapons. Hand-keying is infeasible." },
    { title: "Foot sliding", desc: "Linear interpolation between poses glides the feet across the floor; IK fixes the foot but stiffens the rest of the body." },
    { title: "Weapon clipping", desc: "Swords and staffs pierce the character's own body during fast transitions. Historically accepted as a known quirk." }
  ];

  pains.forEach((p, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.85, y: 2.35 + i * 0.9, w: 0.15, h: 0.15,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
    });
    slide.addText(p.title, {
      x: 1.1, y: 2.25 + i * 0.9, w: 4.7, h: 0.35,
      fontSize: 12, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "middle", bold: true, margin: 0
    });
    slide.addText(p.desc, {
      x: 1.1, y: 2.6 + i * 0.9, w: 4.7, h: 0.55,
      fontSize: 10, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "top", margin: 0
    });
  });

  // Right side: three goals
  slide.addText("Three goals", {
    x: 6.2, y: 1.65, w: 3.3, h: 0.4,
    fontSize: 16, fontFace: "Arial Black", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  const goals = [
    { tag: "ART", text: "Reduce manual work, keep visual quality." },
    { tag: "DESIGN", text: "Hit-action timing, no clipping, no forced slide." },
    { tag: "ENGINEERING", text: "Tight memory budget, low inference latency." }
  ];

  goals.forEach((g, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 6.2, y: 2.15 + i * 1.0, w: 3.3, h: 0.9,
      fill: { color: theme.primary }, line: { color: theme.primary, width: 0 },
      rectRadius: 0.06
    });
    slide.addText(g.tag, {
      x: 6.4, y: 2.25 + i * 1.0, w: 2.9, h: 0.3,
      fontSize: 10, fontFace: "Arial", color: theme.accent,
      align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
    });
    slide.addText(g.text, {
      x: 6.4, y: 2.5 + i * 1.0, w: 2.9, h: 0.45,
      fontSize: 11, fontFace: "Arial", color: "FFFFFF",
      align: "left", valign: "middle", margin: 0
    });
  });

  slide.addText("04", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
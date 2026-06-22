// Slide 06: Markerless mocap setup
// Layout: Mixed media - diagram left, key facts right

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("DATA  /  CAPTURE", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("Markerless mocap in a small room", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Left: diagram of 7 cameras around actor
  const cx = 2.7, cy = 3.7;
  const camR = 1.4;
  // 7 small camera squares in a circle
  for (let i = 0; i < 7; i++) {
    const angle = (i / 7) * Math.PI * 2 - Math.PI / 2;
    const camX = cx + Math.cos(angle) * camR - 0.18;
    const camY = cy + Math.sin(angle) * camR - 0.18;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: camX, y: camY, w: 0.36, h: 0.36,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 },
      rectRadius: 0.04
    });
    slide.addText(String(i + 1), {
      x: camX, y: camY, w: 0.36, h: 0.36,
      fontSize: 11, fontFace: "Arial Black", color: theme.primary,
      align: "center", valign: "middle", bold: true, margin: 0
    });
  }

  // Actor in center
  slide.addShape(pres.shapes.OVAL, {
    x: cx - 0.35, y: cy - 0.5, w: 0.7, h: 1.0,
    fill: { color: theme.secondary }, line: { color: theme.secondary, width: 0 }
  });
  slide.addText("actor", {
    x: cx - 0.7, y: cy + 0.6, w: 1.4, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.primary,
    align: "center", valign: "middle", margin: 0
  });

  // Caption
  slide.addText("7 consumer cameras, no markers, no stage.", {
    x: 0.5, y: 5.05, w: 4.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "center", valign: "middle", italic: true, margin: 0
  });

  // Right: 3 key facts as cards
  const facts = [
    { tag: "TRIANGULATION", text: "Cross-camera joint positions computed in real time. No marker suits required." },
    { tag: "INERTIAL SPINE", text: "IMU sensors correct spine rotation. Replaces facial marker rigs at a fraction of the cost." },
    { tag: "DATA AUGMENTATION", text: "Mirror flip along forward axis, frame-rate rescale, and mix-fuse initial frames to multiply one sample into many." }
  ];

  facts.forEach((f, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 5.4, y: 1.7 + i * 1.2, w: 4.1, h: 1.0,
      fill: { color: theme.light }, line: { color: theme.light, width: 0 },
      rectRadius: 0.06
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 5.4, y: 1.7 + i * 1.2, w: 0.08, h: 1.0,
      fill: { color: theme.accent }, line: { color: theme.accent, width: 0 }
    });
    slide.addText(f.tag, {
      x: 5.6, y: 1.78 + i * 1.2, w: 3.8, h: 0.3,
      fontSize: 10, fontFace: "Arial", color: theme.accent,
      align: "left", valign: "middle", bold: true, charSpacing: 2, margin: 0
    });
    slide.addText(f.text, {
      x: 5.6, y: 2.1 + i * 1.2, w: 3.8, h: 0.55,
      fontSize: 10, fontFace: "Arial", color: theme.primary,
      align: "left", valign: "top", margin: 0
    });
  });

  slide.addText("06", {
    x: 9.3, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
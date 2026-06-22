// Slide 04: GDC 2026 AI Landscape - Data Visualization
// Layout: Mixed (chart left, key takeaways right)

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText("GDC 2026  /  THE AI MOMENT", {
    x: 0.5, y: 0.4, w: 9, h: 0.35,
    fontSize: 11, fontFace: "Arial", color: theme.accent,
    align: "left", valign: "middle", charSpacing: 4, bold: true, margin: 0
  });
  slide.addText("AI has eaten the conference floor", {
    x: 0.5, y: 0.75, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: theme.primary,
    align: "left", valign: "middle", bold: true, margin: 0
  });

  // Bar chart showing AI session growth
  slide.addChart(pres.charts.BAR, [
    {
      name: "AI-related sessions",
      labels: ["2023", "2024", "2025", "2026"],
      values: [18, 20, 50, 105]
    }
  ], {
    x: 0.5, y: 1.7, w: 5.0, h: 3.3,
    barDir: "col",
    chartColors: [theme.accent],
    chartArea: { fill: { color: theme.bg }, roundedCorners: false },
    catAxisLabelColor: theme.secondary,
    catAxisLabelFontSize: 11,
    valAxisLabelColor: theme.secondary,
    valAxisLabelFontSize: 10,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelPosition: "outEnd",
    dataLabelColor: theme.primary,
    dataLabelFontSize: 11,
    dataLabelFontBold: true,
    showLegend: false,
    showTitle: true,
    title: "GDC AI-related sessions (estimated)",
    titleFontSize: 12,
    titleColor: theme.primary,
    titleFontFace: "Arial"
  });

  // Source
  slide.addText("Source: GDC program data, multiple press summaries", {
    x: 0.5, y: 5.05, w: 5.0, h: 0.3,
    fontSize: 9, fontFace: "Arial", color: theme.secondary,
    align: "left", valign: "middle", italic: true, margin: 0
  });

  // Right column: key facts as stat callouts
  // Stat 1
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.8, y: 1.7, w: 3.7, h: 1.0,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("105+", {
    x: 5.95, y: 1.78, w: 1.3, h: 0.85,
    fontSize: 36, fontFace: "Arial Black", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("AI sessions at GDC 2026 - more than 2x last year", {
    x: 7.25, y: 1.78, w: 2.2, h: 0.85,
    fontSize: 10, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", margin: 0
  });

  // Stat 2
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.8, y: 2.85, w: 3.7, h: 1.0,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("20%", {
    x: 5.95, y: 2.93, w: 1.3, h: 0.85,
    fontSize: 36, fontFace: "Arial Black", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("of all AI sessions came from Tencent alone", {
    x: 7.25, y: 2.93, w: 2.2, h: 0.85,
    fontSize: 10, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", margin: 0
  });

  // Stat 3
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.8, y: 4.0, w: 3.7, h: 1.0,
    fill: { color: theme.light }, line: { color: theme.light, width: 0 },
    rectRadius: 0.08
  });
  slide.addText("1 hr", {
    x: 5.95, y: 4.08, w: 1.3, h: 0.85,
    fontSize: 36, fontFace: "Arial Black", color: theme.accent,
    align: "left", valign: "middle", bold: true, margin: 0
  });
  slide.addText("queue started forming BEFORE this talk began", {
    x: 7.25, y: 4.08, w: 2.2, h: 0.85,
    fontSize: 10, fontFace: "Arial", color: theme.primary,
    align: "left", valign: "middle", margin: 0
  });

  // Page number badge
  slide.addText("04", {
    x: 9.3, y: 5.1, w: 0.5, h: 0.3,
    fontSize: 10, fontFace: "Arial", color: theme.secondary,
    align: "right", valign: "middle", margin: 0
  });
}

module.exports = { createSlide };
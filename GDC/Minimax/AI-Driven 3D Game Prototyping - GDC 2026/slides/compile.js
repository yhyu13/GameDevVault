// compile.js - Compile all slide modules into final PPTX
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "GameDevVault";
pres.title = "AI-Driven 3D Game Prototyping - GDC 2026";

// Pure Tech Blue palette
const theme = {
  primary:   "03045E",  // deep navy
  secondary: "0077B6",  // mid blue
  accent:    "00B4D8",  // cyan accent
  light:     "CAF0F8",  // very light cyan
  bg:        "FFFFFF"   // white background
};

// Load all slides in order
for (let i = 1; i <= 13; i++) {
  const num = String(i).padStart(2, "0");
  require(`./slide-${num}.js`).createSlide(pres, theme);
}

pres.writeFile({
  fileName: "./output/AI-Driven-3D-Game-Prototyping-GDC2026.pptx"
}).then(fileName => {
  console.log("Deck written to: " + fileName);
});
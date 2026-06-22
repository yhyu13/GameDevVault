// compile.js - Compile all slide modules into final PPTX
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "GameDevVault";
pres.title = "Tencent Magic Studio - Real-time AI Motion Generation - GDC 2026";

// Pure Tech Blue palette (consistent with the Photon C.A.T deck for vault coherence)
const theme = {
  primary:   "03045E",
  secondary: "0077B6",
  accent:    "00B4D8",
  light:     "CAF0F8",
  bg:        "FFFFFF"
};

// Load all slides in order
for (let i = 1; i <= 13; i++) {
  const num = String(i).padStart(2, "0");
  require(`./slide-${num}.js`).createSlide(pres, theme);
}

pres.writeFile({
  fileName: "./output/Tencent-Magic-Studio-Real-time-AI-Motion-Generation-GDC2026.pptx"
}).then(fileName => {
  console.log("Deck written to: " + fileName);
});
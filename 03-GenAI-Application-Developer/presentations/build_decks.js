// Builds presentation.pptx in each course folder.
// Run: cd presentations && npm install && node build_decks.js [deck id, such as 03-02]
const path = require("path");
const { writeDeck, warnings } = require("./lib.js");

const DECKS = [...require("./decks_a.js"), ...require("./decks_b.js"), ...require("./decks_c.js")];
const ROOT = path.resolve(__dirname, "..");

(async () => {
  const only = process.argv[2];
  for (const deck of DECKS) {
    if (only && deck.id !== only) continue;
    const output = path.join(ROOT, deck.dir, "presentation.pptx");
    await writeDeck(deck, output);
    console.log(`${deck.id}: ${deck.slides.length + 1} slides -> ${path.relative(ROOT, output)}`);
  }
  if (warnings.length) {
    console.log(`\n${warnings.length} fit warnings:`);
    warnings.forEach((warning) => console.log(`  ${warning}`));
  } else {
    console.log("\nNo fit warnings.");
  }
})();

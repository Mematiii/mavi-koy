// Copies the game's fonts into www/fonts so the app works offline and never calls Google Fonts.
import { cpSync, mkdirSync } from "node:fs";
for (const [pkg, weights] of [["fredoka", [600, 700]], ["lilita-one", [400]], ["nunito", [600, 700, 800, 900]]]) {
  const src = `node_modules/@fontsource/${pkg}`, dst = `www/fonts/${pkg}`;
  mkdirSync(dst, { recursive: true });
  cpSync(`${src}/files`, `${dst}/files`, { recursive: true });
  for (const w of weights) cpSync(`${src}/${w}.css`, `${dst}/${w}.css`);
}
console.log("fonts copied");

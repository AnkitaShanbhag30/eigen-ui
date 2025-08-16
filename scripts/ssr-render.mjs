#!/usr/bin/env node
import { build } from "esbuild";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import url from "node:url";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// CLI args
const args = new Map(process.argv.slice(2).map((a, i, arr) => a.startsWith("--") ? [a.replace(/^--/, ""), arr[i+1]] : null).filter(Boolean));
const brand = args.get("brand") || "gigit";
const entry = args.get("entry") || "data/templates/_active/index.tsx";
const out   = args.get("out")   || `data/drafts/${brand}/${brand}-dyad.html`;
const propsPath = args.get("props") || `data/brands/${brand}.json`;

// User requirements for dynamic content
const userRequirements = {
  x: args.get("x") || null,
  y: args.get("y") || null,
  z: args.get("z") || null,
  cta: args.get("cta") || null
};

// ensure out dir
mkdirSync(path.dirname(out), { recursive: true });

// ephemeral bundle
const outfile = ".tmp/dyad-ssr.cjs";
await build({
  entryPoints: [entry],
  bundle: true,
  platform: "node",
  format: "cjs",
  outfile,
  jsx: "transform",
  jsxFactory: "React.createElement",
  external: [], // adjust if Dyad export references external libs
  target: "node18",
  minify: false,
  sourcemap: false,
});

// import bundled component
const mod = await import(url.pathToFileURL(path.resolve(outfile)));

// Try to get the actual function from the wrapped module
let Page = null;
if (mod.default && typeof mod.default === 'object' && mod.default.default) {
  Page = mod.default.default;
} else {
  Page = mod.default || mod.Page || null;
}

if (!Page) {
  console.error("No default export found in", entry);
  process.exit(1);
}

// Ensure Page is a function
if (typeof Page !== 'function') {
  console.error("Page export is not a function:", typeof Page);
  console.error("Available exports:", Object.keys(mod));
  process.exit(1);
}

// load props (brand/intermediate json)
const props = JSON.parse(readFileSync(propsPath, "utf-8"));

// SSR
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
const html = "<!doctype html>" + renderToStaticMarkup(React.createElement(Page, { 
  data: props, 
  userRequirements: userRequirements 
}));

writeFileSync(out, html, "utf-8");
console.log("[ssr] wrote", out);

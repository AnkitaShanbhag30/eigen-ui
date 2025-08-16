#!/usr/bin/env node

import { build } from "esbuild";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import url from "node:url";

// Load environment variables from .env file
try {
  const dotenv = await import("dotenv");
  dotenv.config();
  console.log("🔧 Loaded environment variables from .env file");
} catch (error) {
  console.log("⚠️ Could not load .env file, using system environment variables");
}

const __filename = url.fileURLToPath(import.meta.url);
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

// Generate images using GPT if API key is available
let enhancedProps = { ...props };
if (process.env.OPENAI_API_KEY) {
  try {
    console.log("🔑 OpenAI API key found, generating images with GPT...");
    
    // Import and use GPT image generator
    const GPTImageGenerator = (await import("./gpt-image-generator.mjs")).default;
    const imageGenerator = new GPTImageGenerator(props, userRequirements);
    const generatedImages = await imageGenerator.generateImages();
    
    // Update props with generated images
    enhancedProps = {
      ...props,
      generatedImages: generatedImages
    };
    
    console.log("✅ GPT image generation completed");
  } catch (error) {
    console.error("⚠️ GPT image generation failed, using fallbacks:", error.message);
  }
} else {
  console.log("🔑 No OpenAI API key found, using fallback images");
}

// SSR
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
const html = "<!doctype html>" + renderToStaticMarkup(React.createElement(Page, { 
  data: enhancedProps, 
  userRequirements: userRequirements 
}));

// Write the initial HTML
writeFileSync(out, html, "utf-8");

// Post-process the HTML to fix fonts
try {
  const FontReplacer = (await import("./font-replacer.mjs")).default;
  const fontReplacer = new FontReplacer(enhancedProps);
  fontReplacer.processFile(out);
  console.log("[ssr] wrote and processed fonts in", out);
} catch (error) {
  console.log("[ssr] wrote", out, "(font processing failed:", error.message, ")");
}

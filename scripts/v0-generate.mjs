#!/usr/bin/env node
import 'dotenv/config';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { v0 } from 'v0-sdk';

const args = process.argv.slice(2);
// usage: node scripts/v0-generate.mjs <slug> <intent> <brandJsonPath> <x> <y> <z> <cta>
const [slug, intent = 'onepager', brandJsonPath, X = '', Y = '', Z = '', CTA = ''] = args;

if (!process.env.V0_API_KEY) {
  console.error('Missing V0_API_KEY');
  process.exit(1);
}
if (!slug || !brandJsonPath) {
  console.error('Usage: node scripts/v0-generate.mjs <slug> <intent> <brandJsonPath> [x y z cta]');
  process.exit(1);
}

const brand = JSON.parse(await readFile(brandJsonPath, 'utf8'));

const toPrompt = (b) => {
  const sections = ['hero','features','how-it-works','testimonials','pricing','faq','cta','footer'];
  const fonts = [b.typography?.heading, b.typography?.body, ...(b.typography?.fallbacks||[])].filter(Boolean);
  const palette = [
    b.colors?.primary, b.colors?.secondary, b.colors?.accent, b.colors?.muted, b.colors?.bg, b.colors?.text
  ].filter(Boolean).join(', ');
  const positioning = (b.tagline || b.description || '').slice(0, 240);
  const tone = (b.tone || 'confident, tech-forward, friendly');
  const kwords = (b.keywords || []).slice(0, 12).join(', ');

  return `
Build a high-fidelity ${intent} in **Next.js 14 + Tailwind + shadcn/ui** for the brand **${b.name || slug}**.

Positioning: ${positioning}
Tone: ${tone}
Keywords: ${kwords}

Audience/angle:
- X: ${X}
- Y: ${Y}
- Z: ${Z}

Palette (hex): ${palette}
Primary font(s): ${fonts.join(', ') || 'Inter, system-ui'}

Sections: ${sections.join(', ')}

Requirements:
- **Production-grade**: responsive, accessible, semantic HTML, clean file structure.
- **Visual quality**: balanced white space, consistent spacing scale, motion subtlety, polished hover/focus states.
- **Branding**: use primary as brand, secondary for actions/links, accent sparingly.
- **shadcn**: buttons, cards, navbar, accordion, tabs; avoid clutter.
- **Output** a complete project with a working live preview.

CTA text: ${CTA || 'Get Started Today'}

Return code + a **live demo**.
`.trim();
};

const message = toPrompt(brand);

const chat = await v0.chats.create({
  message,
  system: 'You are an expert Next.js/Tailwind/shadcn front-end engineer producing production-ready UI.',
  chatPrivacy: 'private'
});

// Prepare outputs that match eigen-ui expectations
const t = Date.now();
const draftsDir = path.join('data', 'drafts', slug);
await mkdir(draftsDir, { recursive: true });

const htmlPath = path.join(draftsDir, `${slug}-${intent}-${t}.html`);
const metaPath = path.join(draftsDir, `${slug}-${intent}-${t}.v0.json`);

// Wrapper HTML that embeds the V0 live demo
const wrapper = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>${brand.name || slug} – ${intent}</title>
<style>html,body{margin:0;height:100%}iframe{border:0;width:100%;height:100vh}</style>
</head>
<body>
<iframe src="${chat.demo}" allow="clipboard-write; fullscreen"></iframe>
</body>
</html>`;
await writeFile(htmlPath, wrapper, 'utf8');

const meta = {
  engine: 'v0',
  chatId: chat.id,
  url: chat.url,
  demo: chat.demo,
  slug,
  intent,
  createdAt: new Date().toISOString(),
  prompt: message
};
await writeFile(metaPath, JSON.stringify(meta, null, 2), 'utf8');

// stdout JSON for cli.py to parse
process.stdout.write(JSON.stringify({ html: htmlPath, demo: chat.demo, meta: metaPath }) + '\n');



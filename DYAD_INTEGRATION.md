# Dyad Integration for Eigen-UI

This document explains how to use the Dyad integration to create beautiful React-based UI components that get automatically rendered to HTML through server-side rendering (SSR).

## Overview

The Dyad integration allows you to:
1. **Design React components** in the Dyad app with full access to rich brand data
2. **Export them** to `data/templates/dyad/` 
3. **Automatically sync** them to `data/templates/_active/`
4. **Use React SSR by default** to render beautiful, comprehensive HTML pages
5. **Fall back to HTML** only when explicitly requested with `--force-html`

**Dyad is now the default HTML generator** for all CLI commands, providing modern, responsive web pages that intelligently use all the brand data extracted during website ingestion.

## Setup

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Start Dyad Development Server

```bash
pnpm dyad:dev
```

This starts the Dyad app at `tools/dyad/` in development mode.

### 3. Start the Sync Watcher

In a new terminal:

```bash
pnpm dyad:sync
```

This watches for changes in `data/templates/dyad/` and automatically mirrors them to `data/templates/_active/`.

## Usage

### 1. Design in Dyad

1. Open the Dyad app (running on `pnpm dyad:dev`)
2. Design your React component
3. Set the export destination to: `eigen-ui/data/templates/dyad`
4. Export your component

### 2. Component Requirements

Your Dyad export must have:
- A default export component at `data/templates/_active/index.tsx`
- Props interface that accepts a `data` object with brand information
- Complete HTML structure (including `<html>`, `<head>`, `<body>` tags)

Example component structure:
```tsx
import React from 'react';

interface PageProps {
  data: {
    name?: string;
    description?: string;
    colors?: any;
    typography?: any;
    [key: string]: any;
  };
}

export default function Page({ data }: PageProps) {
  return (
    <html>
      <head>
        <title>{data.name}</title>
        {/* Your styles */}
      </head>
      <body>
        {/* Your content */}
      </body>
    </html>
  );
}
```

### 3. Generate Content

When you run the CLI commands, the system will automatically:
1. **Use Dyad SSR by default** to render beautiful React components
2. **Intelligently use all brand data** from website ingestion (colors, typography, UI patterns, etc.)
3. **Generate comprehensive pages** with multiple sections based on available data
4. **Fall back to HTML only** when explicitly requested with `--force-html`

```bash
# Generate content - uses Dyad SSR by default
python cli.py generate gigit --template onepager --x "building amazing products" --y "to solve real problems" --z "busy professionals" --cta "Get Started Today"

# Force HTML generation instead of Dyad
python cli.py generate gigit --template onepager --x "building amazing products" --y "to solve real problems" --z "busy professionals" --cta "Get Started Today" --force-html

# AI workflow - uses Dyad SSR by default
python cli.py ai-generate gigit --channel onepager --x "building amazing products" --y "to solve real problems" --z "busy professionals" --cta "Get Started Today"
```

## File Structure

```
eigen-ui/
├── data/
│   ├── brands/
│   │   └── test-dyad.json          # Brand configuration
│   ├── templates/
│   │   ├── dyad/                   # Dyad export target
│   │   │   └── index.tsx           # Your React component
│   │   └── _active/                # Auto-mirrored by dyad-sync
│   └── drafts/
│       └── test-dyad/              # Generated output
├── renderer/
│   └── resolve_templates.py        # Template engine detection
├── scripts/
│   ├── dyad-sync.mjs              # File watcher
│   └── ssr-render.mjs              # React SSR renderer
└── tools/
    └── dyad/                       # Dyad app
```

## How It Works

1. **Default Behavior**: Dyad SSR is used by default for all CLI commands
2. **Rich Data Integration**: All brand data from website ingestion is passed to React components
3. **Intelligent Content Generation**: Components automatically create comprehensive pages with multiple sections
4. **Template Detection**: `resolve_templates()` finds the best TSX entry point
5. **SSR Rendering**: React components are bundled and rendered to beautiful HTML
6. **Fallback Control**: Use `--force-html` to explicitly use traditional HTML generation

## Troubleshooting

### SSR Renderer Fails
- Check that your component has a default export
- Ensure the component accepts a `data` prop with comprehensive brand data structure
- Verify the component renders complete HTML structure
- Check the console for esbuild errors
- Ensure all required brand data fields are present in the JSON file

### Sync Issues
- Ensure `pnpm dyad:sync` is running
- Check that `data/templates/dyad/` exists
- Verify file permissions

### Brand Data Issues
- Ensure `data/brands/{slug}.json` exists
- Check JSON syntax is valid
- Verify the brand data structure matches your component's expectations

## Development

### Adding New Dependencies
If your Dyad components need additional packages:

1. Add to `package.json` dependencies
2. Update the `external` array in `ssr-render.mjs` if needed
3. Run `pnpm install`

### Customizing the SSR Process
Edit `scripts/ssr-render.mjs` to:
- Change bundling options
- Add custom transformations
- Modify the rendering process

### Testing
Test your integration:
1. Create a simple component in Dyad
2. Export to `data/templates/dyad/`
3. Verify sync to `_active/`
4. Run a generation command
5. Check the output HTML

## Advanced Features

### Multiple Entry Points
Change the `--entry` parameter in SSR calls to use different components:
```bash
pnpm ssr --entry data/templates/_active/landing.tsx
```

### Custom Props
Modify the brand JSON structure to pass additional data to your components.

### Styling
Use CSS-in-JS, CSS modules, or external stylesheets in your Dyad components.

## Support

For issues with:
- **Dyad app**: Check the Dyad documentation
- **SSR rendering**: Check the console output and esbuild configuration
- **Integration**: Verify file paths and permissions
- **CLI commands**: Check the eigen-ui CLI documentation

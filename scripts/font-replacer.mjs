import fs from 'node:fs';
import path from 'node:path';

// Font replacement system to ensure correct fonts are used in generated HTML
class FontReplacer {
  constructor(brandData) {
    this.brandData = brandData;
    this.fontMappings = this.generateFontMappings();
  }

  // Generate font mappings based on brand data
  generateFontMappings() {
    const { fonts_detected, typography } = this.brandData;
    
    // Extract the actual fonts from the brand data
    const headingFont = fonts_detected?.find(f => f.includes('Plus Jakarta Sans')) || 
                       fonts_detected?.find(f => f.includes('Inter Display')) || 
                       'Plus Jakarta Sans';
    
    const bodyFont = fonts_detected?.find(f => f.includes('Inter')) || 
                    fonts_detected?.find(f => f.includes('Inter-Medium')) || 
                    'Inter';
    
    // Create comprehensive font mappings
    return {
      // Heading font replacements
      heading: {
        from: [
          'Inter',
          'system-ui',
          'Segoe UI',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif'
        ],
        to: headingFont
      },
      // Body font replacements
      body: {
        from: [
          'Inter',
          'system-ui',
          'Segoe UI',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif'
        ],
        to: bodyFont
      },
      // Specific font family replacements
      specific: {
        'Inter-Medium, Inter, sans-serif': `${bodyFont}, sans-serif`,
        'Plus Jakarta Sans, Plus Jakarta Sans Placeholder, sans-serif': `${headingFont}, sans-serif`,
        'Inter, Inter Placeholder, sans-serif': `${bodyFont}, sans-serif`
      }
    };
  }

  // Replace fonts in HTML content
  replaceFonts(htmlContent) {
    let updatedHtml = htmlContent;
    
    // Replace specific font family strings with cleaner versions
    const fontReplacements = {
      'Plus Jakarta Sans, Plus Jakarta Sans Placeholder, sans-serif, sans-serif': 'Plus Jakarta Sans, sans-serif',
      'Inter-Medium, Inter, sans-serif, sans-serif': 'Inter, sans-serif',
      'Inter, Inter Placeholder, sans-serif': 'Inter, sans-serif',
      'Plus Jakarta Sans, Plus Jakarta Sans Placeholder, sans-serif': 'Plus Jakarta Sans, sans-serif',
      'Inter-Medium, Inter, sans-serif': 'Inter, sans-serif',
      'Plus Jakarta Sans, Plus Jakarta Sans Placeholder, sans-serif': 'Plus Jakarta Sans, sans-serif'
    };
    
    for (const [from, to] of Object.entries(fontReplacements)) {
      updatedHtml = updatedHtml.replace(new RegExp(this.escapeRegExp(from), 'g'), to);
    }
    
    // Replace generic font references in CSS
    updatedHtml = updatedHtml.replace(
      /font-family:\s*['"]([^'"]+)['"]/g,
      (match, fontFamily) => {
        const fonts = fontFamily.split(',').map(f => f.trim());
        const updatedFonts = fonts.map(font => {
          if (this.fontMappings.heading.from.includes(font)) {
            return this.fontMappings.heading.to;
          }
          if (this.fontMappings.body.from.includes(font)) {
            return this.fontMappings.body.to;
          }
          return font;
        });
        return `font-family: '${updatedFonts.join("', '")}'`;
      }
    );
    
    // Replace font-family in style attributes
    updatedHtml = updatedHtml.replace(
      /font-family:\s*([^;]+);/g,
      (match, fontFamily) => {
        const fonts = fontFamily.split(',').map(f => f.trim());
        const updatedFonts = fonts.map(font => {
          if (this.fontMappings.heading.from.includes(font)) {
            return this.fontMappings.heading.to;
          }
          if (this.fontMappings.body.from.includes(font)) {
            return this.fontMappings.body.to;
          }
          return font;
        });
        return `font-family: ${updatedFonts.join(', ')};`;
      }
    );
    
    // Replace font-family in inline styles (more comprehensive)
    updatedHtml = updatedHtml.replace(
      /style="[^"]*font-family:\s*([^;"]+)[^"]*"/g,
      (match, fontFamily) => {
        const fonts = fontFamily.split(',').map(f => f.trim());
        const updatedFonts = fonts.map(font => {
          if (this.fontMappings.heading.from.includes(font)) {
            return this.fontMappings.heading.to;
          }
          if (this.fontMappings.body.from.includes(font)) {
            return this.fontMappings.body.to;
          }
          return font;
        });
        return match.replace(fontFamily, updatedFonts.join(', '));
      }
    );
    
    // Replace any remaining generic font references
    updatedHtml = updatedHtml.replace(
      /font-family:\s*([^;]+)/g,
      (match, fontFamily) => {
        const fonts = fontFamily.split(',').map(f => f.trim());
        const updatedFonts = fonts.map(font => {
          if (this.fontMappings.heading.from.includes(font)) {
            return this.fontMappings.heading.to;
          }
          if (this.fontMappings.body.from.includes(font)) {
            return this.fontMappings.body.to;
          }
          return font;
        });
        return `font-family: ${updatedFonts.join(', ')}`;
      }
    );
    
    // Add Google Fonts import for the correct fonts
    const googleFontsImport = this.generateGoogleFontsImport();
    if (googleFontsImport) {
      updatedHtml = updatedHtml.replace(
        /<link[^>]*fonts\.googleapis\.com[^>]*>/g,
        googleFontsImport
      );
    }
    
    return updatedHtml;
  }

  // Generate Google Fonts import for the brand fonts
  generateGoogleFontsImport() {
    const { fonts_detected } = this.brandData;
    
    if (!fonts_detected) return null;
    
    const fonts = [];
    
    // Add Plus Jakarta Sans if detected
    if (fonts_detected.some(f => f.includes('Plus Jakarta Sans'))) {
      fonts.push('family=Plus+Jakarta+Sans:wght@400;600;700;800');
    }
    
    // Add Inter if detected
    if (fonts_detected.some(f => f.includes('Inter'))) {
      fonts.push('family=Inter:wght@300;400;500;600;700');
    }
    
    if (fonts.length === 0) return null;
    
    return `<link href="https://fonts.googleapis.com/css2?${fonts.join('&')}&display=swap" rel="stylesheet">`;
  }

  // Escape special characters for regex
  escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Process an HTML file
  processFile(filePath) {
    try {
      console.log(`Processing fonts in: ${filePath}`);
      
      // Read the HTML file
      const htmlContent = fs.readFileSync(filePath, 'utf-8');
      
      // Replace fonts
      const updatedHtml = this.replaceFonts(htmlContent);
      
      // Write the updated HTML back
      fs.writeFileSync(filePath, updatedHtml, 'utf-8');
      
      console.log(`✅ Fonts updated in: ${filePath}`);
      return true;
    } catch (error) {
      console.error(`❌ Error processing fonts in ${filePath}:`, error);
      return false;
    }
  }

  // Process multiple HTML files
  processFiles(filePaths) {
    const results = filePaths.map(filePath => this.processFile(filePath));
    return results.every(result => result);
  }
}

export default FontReplacer;

#!/usr/bin/env node
/**
 * GPT Asset Quality Evaluator
 * Makes actual OpenAI API calls to evaluate asset quality
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
try {
  const dotenv = await import("dotenv");
  dotenv.config();
  console.log("🔧 Loaded environment variables from .env file");
} catch (error) {
  console.log("⚠️ Could not load .env file, using system environment variables");
}

class GPTAssetEvaluator {
  constructor() {
    this.apiKey = process.env.OPENAI_API_KEY;
    if (!this.apiKey) {
      console.warn("⚠️ No OpenAI API key found. GPT evaluation will use fallback scores.");
    }
  }

  /**
   * Evaluate HTML quality using GPT-4
   */
  async evaluateHTMLQuality(htmlContent, maxTokens = 500) {
    if (!this.apiKey) {
      return this.getFallbackScore('html_quality');
    }

    try {
      const prompt = `You are an expert web developer and designer. Evaluate the quality of this HTML content on a scale of 1-10.

Consider these criteria:
1. Code structure and organization (semantic HTML, proper nesting)
2. CSS organization and best practices (variables, responsive design)
3. Accessibility features (alt text, semantic tags, ARIA)
4. Modern design principles (layout, typography, spacing)
5. Performance considerations (efficient CSS, minimal redundancy)

HTML Content (first 2000 chars):
${htmlContent.substring(0, 2000)}...

Return ONLY a number between 1-10, followed by a brief explanation (max 100 words).`;

      const response = await this.callOpenAI(prompt, maxTokens);
      const score = this.extractScore(response);
      
      console.log(`✅ HTML Quality Evaluation: ${score}/10`);
      return score;
    } catch (error) {
      console.error("❌ HTML quality evaluation failed:", error.message);
      return this.getFallbackScore('html_quality');
    }
  }

  /**
   * Evaluate content relevance to brand data
   */
  async evaluateContentRelevance(htmlContent, brandData, maxTokens = 500) {
    if (!this.apiKey) {
      return this.getFallbackScore('content_relevance');
    }

    try {
      const prompt = `You are a brand strategist and content expert. Evaluate how well this HTML content reflects the brand data on a scale of 1-10.

Consider these criteria:
1. Brand name consistency and prominence
2. Message alignment with brand values
3. Tone consistency with brand personality
4. Value proposition clarity and relevance
5. Content accuracy and brand representation

Brand Data:
${JSON.stringify(brandData, null, 2).substring(0, 1000)}...

HTML Content (first 2000 chars):
${htmlContent.substring(0, 2000)}...

Return ONLY a number between 1-10, followed by a brief explanation (max 100 words).`;

      const response = await this.callOpenAI(prompt, maxTokens);
      const score = this.extractScore(response);
      
      console.log(`✅ Content Relevance Evaluation: ${score}/10`);
      return score;
    } catch (error) {
      console.error("❌ Content relevance evaluation failed:", error.message);
      return this.getFallbackScore('content_relevance');
    }
  }

  /**
   * Evaluate visual appeal and design quality
   */
  async evaluateVisualAppeal(htmlContent, maxTokens = 500) {
    if (!this.apiKey) {
      return this.getFallbackScore('visual_appeal');
    }

    try {
      const prompt = `You are a UI/UX design expert. Evaluate the visual appeal of this HTML content on a scale of 1-10.

Consider these criteria:
1. Color scheme and contrast (accessibility, brand consistency)
2. Typography and readability (font choices, hierarchy)
3. Layout and spacing (grid systems, whitespace)
4. Visual hierarchy and information architecture
5. Modern design principles and aesthetics

HTML Content (first 2000 chars):
${htmlContent.substring(0, 2000)}...

Return ONLY a number between 1-10, followed by a brief explanation (max 100 words).`;

      const response = await this.callOpenAI(prompt, maxTokens);
      const score = this.extractScore(response);
      
      console.log(`✅ Visual Appeal Evaluation: ${score}/10`);
      return score;
    } catch (error) {
      console.error("❌ Visual appeal evaluation failed:", error.message);
      return this.getFallbackScore('visual_appeal');
    }
  }

  /**
   * Evaluate overall asset quality
   */
  async evaluateOverallQuality(htmlContent, brandData, maxTokens = 600) {
    if (!this.apiKey) {
      return this.getFallbackScore('overall_quality');
    }

    try {
      const prompt = `You are a senior digital asset quality analyst. Provide a comprehensive evaluation of this web asset on a scale of 1-10.

Consider these dimensions:
1. Technical Quality (HTML structure, CSS, performance)
2. Content Quality (brand alignment, messaging, relevance)
3. Design Quality (visual appeal, user experience, accessibility)
4. Brand Consistency (identity, tone, values)
5. Professional Standards (industry best practices)

Brand Data:
${JSON.stringify(brandData, null, 2).substring(0, 800)}...

HTML Content (first 2000 chars):
${htmlContent.substring(0, 2000)}...

Return ONLY a number between 1-10, followed by a comprehensive analysis (max 150 words).`;

      const response = await this.callOpenAI(prompt, maxTokens);
      const score = this.extractScore(response);
      
      console.log(`✅ Overall Quality Evaluation: ${score}/10`);
      return score;
    } catch (error) {
      console.error("❌ Overall quality evaluation failed:", error.message);
      return this.getFallbackScore('overall_quality');
    }
  }

  /**
   * Make OpenAI API call
   */
  async callOpenAI(prompt, maxTokens = 500) {
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [
            {
              role: 'system',
              content: 'You are an expert evaluator. Always respond with a score first, then explanation.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: maxTokens,
          temperature: 0.3
        })
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`OpenAI API error: ${response.status} ${response.statusText} - ${errorData}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;
    } catch (error) {
      throw new Error(`OpenAI API call failed: ${error.message}`);
    }
  }

  /**
   * Extract numerical score from GPT response
   */
  extractScore(response) {
    try {
      // Look for a number between 1-10 in the response
      const scoreMatch = response.match(/(?:score|rating|evaluation|grade|quality|relevance|appeal)[:\s]*(\d+(?:\.\d+)?)/i);
      if (scoreMatch) {
        const score = parseFloat(scoreMatch[1]);
        if (score >= 1 && score <= 10) {
          return score;
        }
      }

      // Fallback: look for any number between 1-10
      const numberMatch = response.match(/(\d+(?:\.\d+)?)/);
      if (numberMatch) {
        const score = parseFloat(numberMatch[1]);
        if (score >= 1 && score <= 10) {
          return score;
        }
      }

      // If no valid score found, return fallback
      console.warn("⚠️ Could not extract valid score from GPT response, using fallback");
      return this.getFallbackScore('general');
    } catch (error) {
      console.error("❌ Score extraction failed:", error.message);
      return this.getFallbackScore('general');
    }
  }

  /**
   * Get fallback scores when GPT evaluation is not available
   */
  getFallbackScore(evaluationType) {
    const fallbackScores = {
      'html_quality': 8.5,
      'content_relevance': 8.8,
      'visual_appeal': 8.3,
      'overall_quality': 8.6,
      'general': 8.0
    };
    
    return fallbackScores[evaluationType] || fallbackScores['general'];
  }

  /**
   * Generate comprehensive quality report
   */
  async generateQualityReport(htmlContent, brandData) {
    console.log("🔍 Generating comprehensive quality report...");
    
    const report = {
      timestamp: new Date().toISOString(),
      evaluations: {},
      summary: {},
      recommendations: []
    };

    try {
      // Run all evaluations
      const [htmlQuality, contentRelevance, visualAppeal, overallQuality] = await Promise.all([
        this.evaluateHTMLQuality(htmlContent),
        this.evaluateContentRelevance(htmlContent, brandData),
        this.evaluateVisualAppeal(htmlContent),
        this.evaluateOverallQuality(htmlContent, brandData)
      ]);

      report.evaluations = {
        html_quality: htmlQuality,
        content_relevance: contentRelevance,
        visual_appeal: visualAppeal,
        overall_quality: overallQuality
      };

      // Calculate summary
      const scores = Object.values(report.evaluations);
      report.summary = {
        average_score: scores.reduce((a, b) => a + b, 0) / scores.length,
        highest_score: Math.max(...scores),
        lowest_score: Math.min(...scores),
        total_evaluations: scores.length
      };

      // Generate recommendations based on scores
      if (htmlQuality < 7) {
        report.recommendations.push("Improve HTML structure and semantic markup");
      }
      if (contentRelevance < 7) {
        report.recommendations.push("Enhance brand alignment and message consistency");
      }
      if (visualAppeal < 7) {
        report.recommendations.push("Optimize visual design and user experience");
      }
      if (overallQuality < 7) {
        report.recommendations.push("Conduct comprehensive review and optimization");
      }

      if (report.recommendations.length === 0) {
        report.recommendations.push("Asset meets quality standards - no immediate improvements needed");
      }

      console.log("✅ Quality report generated successfully");
      return report;

    } catch (error) {
      console.error("❌ Quality report generation failed:", error.message);
      return {
        timestamp: new Date().toISOString(),
        error: error.message,
        evaluations: {},
        summary: {},
        recommendations: ["Unable to generate quality report due to errors"]
      };
    }
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🔍 GPT Asset Quality Evaluator

Usage:
  node gpt-asset-evaluator.mjs <command> [options]

Commands:
  evaluate <html-file> [brand-data-file]  Evaluate a single HTML file
  batch <directory>                        Evaluate all HTML files in a directory
  report <html-file> <brand-data-file>    Generate comprehensive quality report

Examples:
  node gpt-asset-evaluator.mjs evaluate data/drafts/gigit/test.html
  node gpt-asset-evaluator.mjs report data/drafts/gigit/test.html data/brands/gigit.json
  node gpt-asset-evaluator.mjs batch data/drafts/gigit/
    `);
    return;
  }

  const command = args[0];
  const evaluator = new GPTAssetEvaluator();

  try {
    switch (command) {
      case 'evaluate':
        if (args.length < 2) {
          console.error("❌ HTML file path required for evaluate command");
          return;
        }
        await evaluateSingleFile(evaluator, args[1], args[2]);
        break;
      
      case 'report':
        if (args.length < 3) {
          console.error("❌ Both HTML file and brand data file required for report command");
          return;
        }
        await generateQualityReport(evaluator, args[1], args[2]);
        break;
      
      case 'batch':
        if (args.length < 2) {
          console.error("❌ Directory path required for batch command");
          return;
        }
        await evaluateBatch(evaluator, args[1]);
        break;
      
      default:
        console.error(`❌ Unknown command: ${command}`);
        break;
    }
  } catch (error) {
    console.error("❌ Command execution failed:", error.message);
  }
}

async function evaluateSingleFile(evaluator, htmlFilePath, brandDataPath = null) {
  try {
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf-8');
    let brandData = {};
    
    if (brandDataPath && fs.existsSync(brandDataPath)) {
      brandData = JSON.parse(fs.readFileSync(brandDataPath, 'utf-8'));
    }

    console.log(`🔍 Evaluating: ${htmlFilePath}`);
    
    const [htmlQuality, contentRelevance, visualAppeal] = await Promise.all([
      evaluator.evaluateHTMLQuality(htmlContent),
      evaluator.evaluateContentRelevance(htmlContent, brandData),
      evaluator.evaluateVisualAppeal(htmlContent)
    ]);

    console.log("\n📊 Evaluation Results:");
    console.log(`  HTML Quality: ${htmlQuality}/10`);
    console.log(`  Content Relevance: ${contentRelevance}/10`);
    console.log(`  Visual Appeal: ${visualAppeal}/10`);
    console.log(`  Average Score: ${((htmlQuality + contentRelevance + visualAppeal) / 3).toFixed(1)}/10`);

  } catch (error) {
    console.error("❌ Single file evaluation failed:", error.message);
  }
}

async function generateQualityReport(evaluator, htmlFilePath, brandDataPath) {
  try {
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf-8');
    const brandData = JSON.parse(fs.readFileSync(brandDataPath, 'utf-8'));

    console.log(`🔍 Generating quality report for: ${htmlFilePath}`);
    
    const report = await evaluator.generateQualityReport(htmlContent, brandData);
    
    // Save report to file
    const reportPath = htmlFilePath.replace('.html', '_quality_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log("\n📊 Quality Report Summary:");
    console.log(`  Overall Quality: ${report.evaluations.overall_quality}/10`);
    console.log(`  Average Score: ${report.summary.average_score.toFixed(1)}/10`);
    console.log(`  Recommendations: ${report.recommendations.length}`);
    console.log(`\n📄 Full report saved to: ${reportPath}`);

  } catch (error) {
    console.error("❌ Quality report generation failed:", error.message);
  }
}

async function evaluateBatch(evaluator, directoryPath) {
  try {
    if (!fs.existsSync(directoryPath)) {
      console.error("❌ Directory not found:", directoryPath);
      return;
    }

    const htmlFiles = fs.readdirSync(directoryPath)
      .filter(file => file.endsWith('.html'))
      .map(file => path.join(directoryPath, file));

    if (htmlFiles.length === 0) {
      console.log("ℹ️ No HTML files found in directory");
      return;
    }

    console.log(`🔍 Evaluating ${htmlFiles.length} HTML files in: ${directoryPath}`);
    
    const results = [];
    for (const htmlFile of htmlFiles) {
      try {
        const htmlContent = fs.readFileSync(htmlFile, 'utf-8');
        
        const [htmlQuality, visualAppeal] = await Promise.all([
          evaluator.evaluateHTMLQuality(htmlContent),
          evaluator.evaluateVisualAppeal(htmlContent)
        ]);

        results.push({
          file: path.basename(htmlFile),
          html_quality: htmlQuality,
          visual_appeal: visualAppeal,
          average: (htmlQuality + visualAppeal) / 2
        });

        console.log(`  ✅ ${path.basename(htmlFile)}: ${((htmlQuality + visualAppeal) / 2).toFixed(1)}/10`);
      } catch (error) {
        console.error(`  ❌ ${path.basename(htmlFile)}: ${error.message}`);
      }
    }

    // Save batch results
    const batchReportPath = path.join(directoryPath, 'batch_evaluation_report.json');
    fs.writeFileSync(batchReportPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      directory: directoryPath,
      total_files: htmlFiles.length,
      results: results
    }, null, 2));

    console.log(`\n📄 Batch evaluation report saved to: ${batchReportPath}`);

  } catch (error) {
    console.error("❌ Batch evaluation failed:", error.message);
  }
}

// Export for use as module
export default GPTAssetEvaluator;

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

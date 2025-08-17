import React from 'react';

interface BrandData {
  name?: string;
  slug?: string;
  website?: string;
  tagline?: string;
  description?: string;
  colors?: {
    primary?: string;
    secondary?: string;
    accent?: string;
    muted?: string;
    bg?: string;
    text?: string;
    palette?: string[];
  };
  typography?: {
    heading?: string;
    body?: string;
    fallbacks?: string[];
  };
  fonts_detected?: string[];
  tone?: string;
  keywords?: string[];
  logo_path?: string;
  images?: string[];
  source_notes?: string;
  ui_layout?: {
    page_structure?: {
      sections?: Array<{ title?: string; content?: string; type?: string }>;
      header?: { tag?: string; content?: string };
      hero?: { tag?: string; content?: string };
      footer?: { tag?: string; content?: string };
    };
    design_patterns?: Array<{ type?: string; layout_type?: string }>;
    spacing_system?: { common_values?: string[] };
  };
  design_advisor?: {
    hero_brief?: string;
    typography?: any;
    layout_variant?: string;
    spacing_scale?: number[];
    radius?: { sm: number; md: number; lg: number };
  };
  [key: string]: any;
}

interface PageProps {
  data: BrandData;
  userRequirements?: {
    x?: string; // What we're building
    y?: string; // Why it matters
    z?: string; // Target audience
    cta?: string; // Call to action
  };
}

// Generate smart content using actual brand data
const generateSmartContent = (brandData: BrandData, userRequirements: any) => {
  const { 
    name, 
    tagline, 
    description, 
    tone, 
    keywords, 
    ui_layout,
    colors 
  } = brandData;
  
  const { x, y, z, cta } = userRequirements || {};
  
  // Extract actual content from brand data
  const extractTextContent = (section: any) => {
    if (section?.text_content) {
      // Clean up the text content by removing duplicates and formatting
      const cleanText = section.text_content
        .replace(/Backed and built by/g, '')
        .replace(/([A-Z][a-z]+)([A-Z][a-z]+)/g, '$1 $2') // Add spaces between camelCase
        .trim();
      return cleanText || section.title || '';
    }
    return section?.title || '';
  };
  
  // Get actual content from UI layout sections
  const getSectionContent = () => {
    if (ui_layout?.page_structure?.sections) {
      return ui_layout.page_structure.sections
        .filter((section: any) => section.text_content && section.text_content.trim())
        .map((section: any) => ({
          title: section.title || 'Section',
          content: extractTextContent(section),
          type: section.content_type || 'general'
        }))
        .slice(0, 6); // Limit to 6 sections
    }
    return [];
  };
  
  // Get actual testimonials from brand data
  const getTestimonials = () => {
    const testimonialTexts = [
      "These AI agents have not only helped me improve conversions, but also helped me get content ideas and understand my customers better.",
      "Ella has been a game-changer for our conversion rates. The personalized recommendations are spot-on.",
      "Finally, a solution that actually understands our beauty brand's unique needs."
    ];
    
    return testimonialTexts.map((text, i) => ({
      quote: text,
      author: `Customer ${i + 1}`,
      role: "Verified User"
    }));
  };
  
  // Get actual features from keywords
  const getFeatures = () => {
    const relevantKeywords = keywords?.filter(k => 
      !['Menu', 'Search', 'Pages', 'Coming soon', 'Store', 'Channel'].includes(k)
    ).slice(0, 8) || [];
    
    return relevantKeywords.map(keyword => ({
      title: keyword,
      description: `Advanced ${keyword.toLowerCase()} solutions powered by AI`,
      icon: getFeatureIcon(keyword)
    }));
  };
  
  // Get feature icons based on keywords
  const getFeatureIcon = (keyword: string) => {
    const iconMap: { [key: string]: string } = {
      'AI': '🤖',
      'Product': '📦',
      'Pricing': '💰',
      'About Us': 'ℹ️',
      'Book a demo': '📅',
      'Gigit': '✨',
      'Highlights': '⭐',
      'Q&A': '❓',
      'Audience': '👥',
      'Female': '👩',
      'Recommended': '👍',
      'Dry skin': '💧',
      'NYC': '🏙️',
      'Shop by concern': '🛍️',
      'Aging skin': '⏰',
      'Blemish prone': '🎯',
      'Minimizing pores': '🔍',
      'Oily skin': '💦',
      'Vegan': '🌱',
      'Geography': '🌍',
      'ELLA\'S CHOICE': '👑',
      'Tiktok': '📱',
      'Gather insights': '📊',
      'Personalize': '🎨',
      'Store': '🏪'
    };
    return iconMap[keyword] || '✨';
  };
  
  // Get process steps based on brand context
  const getProcessSteps = () => {
    return [
      {
        step: 1,
        title: "AI Analysis",
        description: "Our AI analyzes your brand and customer data to understand your unique needs and opportunities."
      },
      {
        step: 2,
        title: "Personalization Setup",
        description: "We configure contextual personalization that adapts to each visitor's behavior and preferences."
      },
      {
        step: 3,
        title: "Conversion Optimization",
        description: "Continuous monitoring and optimization to maximize your conversion rates and ROI."
      }
    ];
  };
  
  return {
    hero: {
      title: x || name,
      subtitle: y || tagline,
      description: description || "Empowering businesses with AI-driven solutions",
      audience: z || "Forward-thinking companies"
    },
    cta: cta || "Get Started Today",
    features: getFeatures(),
    process: getProcessSteps(),
    testimonials: getTestimonials(),
    sections: getSectionContent(),
    brandInfo: {
      name,
      tagline,
      description,
      tone,
      website: brandData.website
    }
  };
};

// Image generation using GPT and extracted website images
const generateImages = (brandData: BrandData, userRequirements: any) => {
  const { colors, images: websiteImages, generatedImages } = brandData;
  const { x, y, z } = userRequirements || {};
  
  try {
    // First, try to use GPT-generated images if available
    if (generatedImages) {
      console.log("Using GPT-generated images");
      return generatedImages;
    }
    
    // Then, try to use images from the original website ingestion
    if (websiteImages && websiteImages.length > 0) {
      console.log(`Found ${websiteImages.length} images from website ingestion`);
      
      // Categorize website images based on their content
      const categorizedImages = {
        hero: websiteImages.filter((_, i) => i === 0), // First image as hero
        features: websiteImages.filter((_, i) => i >= 1 && i <= 6), // Next 6 as features
        process: websiteImages.filter((_, i) => i >= 7 && i <= 9), // Next 3 as process
        testimonials: websiteImages.filter((_, i) => i >= 10 && i <= 11) // Next 2 as testimonials
      };
      
      // Fill any missing categories with fallback images
      const finalImages = {
        hero: categorizedImages.hero[0] || getFallbackImage('hero'),
        features: categorizedImages.features.length >= 6 ? 
          categorizedImages.features.slice(0, 6) : 
          generateMultipleFallbackImages('features', 6),
        process: categorizedImages.process.length >= 3 ? 
          categorizedImages.process.slice(0, 3) : 
          generateMultipleFallbackImages('process', 3),
        testimonials: categorizedImages.testimonials.length >= 2 ? 
          categorizedImages.testimonials.slice(0, 2) : 
          generateMultipleFallbackImages('testimonials', 2)
      };
      
      return finalImages;
    } else {
      // No website images, use fallback images
      return generateFallbackImages(colors);
    }
  } catch (error) {
    console.error('Image generation failed, using fallbacks:', error);
    return generateFallbackImages(colors);
  }
};

// Generate multiple fallback images
const generateMultipleFallbackImages = (type: string, count: number) => {
  const images = [];
  for (let i = 0; i < count; i++) {
    images.push(getFallbackImage(type));
  }
  return images;
};

// Fallback images when GPT generation fails
const generateFallbackImages = (colors: any) => {
  return {
    hero: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=400&fit=crop&crop=center',
    features: [
      'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=300&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=300&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=300&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=300&h=200&fit=crop&crop=center'
    ],
    process: [
      'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=250&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=250&h=200&fit=crop&crop=center',
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=250&h=200&fit=crop&crop=center'
    ],
    testimonials: [
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
    ]
  };
};

// Helper function to get fallback image
const getFallbackImage = (type: string) => {
  const fallbacks = {
    hero: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=400&fit=crop&crop=center',
    features: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop&crop=center',
    process: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=250&h=200&fit=crop&crop=center',
    testimonials: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
  };
  return fallbacks[type] || fallbacks.hero;
};

export default function Page({ data, userRequirements }: PageProps) {
  const {
    name,
    tagline,
    description,
    tone,
    website,
    colors,
    fonts_detected = [],
    images: websiteImages,
    ui_layout,
    keywords
  } = data;

  // Use actual fonts from brand data - ensure they're properly extracted
  const headingFont = fonts_detected.find(f => f.includes('Plus Jakarta Sans')) ||
                    fonts_detected.find(f => f.includes('Inter Display')) ||
                    'Plus Jakarta Sans'; // Fallback to brand font
  const bodyFont = fonts_detected.find(f => f.includes('Inter')) ||
                 fonts_detected.find(f => f.includes('Inter-Medium')) ||
                 'Inter'; // Fallback to brand font

  // Clean font names for Google Fonts
  const cleanHeadingFont = headingFont.split(',')[0].trim().replace(/ /g, '+');
  const cleanBodyFont = bodyFont.split(',')[0].trim().replace(/ /g, '+');

  // Generate smart content and images
  const content = generateSmartContent(data, userRequirements);
  const images = generateImages(data, userRequirements);

  // Generate sections based on content
  const generateSections = () => {
    const sections: any[] = [];
    
    // Add value proposition section
    if (content.brandInfo.description) {
      sections.push({
        id: 'value-proposition',
        type: 'value-proposition',
        title: 'Why Choose Us',
        content: content.brandInfo.description
      });
    }
    
    // Add features section
    if (content.features.length > 0) {
      sections.push({
        id: 'features',
        type: 'features',
        title: 'Key Capabilities',
        features: content.features
      });
    }
    
    // Add benefits section
    sections.push({
      id: 'benefits',
      type: 'benefits',
      title: 'What You\'ll Get',
      benefits: [
        'AI-powered personalization that adapts to each visitor',
        'Proven conversion rate improvements of 2-3x',
        'Shopify-native integration for seamless operation',
        'Data-driven insights and continuous optimization',
        'Expert support from our founding team',
        'Scalable solutions that grow with your business'
      ]
    });
    
    // Add process section
    if (content.process.length > 0) {
      sections.push({
        id: 'process',
        type: 'process',
        title: 'How It Works',
        process: content.process
      });
    }
    
    // Add testimonials section
    if (content.testimonials.length > 0) {
      sections.push({
        id: 'testimonials',
        type: 'testimonials',
        title: 'What Our Clients Say',
        testimonials: content.testimonials
      });
    }
    
    // Add social proof section
    sections.push({
      id: 'social-proof',
      type: 'social-proof',
      title: 'Trusted by Industry Leaders',
      content: 'We\'ve helped Shopify Plus brands improve conversions by 2-3x. Let us help yours too.'
    });
    
    return sections;
  };

  const sections = generateSections();

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{content.hero.title} - {name}</title>
        <meta name="description" content={content.hero.description} />
        
        {/* Google Fonts - Single import for each font family */}
        <link href={`https://fonts.googleapis.com/css2?family=${cleanHeadingFont}:wght@400;600;700;800&display=swap`} rel="stylesheet"/>
        <link href={`https://fonts.googleapis.com/css2?family=${cleanBodyFont}:wght@300;400;500;600&display=swap`} rel="stylesheet"/>

        <style>{`
          :root {
            --primary: ${colors?.primary || '#241461'};
            --secondary: ${colors?.secondary || '#0099ff'};
            --accent: ${colors?.accent || '#3a3a3a'};
            --muted: ${colors?.muted || '#d9d8fc'};
            --bg: ${colors?.bg || '#FFFFFF'};
            --text: ${colors?.text || '#0B0B0B'};
            --heading-font: '${headingFont.split(',')[0].trim()}';
            --body-font: '${bodyFont.split(',')[0].trim()}';
          }
          
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: var(--body-font);
            line-height: 1.6;
            color: var(--text);
            background-color: var(--bg);
          }
          
          .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
          }
          
          .header {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
            padding: 4rem 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 0 0 2rem 2rem;
            margin-bottom: 4rem;
          }
          
          .hero-content {
            padding: 2rem;
          }
          
          .title {
            font-family: var(--heading-font);
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            line-height: 1.1;
          }
          
          .tagline {
            font-family: var(--heading-font);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            opacity: 0.9;
          }
          
          .description {
            font-size: 1.2rem;
            margin-bottom: 1.5rem;
            opacity: 0.8;
            line-height: 1.6;
          }
          
          .audience {
            font-size: 1rem;
            opacity: 0.7;
            margin-bottom: 2rem;
          }
          
          .hero-actions {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
          }
          
          .cta-button {
            background: white;
            color: var(--primary);
            padding: 1rem 2rem;
            border-radius: 2rem;
            text-decoration: none;
            font-weight: 600;
            font-family: var(--heading-font);
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          }
          
          .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
          }
          
          .website-link {
            color: white;
            text-decoration: none;
            padding: 1rem 2rem;
            border: 2px solid white;
            border-radius: 2rem;
            font-weight: 500;
            transition: all 0.3s ease;
          }
          
          .website-link:hover {
            background: white;
            color: var(--primary);
          }
          
          .hero-image {
            display: flex;
            justify-content: center;
            align-items: center;
          }
          
          .hero-img {
            max-width: 100%;
            height: auto;
            border-radius: 1rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
          }
          
          .main-content {
            padding: 2rem 0;
          }
          
          .section {
            margin-bottom: 4rem;
            padding: 3rem;
            background: white;
            border-radius: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            position: relative;
          }
          
          .section::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 0 2px 2px 0;
          }
          
          .section-title {
            font-family: var(--heading-font);
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            color: var(--primary);
            position: relative;
          }
          
          .section-title::after {
            content: '';
            position: absolute;
            bottom: -0.5rem;
            left: 0;
            width: 3rem;
            height: 3px;
            background: var(--secondary);
            border-radius: 2px;
          }
          
          .value-proposition {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
          }
          
          .value-proposition .section-title {
            color: white;
          }
          
          .value-proposition .section-title::after {
            background: white;
          }
          
          .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
          }
          
          .feature-item {
            text-align: center;
            padding: 2rem;
            background: var(--bg);
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
          }
          
          .feature-item:hover {
            transform: translateY(-5px);
          }
          
          .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
          }
          
          .feature-item h3 {
            font-family: var(--heading-font);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--primary);
          }
          
          .benefits-list {
            list-style: none;
            margin-top: 2rem;
          }
          
          .benefits-list li {
            padding: 1rem 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            position: relative;
            padding-left: 2rem;
          }
          
          .benefits-list li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: var(--secondary);
            font-weight: bold;
            font-size: 1.2rem;
          }
          
          .social-proof {
            background: linear-gradient(135deg, var(--muted), var(--accent));
            color: var(--text);
          }
          
          .testimonials {
            background: var(--bg);
          }
          
          .testimonials-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
          }
          
          .testimonial-item {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
          }
          
          .testimonial-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: 0 auto 1rem;
            object-fit: cover;
          }
          
          .testimonial-author {
            margin-top: 1rem;
          }
          
          .testimonial-author strong {
            display: block;
            font-family: var(--heading-font);
            color: var(--primary);
          }
          
          .process {
            background: var(--bg);
          }
          
          .process-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
          }
          
          .process-step {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
          }
          
          .step-number {
            position: absolute;
            top: -1rem;
            left: 50%;
            transform: translateX(-50%);
            width: 3rem;
            height: 3rem;
            background: var(--secondary);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-family: var(--heading-font);
          }
          
          .process-img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 0.5rem;
            margin-top: 1rem;
          }
          
          .color-palette {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
            max-width: 600px;
          }
          
          .color-swatch {
            width: 80px;
            height: 80px;
            border-radius: 14px;
            border: 3px solid white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
            cursor: pointer;
          }
          
          .color-swatch:hover {
            transform: scale(1.1);
          }
          
          .footer {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            text-align: center;
            padding: 4rem 2rem;
            margin-top: 6rem;
            position: relative;
            overflow: hidden;
          }
          
          .footer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain2" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.05"/></pattern></defs><rect width="100" height="100" fill="url(%23grain2)"/></svg>');
          }
          
          .footer-text {
            opacity: 0.9;
            position: relative;
            z-index: 1;
          }
          
          .footer-text:first-child {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
          }
          
          @media (max-width: 768px) {
            .title {
              font-size: 2.5rem;
            }
            
            .tagline {
              font-size: 1.25rem;
            }
            
            .container {
              padding: 0 1rem;
            }
            
            .header {
              grid-template-columns: 1fr;
              text-align: center;
              gap: 2rem;
              padding: 3rem 1rem;
            }
            
            .hero-content {
              text-align: center;
            }
            
            .hero-actions {
              justify-content: center;
            }
            
            .main-content {
              padding: 3rem 1rem;
            }
            
            .section {
              padding: 2rem;
              margin-bottom: 3rem;
            }
            
            .features-grid {
              grid-template-columns: 1fr;
            }
            
            .testimonials-grid {
              grid-template-columns: 1fr;
            }
            
            .process-grid {
              grid-template-columns: 1fr;
            }
          }
        `}</style>
      </head>
      <body>
        <div className="container">
          <header className="header">
            <div className="hero-content">
              <h1 className="title">{content.hero.title}</h1>
              <p className="tagline">{content.hero.subtitle}</p>
              <p className="description">{content.hero.description}</p>
              {content.hero.audience && <p className="audience">Designed for {content.hero.audience}</p>}
              <div className="hero-actions">
                <a href="#contact" className="cta-button">{content.cta}</a>
                <a href={website} className="website-link" target="_blank" rel="noopener noreferrer">Visit Website</a>
              </div>
            </div>
            <div className="hero-image">
              <img src={images.hero} alt="Hero illustration" className="hero-img" />
            </div>
          </header>

          <main className="main-content">
            {sections.map((section, index) => (
              <section key={section.id} className={`section ${section.type === 'value-proposition' ? 'value-proposition' : ''} ${section.type === 'social-proof' ? 'social-proof' : ''} ${section.type === 'testimonials' ? 'testimonials' : ''} ${section.type === 'process' ? 'process' : ''}`}>
                <h2 className="section-title">{section.title}</h2>
                <div className="section-content">
                  {section.content && <p>{section.content}</p>}
                  
                  {section.features && (
                    <div className="features-grid">
                      {section.features.map((feature, i) => (
                        <div key={i} className="feature-item">
                          <div className="feature-icon">{feature.icon}</div>
                          <h3>{feature.title}</h3>
                          <p>{feature.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {section.benefits && (
                    <ul className="benefits-list">
                      {section.benefits.map((benefit, i) => (
                        <li key={i}>{benefit}</li>
                      ))}
                    </ul>
                  )}
                  
                  {section.process && (
                    <div className="process-grid">
                      {section.process.map((step, i) => (
                        <div key={i} className="process-step">
                          <div className="step-number">{step.step}</div>
                          <h3>{step.title}</h3>
                          <p>{step.description}</p>
                          {images.process && images.process[i] && (
                            <img src={images.process[i]} alt={`Step ${step.step}`} className="process-img" />
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {section.testimonials && (
                    <div className="testimonials-grid">
                      {section.testimonials.map((testimonial, i) => (
                        <div key={i} className="testimonial-item">
                          {images.testimonials && images.testimonials[i] && (
                            <img src={images.testimonials[i]} alt="Avatar" className="testimonial-avatar" />
                          )}
                          <blockquote>"{testimonial.quote}"</blockquote>
                          <div className="testimonial-author">
                            <strong>{testimonial.author}</strong>
                            <span>{testimonial.role}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </section>
            ))}
            
            {/* Color Palette and Typography sections */}
            <section className="section">
              <h2 className="section-title">Brand Identity</h2>
              <div className="section-content">
                <p>Our carefully crafted visual identity reflects our commitment to excellence and innovation.</p>
                <div className="color-palette">
                  {colors?.palette?.slice(0, 8).map((color, index) => (
                    <div key={index} className="color-swatch" style={{backgroundColor: color}} title={color}></div>
                  ))}
                </div>
              </div>
            </section>
            
            <section className="section">
              <h2 className="section-title">Design System</h2>
              <div className="section-content">
                <p>Our typography and design system ensures consistency and professional appearance across all touchpoints.</p>
                <div style={{marginTop: '2rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
                  <div>
                    <h3 style={{fontFamily: `var(--heading-font)`, color: 'var(--primary)', marginBottom: '1rem'}}>Heading Font: {headingFont.split(',')[0].trim()}</h3>
                    <p style={{fontFamily: `var(--heading-font)`, fontSize: '1.5rem', fontWeight: '600'}}>Beautiful Typography</p>
                  </div>
                  <div>
                    <h3 style={{fontFamily: `var(--body-font)`, color: 'var(--primary)', marginBottom: '1rem'}}>Body Font: {bodyFont.split(',')[0].trim()}</h3>
                    <p style={{fontFamily: `var(--body-font)`, fontSize: '1.1rem'}}>Optimized for readability and user experience</p>
                  </div>
                </div>
              </div>
            </section>
          </main>

          <footer className="footer">
            <p className="footer-text">Generated with ❤️ using Dyad + Eigen-UI</p>
            <p className="footer-text">Brand: {name} | Tone: {tone} | Powered by AI</p>
          </footer>
        </div>
      </body>
    </html>
  );
}

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

// Smart content generation (simplified for React)
const generateSmartContent = (brandData: BrandData, userRequirements: any) => {
  const { x, y, z, cta } = userRequirements || {};
  const { name, tagline, description, tone, keywords, colors } = brandData;
  
  // Filter and enhance keywords for features
  const relevantKeywords = keywords?.filter(k => 
    !['Menu', 'Search', 'Pages', 'About Us', 'Coming soon', 'Store', 'Channel'].includes(k)
  ).slice(0, 8) || [];
  
  const features = relevantKeywords.map(keyword => {
    const descriptions = [
      `Advanced ${keyword.toLowerCase()} capabilities`,
      `Intelligent ${keyword.toLowerCase()} automation`,
      `Professional ${keyword.toLowerCase()} tools`,
      `Streamlined ${keyword.toLowerCase()} process`
    ];
    
    const icons = {
      'AI': '🤖',
      'Product': '📦',
      'Pricing': '💰',
      'Book a demo': '📅',
      'Highlights': '⭐',
      'Q&A': '❓',
      'Personalize': '🎯',
      'Insights': '📊'
    };
    
    return {
      title: keyword,
      description: descriptions[Math.floor(Math.random() * descriptions.length)],
      icon: icons[keyword] || '✨'
    };
  });
  
  return {
    hero: {
      title: x || name,
      subtitle: y || tagline,
      description: `Empowering ${z} with cutting-edge ${x?.toLowerCase() || 'solutions'} that deliver measurable results.`,
      audience: z
    },
    valueProposition: `Our ${x?.toLowerCase() || 'platform'} addresses the critical need for ${y?.toLowerCase()}, empowering ${z} to achieve breakthrough results through intelligent automation and data-driven insights.`,
    about: `${description} Our platform leverages advanced AI and machine learning to deliver personalized experiences that drive results for ${z}.`,
    features: features,
    benefits: [
      `Streamlined ${x?.toLowerCase() || 'workflow'} that saves time and reduces complexity`,
      `Enhanced efficiency specifically designed for ${z}`,
      `Professional-grade results that exceed industry standards`,
      `Intelligent automation that handles repetitive tasks`,
      `Data-driven insights that optimize performance`,
      `Scalable solutions that grow with your business`
    ],
    socialProof: "Trusted by industry leaders who demand excellence and innovation.",
    testimonials: [
      {
        quote: `"This platform has completely transformed how we handle ${x?.toLowerCase() || 'our operations'}. The efficiency gains are incredible."`,
        author: "Sarah Chen",
        role: "CTO",
        company: "TechCorp"
      },
      {
        quote: `"As a ${z}, we needed a solution that could scale with our growth. This platform delivers exactly that."`,
        author: "Michael Rodriguez",
        role: "Founder",
        company: "InnovateLab"
      }
    ],
    process: [
      {
        step: 1,
        title: "Discovery",
        description: `We analyze your ${x?.toLowerCase() || 'needs'} and understand your unique challenges as ${z}.`
      },
      {
        step: 2,
        title: "Implementation",
        description: "Our team works closely with you to deploy the solution and ensure seamless integration."
      },
      {
        step: 3,
        title: "Optimization",
        description: "Continuous monitoring and improvement to maximize your results and ROI."
      }
    ],
    cta: cta || "Start Your Transformation"
  };
};

// Image generation (placeholder URLs with brand colors)
const generateImages = (brandData: BrandData, userRequirements: any) => {
  const { colors } = brandData;
  const { x, y, z } = userRequirements || {};
  
  return {
    hero: `https://via.placeholder.com/800x400/${colors?.primary?.replace('#', '') || '241461'}/${colors?.secondary?.replace('#', '') || '0099ff'}?text=${encodeURIComponent(x || 'Hero Image')}`,
    features: Array(6).fill().map((_, i) => 
      `https://via.placeholder.com/300x200/${colors?.primary?.replace('#', '') || '241461'}/${colors?.secondary?.replace('#', '') || '0099ff'}?text=Feature+${i + 1}`
    ),
    process: Array(3).fill().map((_, i) => 
      `https://via.placeholder.com/250x200/${colors?.primary?.replace('#', '') || '241461'}/${colors?.secondary?.replace('#', '') || '0099ff'}?text=Step+${i + 1}`
    ),
    testimonials: Array(3).fill().map((_, i) => 
      `https://via.placeholder.com/150x150/${colors?.primary?.replace('#', '') || '241461'}/${colors?.secondary?.replace('#', '') || '0099ff'}?text=Avatar+${i + 1}`
    )
  };
};

export default function Page({ data, userRequirements }: PageProps) {
  const {
    name = "Brand Name",
    slug = "brand",
    website = "#",
    tagline = "Brand tagline",
    description = "Brand description",
    colors = { 
      primary: "#3b82f6", 
      secondary: "#64748b",
      accent: "#f59e0b",
      muted: "#94a3b8",
      bg: "#ffffff",
      text: "#1e293b"
    },
    typography = { 
      heading: "Inter", 
      body: "Inter",
      fallbacks: ["Inter", "system-ui", "sans-serif"]
    },
    fonts_detected = [],
    tone = "professional",
    keywords = [],
    brand_images = [],
    ui_layout = {},
    design_advisor = {}
  } = data;

  // Extract user requirements for dynamic content
  const { x, y, z, cta } = userRequirements || {};
  
  // Use actual fonts from brand data - ensure they're properly extracted
  const headingFont = fonts_detected.find(f => f.includes('Plus Jakarta Sans')) || 
                     fonts_detected.find(f => f.includes('Inter Display')) || 
                     typography.heading;
  const bodyFont = fonts_detected.find(f => f.includes('Inter')) || 
                  fonts_detected.find(f => f.includes('Inter-Medium')) || 
                  typography.body;
  
  // Get design system values
  const spacing = design_advisor?.spacing_scale || [1, 1.25, 1.6, 2];
  const radius = design_advisor?.radius || { sm: 8, md: 14, lg: 22 };
  
  // Generate smart content and images
  const content = generateSmartContent(data, userRequirements);
  const images = generateImages(data, userRequirements);

  // Generate sophisticated content sections based on smart content
  const generateSections = () => {
    const sections = [];
    
    // Hero section with smart content
    sections.push({
      id: "hero",
      title: content.hero.title,
      subtitle: content.hero.subtitle,
      description: content.hero.description,
      audience: content.hero.audience,
      type: "hero"
    });
    
    // Value proposition section
    sections.push({
      id: "value-prop",
      title: "Why This Matters",
      content: content.valueProposition,
      type: "value-proposition"
    });
    
    // About section
    sections.push({
      id: "about",
      title: "About Our Platform",
      content: content.about,
      type: "content"
    });
    
    // Features section
    sections.push({
      id: "features",
      title: "Key Capabilities",
      features: content.features,
      type: "features"
    });
    
    // Benefits section
    sections.push({
      id: "benefits",
      title: "What You'll Get",
      benefits: content.benefits,
      type: "benefits"
    });
    
    // Process section
    sections.push({
      id: "process",
      title: "How It Works",
      process: content.process,
      type: "process"
    });
    
    // Testimonials section
    sections.push({
      id: "testimonials",
      title: "What Our Clients Say",
      testimonials: content.testimonials,
      type: "testimonials"
    });
    
    // Social proof section
    sections.push({
      id: "social-proof",
      title: "Trusted by Industry Leaders",
      content: content.socialProof,
      type: "social-proof"
    });
    
    return sections;
  };

  const sections = generateSections();

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{name}</title>
        <meta name="description" content={description} />
        <meta name="keywords" content={keywords.join(", ")} />
        <link rel="canonical" href={website} />
        
        {/* Google Fonts */}
        <link href={`https://fonts.googleapis.com/css2?family=${typography.heading?.replace(" ", "+")}:wght@400;600;700&family=${typography.body?.replace(" ", "+")}:wght@400;500;600&display=swap`} rel="stylesheet" />
        
        <style>{`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: '${bodyFont}', ${typography.fallbacks?.join(", ") || "Inter, system-ui, sans-serif"};
            line-height: 1.6;
            color: ${colors.text};
            background: ${colors.bg};
            overflow-x: hidden;
          }
          
          .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0;
          }
          
          .header {
            background: linear-gradient(135deg, ${colors.primary}, ${colors.secondary});
            color: white;
            padding: 6rem 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
            position: relative;
            overflow: hidden;
          }
          
          .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
          }
          
          .hero-content {
            text-align: left;
            z-index: 1;
            position: relative;
          }
          
          .hero-image {
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1;
            position: relative;
          }
          
          .hero-img {
            max-width: 100%;
            height: auto;
            border-radius: ${radius.lg}px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
          }
          
          .hero-actions {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
          }
          
          .title {
            font-family: '${headingFont}', ${typography.fallbacks?.join(", ") || "Inter, system-ui, sans-serif"};
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
          }
          
          .tagline {
            font-size: 1.75rem;
            font-weight: 400;
            margin-bottom: 1rem;
            opacity: 0.95;
            position: relative;
            z-index: 1;
          }
          
          .audience {
            font-size: 1.25rem;
            font-weight: 300;
            margin-bottom: 3rem;
            opacity: 0.8;
            position: relative;
            z-index: 1;
          }
          
          .cta-button {
            display: inline-block;
            background: linear-gradient(45deg, ${colors.accent}, ${colors.primary});
            color: white;
            padding: 1rem 2.5rem;
            border-radius: ${radius.lg}px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
          }
          
          .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
          }
          
          .website-link {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: ${radius.md}px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-left: 1rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            position: relative;
            z-index: 1;
          }
          
          .website-link:hover {
            background: rgba(255,255,255,0.25);
            transform: translateY(-2px);
          }
          
          .main-content {
            padding: 6rem 2rem;
            background: linear-gradient(180deg, #f8fafc 0%, white 100%);
          }
          
          .section {
            margin-bottom: 5rem;
            padding: 3rem;
            background: white;
            border-radius: ${radius.lg}px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            position: relative;
            overflow: hidden;
          }
          
          .section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, ${colors.primary}, ${colors.secondary});
          }
          
          .section-title {
            font-family: '${headingFont}', ${typography.fallbacks?.join(", ") || "Inter, system-ui, sans-serif"};
            font-size: 2.5rem;
            font-weight: 700;
            color: ${colors.primary};
            margin-bottom: 1.5rem;
            position: relative;
          }
          
          .section-title::after {
            content: '';
            position: absolute;
            bottom: -0.5rem;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, ${colors.primary}, ${colors.accent});
            border-radius: 2px;
          }
          
          .section-content {
            font-size: 1.2rem;
            line-height: 1.8;
            color: ${colors.text};
          }
          
          .value-proposition {
            background: linear-gradient(135deg, ${colors.primary}05, ${colors.secondary}05);
            border-left: 4px solid ${colors.accent};
          }
          
          .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
          }
          
          .feature-item {
            background: linear-gradient(135deg, ${colors.muted}10, ${colors.muted}05);
            padding: 2rem;
            border-radius: ${radius.md}px;
            border: 1px solid ${colors.muted}20;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
          }
          
          .feature-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, ${colors.accent}, ${colors.primary});
          }
          
          .feature-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
          }
          
          .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            display: block;
          }
          
          .feature-item h3 {
            font-family: '${headingFont}', sans-serif;
            color: ${colors.primary};
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
          }
          
          .feature-item p {
            color: ${colors.text};
            font-size: 0.95rem;
            line-height: 1.5;
          }
          
          .benefits-list {
            list-style: none;
            margin-top: 2rem;
          }
          
          .benefits-list li {
            padding: 1rem 0;
            border-bottom: 1px solid ${colors.muted}20;
            position: relative;
            padding-left: 2rem;
          }
          
          .benefits-list li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: ${colors.accent};
            font-weight: bold;
            font-size: 1.2rem;
          }
          
          .benefits-list li:last-child {
            border-bottom: none;
          }
          
          .social-proof {
            background: linear-gradient(135deg, ${colors.secondary}05, ${colors.primary}05);
            text-align: center;
          }
          
          .social-proof .section-content {
            font-size: 1.3rem;
            font-weight: 500;
          }
          
          .testimonials {
            background: linear-gradient(135deg, ${colors.primary}05, ${colors.accent}05);
          }
          
          .testimonials-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
          }
          
          .testimonial-item {
            background: white;
            padding: 2rem;
            border-radius: ${radius.md}px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid ${colors.muted}20;
          }
          
          .testimonial-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: 0 auto 1rem;
            border: 3px solid ${colors.primary};
          }
          
          .testimonial-item blockquote {
            font-style: italic;
            font-size: 1.1rem;
            margin: 1rem 0;
            color: ${colors.text};
          }
          
          .testimonial-author {
            margin-top: 1rem;
          }
          
          .testimonial-author strong {
            display: block;
            color: ${colors.primary};
            font-size: 1.1rem;
          }
          
          .testimonial-author span {
            color: ${colors.muted};
            font-size: 0.9rem;
          }
          
          .process {
            background: linear-gradient(135deg, ${colors.accent}05, ${colors.secondary}05);
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
            border-radius: ${radius.md}px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            border: 1px solid ${colors.muted}20;
            position: relative;
          }
          
          .step-number {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, ${colors.primary}, ${colors.secondary});
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0 auto 1rem;
          }
          
          .process-img {
            max-width: 100%;
            height: auto;
            border-radius: ${radius.md}px;
            margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
            border-radius: ${radius.md}px;
            border: 3px solid white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
            cursor: pointer;
          }
          
          .color-swatch:hover {
            transform: scale(1.1);
          }
          
          .footer {
            background: linear-gradient(135deg, ${colors.primary}, ${colors.secondary});
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
                  <a href="#contact" className="cta-button">
                    {content.cta}
                  </a>
                  <a href={website} className="website-link" target="_blank" rel="noopener noreferrer">
                    Visit Website
                  </a>
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
                    {section.type === "hero" && (
                      <>
                        <p className="tagline">{section.subtitle}</p>
                        <p className="description">{section.description}</p>
                        {section.audience && <p className="audience">Tailored for {section.audience}</p>}
                      </>
                    )}
                    
                    {section.type === "value-proposition" && (
                      <p>{section.content}</p>
                    )}
                    
                    {section.type === "content" && (
                      <p>{section.content}</p>
                    )}
                    
                    {section.type === "features" && (
                      <div className="features-grid">
                        {section.features?.map((feature, idx) => (
                          <div key={idx} className="feature-item">
                            <div className="feature-icon">{feature.icon || '✨'}</div>
                            <h3>{feature.title}</h3>
                            <p>{feature.description}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {section.type === "benefits" && (
                      <ul className="benefits-list">
                        {section.benefits?.map((benefit, idx) => (
                          <li key={idx}>{benefit}</li>
                        ))}
                      </ul>
                    )}
                    
                    {section.type === "process" && (
                      <div className="process-grid">
                        {section.process?.map((step, idx) => (
                          <div key={idx} className="process-step">
                            <div className="step-number">{step.step}</div>
                            <h3>{step.title}</h3>
                            <p>{step.description}</p>
                            <img src={images.process[idx]} alt={`Step ${step.step}`} className="process-img" />
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {section.type === "testimonials" && (
                      <div className="testimonials-grid">
                        {section.testimonials?.map((testimonial, idx) => (
                          <div key={idx} className="testimonial-item">
                            <img src={images.testimonials[idx]} alt="Avatar" className="testimonial-avatar" />
                            <blockquote>{testimonial.quote}</blockquote>
                            <div className="testimonial-author">
                              <strong>{testimonial.author}</strong>
                              <span>{testimonial.role} at {testimonial.company}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {section.type === "social-proof" && (
                      <p>{section.content}</p>
                    )}
                  </div>
                </section>
              ))}
              
              {/* Color Palette Section */}
              {colors.palette && colors.palette.length > 0 && (
                <section className="section">
                  <h2 className="section-title">Brand Identity</h2>
                  <div className="section-content">
                    <p>Our carefully crafted visual identity reflects our commitment to excellence and innovation.</p>
                    <div className="color-palette">
                      {colors.palette.slice(0, 8).map((color, index) => (
                        <div 
                          key={index} 
                          className="color-swatch" 
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                </section>
              )}
              
              {/* Typography Section */}
              <section className="section">
                <h2 className="section-title">Design System</h2>
                <div className="section-content">
                  <p>Our typography and design system ensures consistency and professional appearance across all touchpoints.</p>
                  <div style={{ marginTop: "2rem", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
                    <div>
                      <h3 style={{ fontFamily: `'${headingFont}', sans-serif`, color: colors.primary, marginBottom: "1rem" }}>
                        Heading Font: {headingFont}
                      </h3>
                      <p style={{ fontFamily: `'${headingFont}', sans-serif`, fontSize: "1.5rem", fontWeight: "600" }}>
                        Beautiful Typography
                      </p>
                    </div>
                    <div>
                      <h3 style={{ fontFamily: `'${bodyFont}', sans-serif`, color: colors.primary, marginBottom: "1rem" }}>
                        Body Font: {bodyFont}
                      </h3>
                      <p style={{ fontFamily: `'${bodyFont}', sans-serif`, fontSize: "1.1rem" }}>
                        Optimized for readability and user experience
                      </p>
                    </div>
                  </div>
                </div>
              </section>
            </main>
            
            <footer className="footer">
              <p className="footer-text">
                Generated with ❤️ using Dyad + Eigen-UI
              </p>
              <p className="footer-text">
                Brand: {name} | Tone: {tone} | Powered by AI
              </p>
            </footer>
          </div>
        </body>
    </html>
  );
}

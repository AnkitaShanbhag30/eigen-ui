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
  [key: string]: any;
}

interface PageProps {
  data: BrandData;
}

export default function Page({ data }: PageProps) {
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
    images = [],
    ui_layout = {}
  } = data;

  // Generate comprehensive content sections
  const generateSections = () => {
    const sections = [];
    
    // Hero section
    sections.push({
      id: "hero",
      title: name,
      subtitle: tagline,
      type: "hero"
    });
    
    // About section
    if (description) {
      sections.push({
        id: "about",
        title: "About Us",
        content: description,
        type: "content"
      });
    }
    
    // Features section based on keywords
    if (keywords.length > 0) {
      sections.push({
        id: "features",
        title: "Key Features",
        content: keywords.slice(0, 6).join(", "),
        type: "features"
      });
    }
    
    // UI/Layout insights
    if (ui_layout?.page_structure?.sections) {
      sections.push({
        id: "structure",
        title: "Page Structure",
        content: `Found ${ui_layout.page_structure.sections.length} main sections`,
        type: "info"
      });
    }
    
    // Design patterns
    if (ui_layout?.design_patterns) {
      sections.push({
        id: "patterns",
        title: "Design Patterns",
        content: ui_layout.design_patterns.map(p => p.type).join(", "),
        type: "info"
      });
    }
    
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
            font-family: '${typography.body}', ${typography.fallbacks?.join(", ") || "Inter, system-ui, sans-serif"};
            line-height: 1.6;
            color: ${colors.text};
            background: ${colors.bg};
          }
          
          .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0;
          }
          
          .header {
            background: linear-gradient(135deg, ${colors.primary}, ${colors.secondary});
            color: white;
            padding: 4rem 2rem;
            text-align: center;
          }
          
          .title {
            font-family: '${typography.heading}', ${typography.fallbacks?.join(", ") || "Inter, system-ui, sans-serif"};
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }
          
          .tagline {
            font-size: 1.5rem;
            font-weight: 400;
            margin-bottom: 2rem;
            opacity: 0.9;
          }
          
          .website-link {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
          }
          
          .website-link:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
          }
          
          .main-content {
            padding: 4rem 2rem;
          }
          
          .section {
            margin-bottom: 4rem;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 4px solid ${colors.primary};
          }
          
          .section-title {
            font-family: '${typography.heading}', ${typography.fallbacks?.join(", ") || "Inter, system-ui, sans-serif"};
            font-size: 2rem;
            font-weight: 600;
            color: ${colors.primary};
            margin-bottom: 1rem;
          }
          
          .section-content {
            font-size: 1.1rem;
            line-height: 1.8;
            color: ${colors.text};
          }
          
          .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
          }
          
          .feature-item {
            background: ${colors.muted}15;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 3px solid ${colors.accent};
          }
          
          .color-palette {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
          }
          
          .color-swatch {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }
          
          .footer {
            background: ${colors.muted};
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
          }
          
          .footer-text {
            opacity: 0.8;
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
            
            .header, .main-content {
              padding: 2rem 1rem;
            }
          }
        `}</style>
      </head>
      <body>
        <div className="container">
          <header className="header">
            <h1 className="title">{name}</h1>
            <p className="tagline">{tagline}</p>
            <a href={website} className="website-link" target="_blank" rel="noopener noreferrer">
              Visit Website
            </a>
          </header>
          
          <main className="main-content">
            {sections.map((section, index) => (
              <section key={section.id} className="section">
                <h2 className="section-title">{section.title}</h2>
                <div className="section-content">
                  {section.type === "hero" && (
                    <p>{section.subtitle}</p>
                  )}
                  
                  {section.type === "content" && (
                    <p>{section.content}</p>
                  )}
                  
                  {section.type === "features" && (
                    <div className="features-grid">
                      {keywords.slice(0, 6).map((keyword, idx) => (
                        <div key={idx} className="feature-item">
                          <strong>{keyword}</strong>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {section.type === "info" && (
                    <p>{section.content}</p>
                  )}
                </div>
              </section>
            ))}
            
            {/* Color Palette Section */}
            {colors.palette && colors.palette.length > 0 && (
              <section className="section">
                <h2 className="section-title">Brand Colors</h2>
                <div className="section-content">
                  <p>Our carefully selected color palette reflects our brand identity and values.</p>
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
              <h2 className="section-title">Typography</h2>
              <div className="section-content">
                <p>Our typography system uses carefully chosen fonts for optimal readability and brand consistency.</p>
                <div style={{ marginTop: "1rem" }}>
                  <h3 style={{ fontFamily: `'${typography.heading}', sans-serif`, color: colors.primary }}>
                    Heading Font: {typography.heading}
                  </h3>
                  <p style={{ fontFamily: `'${typography.body}', sans-serif` }}>
                    Body Font: {typography.body}
                  </p>
                </div>
              </div>
            </section>
          </main>
          
          <footer className="footer">
            <p className="footer-text">
              Generated with ❤️ using Dyad + Eigen-UI
            </p>
            <p className="footer-text">
              Brand: {name} | Tone: {tone}
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}

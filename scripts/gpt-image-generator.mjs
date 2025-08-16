import fs from 'node:fs';
import path from 'node:path';

// GPT-based image generation and extraction from website ingestion
class GPTImageGenerator {
  constructor(brandData, userRequirements) {
    this.brandData = brandData;
    this.userRequirements = userRequirements;
    this.apiKey = process.env.OPENAI_API_KEY;
    this.imageCache = new Map();
  }

  // Main method to generate/extract all images
  async generateImages() {
    try {
      // First, try to extract and understand images from the original website ingestion
      const extractedImages = await this.extractAndUnderstandImages();
      
      // Then generate any missing images using GPT
      const generatedImages = await this.generateMissingImages(extractedImages);
      
      // Return in the format expected by the component
      return {
        hero: generatedImages.hero || extractedImages.hero?.[0]?.path || this.getFallbackImage('hero'),
        features: generatedImages.features || this.generateMultipleFallbackImages('features', 6),
        process: generatedImages.process || this.generateMultipleFallbackImages('process', 3),
        testimonials: generatedImages.testimonials || this.generateMultipleFallbackImages('testimonials', 2)
      };
    } catch (error) {
      console.error('Image generation failed:', error);
      return this.generateFallbackImages();
    }
  }

  // Extract and understand images from website ingestion data
  async extractAndUnderstandImages() {
    const { images, ui_layout, source_notes } = this.brandData;
    const extractedImages = {};

    if (images && images.length > 0) {
      console.log(`Found ${images.length} images from website ingestion`);
      
      // Analyze each image to understand its content and purpose
      for (let i = 0; i < images.length; i++) {
        const imagePath = images[i];
        const imageAnalysis = await this.analyzeImageWithGPT(imagePath, i);
        
        if (imageAnalysis) {
          // Categorize the image based on GPT analysis
          const category = this.categorizeImage(imageAnalysis);
          if (!extractedImages[category]) {
            extractedImages[category] = [];
          }
          extractedImages[category].push({
            path: imagePath,
            analysis: imageAnalysis,
            category: category
          });
        }
      }
    }

    return extractedImages;
  }

  // Use GPT to analyze and understand an image
  async analyzeImageWithGPT(imagePath, index) {
    try {
      // For now, we'll use a mock analysis since we don't have actual image files
      // In production, this would make a GPT Vision API call
      
      const mockAnalyses = [
        "Professional business website hero image with modern design elements",
        "Product showcase image with clean layout and professional styling",
        "Team or company image showing business professionals",
        "Feature illustration or icon representing business capabilities",
        "Process or workflow diagram showing business operations"
      ];
      
      return mockAnalyses[index % mockAnalyses.length];
      
      // TODO: Implement actual GPT Vision API call
      /*
      if (this.apiKey) {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: 'gpt-4-vision-preview',
            messages: [
              {
                role: 'user',
                content: [
                  {
                    type: 'text',
                    text: 'Analyze this image and describe what it shows, its purpose, and where it would be best used on a business website. Be specific about the content, style, and business context.'
                  },
                  {
                    type: 'image_url',
                    image_url: {
                      url: imagePath
                    }
                  }
                ]
              }
            ],
            max_tokens: 300
          })
        });
        
        const data = await response.json();
        return data.choices[0].message.content;
      }
      */
    } catch (error) {
      console.error(`Failed to analyze image ${imagePath}:`, error);
      return null;
    }
  }

  // Categorize image based on GPT analysis
  categorizeImage(analysis) {
    const lowerAnalysis = analysis.toLowerCase();
    
    if (lowerAnalysis.includes('hero') || lowerAnalysis.includes('main') || lowerAnalysis.includes('banner')) {
      return 'hero';
    } else if (lowerAnalysis.includes('product') || lowerAnalysis.includes('feature') || lowerAnalysis.includes('icon')) {
      return 'features';
    } else if (lowerAnalysis.includes('team') || lowerAnalysis.includes('people') || lowerAnalysis.includes('professional')) {
      return 'testimonials';
    } else if (lowerAnalysis.includes('process') || lowerAnalysis.includes('workflow') || lowerAnalysis.includes('diagram')) {
      return 'process';
    } else {
      return 'general';
    }
  }

  // Generate missing images using GPT
  async generateMissingImages(extractedImages) {
    const { x, y, z } = this.userRequirements;
    const { colors } = this.brandData;
    
    const missingImages = {};
    
    // Generate hero image if missing
    if (!extractedImages.hero || extractedImages.hero.length === 0) {
      missingImages.hero = await this.generateHeroImageWithGPT(x, y, z, colors);
    }
    
    // Generate feature images if missing
    if (!extractedImages.features || extractedImages.features.length < 6) {
      missingImages.features = await this.generateFeatureImagesWithGPT(x, z, colors);
    }
    
    // Generate process images if missing
    if (!extractedImages.process || extractedImages.process.length < 3) {
      missingImages.process = await this.generateProcessImagesWithGPT(x, z, colors);
    }
    
    // Generate testimonial images if missing
    if (!extractedImages.testimonials || extractedImages.testimonials.length < 2) {
      missingImages.testimonials = await this.generateTestimonialImagesWithGPT(x, z, colors);
    }
    
    return missingImages;
  }

  // Generate hero image using GPT
  async generateHeroImageWithGPT(x, y, z, colors) {
    const prompt = `Modern professional business website hero image for ${x || 'AI platform'} that ${y || 'transforms business'}. Clean minimalist style, professional aesthetic, innovative and trustworthy mood.`;
    
    return await this.callGPTImageAPI(prompt, 'hero');
  }

  // Generate feature images using GPT
  async generateFeatureImagesWithGPT(x, z, colors) {
    const { keywords } = this.brandData;
    const relevantKeywords = keywords?.filter(k => 
      !['Menu', 'Search', 'Pages', 'About Us', 'Coming soon', 'Store', 'Channel'].includes(k)
    ).slice(0, 6) || [];
    
    const featureImages = [];
    
    for (const keyword of relevantKeywords) {
      const prompt = `Professional business icon for ${keyword} feature. Modern flat design, clean lines, simple and recognizable.`;
      
      const image = await this.callGPTImageAPI(prompt, `feature_${keyword}`);
      featureImages.push(image);
    }
    
    return featureImages;
  }

  // Generate process images using GPT
  async generateProcessImagesWithGPT(x, z, colors) {
    const processSteps = [
      {
        step: 1,
        title: "Discovery",
        description: `Analysis of ${x?.toLowerCase() || 'business needs'} for ${z}`
      },
      {
        step: 2,
        title: "Implementation",
        description: `Deployment of ${x?.toLowerCase() || 'business solution'}`
      },
      {
        step: 3,
        title: "Optimization",
        description: `Continuous improvement of ${x?.toLowerCase() || 'business process'}`
      }
    ];
    
    const processImages = [];
    
    for (const step of processSteps) {
      const prompt = `Professional business illustration for ${step.title} step. Modern clean design, represents business process workflow.`;
      
      const image = await this.callGPTImageAPI(prompt, `process_${step.step}`);
      processImages.push(image);
    }
    
    return processImages;
  }

  // Generate testimonial images using GPT
  async generateTestimonialImagesWithGPT(x, z, colors) {
    const prompt = `Professional business portrait for testimonial. Modern professional person, trustworthy and approachable mood.`;
    
    const testimonialImages = [];
    
    // Generate 2 different testimonial portraits
    for (let i = 0; i < 2; i++) {
      const image = await this.callGPTImageAPI(prompt, `testimonial_${i + 1}`);
      testimonialImages.push(image);
    }
    
    return testimonialImages;
  }

  // Make actual GPT API call for image generation
  async callGPTImageAPI(prompt, imageType) {
    try {
      if (this.apiKey) {
        console.log(`Generating ${imageType} image with GPT...`);
        
        // Make actual API call to DALL-E
        const response = await fetch('https://api.openai.com/v1/images/generations', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            prompt: prompt,
            n: 1,
            size: '1024x1024'
          })
        });
        
        if (!response.ok) {
          const errorData = await response.text();
          console.error(`GPT API error ${response.status}: ${errorData}`);
          throw new Error(`GPT API error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        const imageUrl = data.data[0].url;
        
        console.log(`✅ Generated ${imageType} image successfully`);
        return imageUrl;
      } else {
        // Fallback to high-quality Unsplash images when no API key
        return this.getFallbackImage(imageType);
      }
    } catch (error) {
      console.error(`Failed to generate ${imageType} image:`, error);
      return this.getFallbackImage(imageType);
    }
  }

  // Get fallback images when GPT generation fails
  getFallbackImage(imageType) {
    const fallbackImages = {
      hero: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=400&fit=crop&crop=center',
      features: [
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
    
    if (imageType === 'features') {
      return fallbackImages.features;
    } else if (imageType === 'process') {
      return fallbackImages.process;
    } else if (imageType === 'testimonials') {
      return fallbackImages.testimonials;
    } else {
      return fallbackImages.hero;
    }
  }

  // Generate fallback images if everything fails
  generateFallbackImages() {
    return {
      hero: this.getFallbackImage('hero'),
      features: this.getFallbackImage('features'),
      process: this.getFallbackImage('process'),
      testimonials: this.getFallbackImage('testimonials')
    };
  }
}

export default GPTImageGenerator;

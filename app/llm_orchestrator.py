"""
LLM Orchestrator for Serial AI Workflows
Handles content generation, image creation, and dynamic template generation
"""

import json
import time
from typing import Dict, List, Any, Optional
from .llm import get_llm_provider
from .imgfm import generate_hero_image
import os
import base64

class LLMOrchestrator:
    """Orchestrates serial LLM calls for comprehensive content generation"""
    
    def __init__(self):
        self.llm = get_llm_provider()
        self.workflow_history = []
        
    def log_workflow_step(self, step: str, input_data: Any, output_data: Any, duration: float):
        """Log each workflow step for debugging and optimization"""
        self.workflow_history.append({
            'step': step,
            'input': input_data,
            'output': output_data,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def generate_content_strategy(self, brand: Dict, channel: str, x: str, y: str, z: str, cta: str) -> Dict:
        """Generate content strategy using LLM analysis"""
        start_time = time.time()
        
        system_prompt = f"""
        You are a content strategist for {brand.get('name', 'a brand')}. 
        
        Generate a comprehensive content strategy that includes:
        1. Content positioning and angle
        2. Key messaging pillars
        3. Content structure recommendations
        4. Tone and voice guidelines
        5. Visual content suggestions
        
        Return as JSON with keys: positioning, messaging_pillars, structure, tone_guidelines, visual_suggestions
        """
        
        user_prompt = f"""
        Brand Context:
        - Name: {brand.get('name')}
        - Tagline: {brand.get('tagline')}
        - Colors: {brand.get('colors', {}).get('primary')}, {brand.get('colors', {}).get('secondary')}
        - Tone: {brand.get('tone')}
        - Keywords: {', '.join(brand.get('keywords', [])[:5])}
        
        Content Brief:
        - What we're building: {x}
        - Why it matters: {y}
        - Target audience: {z}
        - Call to action: {cta}
        - Channel: {channel}
        """
        
        try:
            strategy = self.llm.generate_json(system_prompt, user_prompt)
            
            self.log_workflow_step(
                'content_strategy', 
                {'brand': brand.get('name'), 'channel': channel, 'brief': {x, y, z, cta}},
                strategy,
                time.time() - start_time
            )
            
            return strategy
        except Exception as e:
            print(f"⚠️ Content strategy generation failed: {e}")
            return self._get_fallback_strategy(brand, channel, x, y, z, cta)
    
    def generate_content_outline(self, strategy: Dict, brand: Dict, channel: str) -> Dict:
        """Generate detailed content outline based on strategy"""
        start_time = time.time()
        
        system_prompt = f"""
        Based on a content strategy, create a detailed content outline for {channel}.
        
        Generate a content outline with:
        1. Compelling headline (max 60 chars)
        2. Engaging subheadline (max 120 chars)
        3. 4-6 content sections with titles and bullet points
        4. Strong call-to-action
        5. Content flow that matches {channel} best practices
        
        Return as JSON with keys: headline, subheadline, sections (array of {{title, bullets, description}}), cta
        """
        
        user_prompt = f"""
        Strategy: {json.dumps(strategy, indent=2)}
        
        Brand: {brand.get('name')} - {brand.get('tagline')}
        """
        
        try:
            outline = self.llm.generate_json(system_prompt, user_prompt)
            
            self.log_workflow_step(
                'content_outline',
                {'strategy': strategy, 'channel': channel},
                outline,
                time.time() - start_time
            )
            
            return outline
        except Exception as e:
            print(f"⚠️ Content outline generation failed: {e}")
            return self._get_fallback_outline(brand, channel)
    
    def generate_template_code(self, strategy: Dict, outline: Dict, brand: Dict, channel: str) -> str:
        """Generate dynamic J2 template code using LLM with enhanced complexity and visual appeal"""
        start_time = time.time()
        
        # Get channel-specific requirements
        channel_requirements = self._get_channel_requirements(channel)
        
        # Create a more sophisticated prompt for complex, visually appealing templates
        system_prompt = f"""
        You are an expert Jinja2 template developer and UI/UX designer. Create a sophisticated, production-ready HTML template for {channel}.
        
        CRITICAL REQUIREMENTS:
        1. Use the actual content data provided, NOT placeholder text
        2. Create a MODERN, VISUALLY APPEALING design with:
           - Advanced CSS Grid/Flexbox layouts
           - Smooth animations and transitions
           - Professional typography hierarchy
           - Card-based component design
           - Responsive breakpoints
           - Modern spacing and shadows
           - Interactive hover effects
        3. Implement COMPLEX STRUCTURE:
           - Multiple layout sections with different styles
           - Hero section with visual impact
           - Feature grids with varying layouts
           - Testimonial/quote sections
           - Call-to-action with visual emphasis
           - Footer with additional information
        4. Use ADVANCED CSS FEATURES:
           - CSS custom properties (variables)
           - Modern CSS selectors
           - Flexbox and Grid layouts
           - Transform and transition effects
           - Box shadows and gradients
           - Responsive design patterns
        5. Ensure BRAND INTEGRATION:
           - Dynamic color schemes
           - Typography that matches brand
           - Consistent visual language
        6. Follow {channel} format requirements
        7. Use proper Jinja2 syntax for all dynamic content
        """
        
        user_prompt = f"""
        Requirements:
        {channel_requirements}
        
        Brand Data:
        - Colors: {brand.get('colors', {})}
        - Fonts: {brand.get('fonts_detected', [])}
        - Name: {brand.get('name')}
        - Tone: {brand.get('tone', 'professional')}
        
        Content Structure (USE THIS REAL CONTENT):
        - Headline: {outline.get('headline')}
        - Subheadline: {outline.get('subheadline')}
        - CTA: {outline.get('cta')}
        - Sections: {len(outline.get('sections', []))}
        
        Section Details:
        {json.dumps(outline.get('sections', []), indent=2)}
        
        Design Requirements:
        - Create a hero section with large, impactful typography
        - Use CSS Grid for feature sections with varying column layouts
        - Implement card-based design for content sections
        - Add subtle animations (hover effects, transitions)
        - Use modern CSS features (custom properties, flexbox, grid)
        - Ensure mobile-first responsive design
        - Create visual hierarchy with typography and spacing
        
        Example of sophisticated section structure:
        {{% for section in sections %}}
        <div class="content-card content-card--{{{{ loop.index % 3 }}}}">
            <div class="card-header">
                <h2 class="card-title">{{{{ section.title }}}}</h2>
                <div class="card-icon">{{{{ loop.index }}}}</div>
            </div>
            <div class="card-body">
                <p class="card-description">{{{{ section.description }}}}</p>
                {{% if section.bullets %}}
                <ul class="feature-list">
                    {{% for bullet in section.bullets %}}
                    <li class="feature-item">{{{{ bullet }}}}</li>
                    {{% endfor %}}
                </ul>
                {{% endif %}}
            </div>
        </div>
        {{% endfor %}}
        
        DO NOT use placeholder text. Use the real content from the sections array.
        Create a template that looks professional and modern, suitable for enterprise use.
        """
        
        try:
            # For template generation, we need raw text, not JSON
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Use the LLM client directly for raw text generation
            if hasattr(self.llm, 'client'):
                # OpenAI
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": combined_prompt}],
                    temperature=0.2,
                    max_tokens=3000
                )
                template_code = response.choices[0].message.content
            else:
                # Fallback to JSON method and extract text
                template_code = self.llm.generate_json(system_prompt, user_prompt)
                if isinstance(template_code, dict):
                    template_code = template_code.get('template', '')
                else:
                    template_code = str(template_code)
            
            # Clean up the response
            template_code = template_code.strip()
            if template_code.startswith('```html'):
                template_code = template_code[7:]
            if template_code.endswith('```'):
                template_code = template_code[:-3]
            
            self.log_workflow_step(
                'template_generation',
                {'channel': channel, 'sections': len(outline.get('sections', []))},
                {'template_length': len(template_code)},
                time.time() - start_time
            )
            
            return template_code
        except Exception as e:
            print(f"⚠️ Enhanced template generation failed: {e}")
            return self._get_fallback_template(channel)
    
    def generate_hero_image_prompt(self, strategy: Dict, outline: Dict, brand: Dict, channel: str) -> str:
        """Generate optimized image prompt for hero image generation using enhanced LLM approach"""
        start_time = time.time()
        
        # First LLM call: Generate a creative, thematic concept
        concept_prompt = f"""
        You are a creative director specializing in visual concepts for {channel} content.
        
        Brand Context:
        - Name: {brand.get('name')}
        - Industry: {brand.get('tagline', '')}
        - Tone: {brand.get('tone', 'professional')}
        - Primary Color: {brand.get('colors', {}).get('primary', '#000000')}
        - Secondary Color: {brand.get('colors', {}).get('secondary', '#666666')}
        
        Content Focus:
        - Headline: {outline.get('headline')}
        - Key Message: {strategy.get('positioning', '')}
        
        Create a VISUAL CONCEPT (not a description) that:
        1. Captures the essence of {channel} format
        2. Represents the brand's AI/tech focus
        3. Is visually striking and memorable
        4. Avoids any text, words, or readable content
        5. Uses abstract, symbolic, or metaphorical imagery
        6. Works well with the brand colors
        
        Return ONLY the visual concept in 1-2 sentences, no explanations.
        """
        
        try:
            # Generate the visual concept
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": concept_prompt}],
                    temperature=0.8,
                    max_tokens=100
                )
                visual_concept = response.choices[0].message.content.strip()
            else:
                visual_concept = "Futuristic AI technology visualization with neural networks and data flows"
            
            # Second LLM call: Convert concept to image generation prompt
            image_prompt = f"""
            You are an expert at creating image generation prompts for AI art tools.
            
            Visual Concept: {visual_concept}
            Channel: {channel}
            Brand Colors: {brand.get('colors', {}).get('primary')}, {brand.get('colors', {}).get('secondary')}
            
            Create a detailed image generation prompt that:
            1. Brings the visual concept to life
            2. Specifies artistic style (modern, minimalist, tech-focused)
            3. Defines composition and perspective
            4. Ensures NO text, words, or readable content
            5. Uses the brand colors as primary palette
            6. Creates a professional, high-quality appearance
            7. Is optimized for AI image generation tools
            
            Return ONLY the image generation prompt, no explanations.
            """
            
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": image_prompt}],
                    temperature=0.3,
                    max_tokens=200
                )
                final_prompt = response.choices[0].message.content.strip()
            else:
                final_prompt = f"Create {visual_concept} in modern minimalist style, using colors {brand.get('colors', {}).get('primary')} and {brand.get('colors', {}).get('secondary')}, professional composition, no text"
            
            self.log_workflow_step(
                'image_prompt_generation',
                {'channel': channel, 'concept': visual_concept},
                {'final_prompt': final_prompt},
                time.time() - start_time
            )
            
            return final_prompt
            
        except Exception as e:
            print(f"⚠️ Enhanced image prompt generation failed: {e}")
            # Fallback to basic prompt
            return f"Create a modern, professional hero image for {brand.get('name')} in {channel} format, using colors {brand.get('colors', {}).get('primary')} and {brand.get('colors', {}).get('secondary')}, no text, tech-focused aesthetic"
    
    def generate_hero_image(self, image_prompt: str, brand: Dict, output_path: str) -> Optional[str]:
        """Generate hero image using the image generation model"""
        start_time = time.time()
        
        try:
            # Truncate long image prompts to avoid filename issues
            if len(image_prompt) > 100:
                image_prompt = image_prompt[:100] + "..."
            
            # Use existing image generation function with correct arguments
            brand_keywords = brand.get('keywords', [])
            palette_hints = [brand.get('colors', {}).get('primary', '#000000')]
            
            image_path = generate_hero_image(image_prompt, output_path, brand_keywords, palette_hints)
            
            if image_path and os.path.exists(image_path):
                self.log_workflow_step(
                    'hero_image_generation',
                    {'prompt': image_prompt, 'output_path': output_path},
                    {'image_path': image_path, 'file_size': os.path.getsize(image_path)},
                    time.time() - start_time
                )
                return image_path
            else:
                print("⚠️ Hero image generation failed")
                return None
                
        except Exception as e:
            print(f"⚠️ Hero image generation error: {e}")
            return None
    
    def execute_full_workflow(self, brand: Dict, channel: str, x: str, y: str, z: str, cta: str, output_dir: str) -> Dict:
        """Execute the complete LLM orchestration workflow"""
        print(f"🚀 Starting LLM orchestration workflow for {channel}...")
        
        workflow_start = time.time()
        
        # Step 1: Generate content strategy
        print("📋 Step 1: Generating content strategy...")
        strategy = self.generate_content_strategy(brand, channel, x, y, z, cta)
        
        # Step 2: Generate content outline
        print("📝 Step 2: Generating content outline...")
        outline = self.generate_content_outline(strategy, brand, channel)
        
        # Step 3: Generate dynamic template
        print("🎨 Step 3: Generating dynamic template...")
        template_code = self.generate_template_code(strategy, outline, brand, channel)
        
        # Step 4: Generate hero image prompt
        print("🖼️ Step 4: Generating hero image prompt...")
        image_prompt = self.generate_hero_image_prompt(strategy, outline, brand, channel)
        
        # Step 5: Generate hero image
        print("🎨 Step 5: Generating hero image...")
        hero_image_path = None
        if channel != 'linkedin':  # LinkedIn doesn't need hero images
            hero_image_path = self.generate_hero_image(
                image_prompt, 
                brand, 
                os.path.join(output_dir, f"hero_{channel}.png")
            )
        
        # Step 6: Render final content
        print("🔨 Step 6: Rendering final content...")
        final_html = self._render_dynamic_template(template_code, brand, outline, hero_image_path)
        
        workflow_duration = time.time() - workflow_start
        
        # Compile results
        results = {
            'strategy': strategy,
            'outline': outline,
            'template_code': template_code,
            'image_prompt': image_prompt,
            'hero_image_path': hero_image_path,
            'final_html': final_html,
            'workflow_duration': workflow_duration,
            'workflow_history': self.workflow_history
        }
        
        print(f"✅ LLM orchestration workflow completed in {workflow_duration:.1f}s")
        return results
    
    def _render_dynamic_template(self, template_code: str, brand: Dict, outline: Dict, hero_image_path: Optional[str]) -> str:
        """Render the dynamic template with actual data"""
        try:
            # Create a temporary Jinja2 environment
            from jinja2 import Environment, Template
            
            # Create template from code
            template = Template(template_code)
            
            # Prepare context with the variable names the AI template expects
            # Handle different variable naming patterns that AI generates
            context = {
                # Brand info
                'brand_name': brand.get('name', 'Brand'),
                'brand': brand,
                
                # Fonts - handle both patterns
                'brand_fonts': brand.get('fonts_detected', ['Inter', 'Arial', 'sans-serif']),
                'fonts': brand.get('fonts_detected', ['Inter', 'Arial', 'sans-serif']),
                
                # Colors - handle both patterns
                'brand_colors': {
                    'primary': brand.get('colors', {}).get('primary', '#000000'),
                    'secondary': brand.get('colors', {}).get('secondary', '#666666'),
                    'text': '#000000',
                    'bg': '#ffffff',
                    'muted': brand.get('colors', {}).get('muted', '#f0f0f0'),
                    'accent': brand.get('colors', {}).get('accent', '#0099ff')
                },
                'colors': {
                    'primary': brand.get('colors', {}).get('primary', '#000000'),
                    'secondary': brand.get('colors', {}).get('secondary', '#666666'),
                    'text': '#000000',
                    'bg': '#ffffff',
                    'muted': brand.get('colors', {}).get('muted', '#f0f0f0'),
                    'accent': brand.get('colors', {}).get('accent', '#0099ff')
                },
                
                # Content
                'headline': outline.get('headline', 'Welcome'),
                'subheadline': outline.get('subheadline', 'Content coming soon'),
                'cta': outline.get('cta', 'Learn More'),
                'sections': outline.get('sections', []),
                'hero_image_path': hero_image_path,
                'title': outline.get('headline', ''),
                'subtitle': outline.get('subheadline', ''),
                'outline': outline
            }
            
            # Render template
            html = template.render(**context)
            return html
            
        except Exception as e:
            print(f"⚠️ Dynamic template rendering failed: {e}")
            return f"<html><body><h1>Template rendering error: {e}</h1></body></html>"
    
    def _get_channel_requirements(self, channel: str) -> str:
        """Get channel-specific template requirements"""
        requirements = {
            'onepager': """
            - 16:9 aspect ratio, desktop-first design
            - Hero section with headline and CTA
            - Feature sections with cards or grids
            - Professional, business-focused layout
            - Responsive design for mobile
            """,
            'story': """
            - 9:16 aspect ratio (1080x1920px)
            - Vertical scrolling layout
            - Large, readable text
            - Visual hierarchy for mobile viewing
            - Engaging, social media optimized
            """,
            'linkedin': """
            - Horizontal layout, max 800px width
            - Professional, business presentation
            - Clean typography and spacing
            - Content-focused, minimal distractions
            - LinkedIn post format
            """
        }
        return requirements.get(channel, requirements['onepager'])
    
    def _get_fallback_strategy(self, brand: Dict, channel: str, x: str, y: str, z: str, cta: str) -> Dict:
        """Fallback content strategy if LLM fails"""
        return {
            'positioning': f"Professional {channel} content for {brand.get('name', 'brand')}",
            'messaging_pillars': [x, y, z],
            'structure': 'hero + features + cta',
            'tone_guidelines': brand.get('tone', 'professional'),
            'visual_suggestions': 'Clean, modern design with brand colors'
        }
    
    def _get_fallback_outline(self, brand: Dict, channel: str) -> Dict:
        """Fallback content outline if LLM fails"""
        return {
            'headline': f"Welcome to {brand.get('name', 'Our Platform')}",
            'subheadline': f"Discover how we can help you achieve your goals",
            'sections': [
                {'title': 'Get Started', 'bullets': ['Simple setup', 'Quick results', 'Expert support']}
            ],
            'cta': 'Learn More'
        }
    
    def _get_fallback_template(self, channel: str) -> str:
        """Fallback template if LLM fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>{{ title or 'Content' }}</title></head>
        <body>
            <h1>{{ outline.headline or 'Welcome' }}</h1>
            <p>{{ outline.subheadline or 'Content coming soon' }}</p>
            <a href="#">{{ outline.cta or 'Learn More' }}</a>
        </body>
        </html>
        """

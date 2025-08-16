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
        """Generate dynamic J2 template code using LLM"""
        start_time = time.time()
        
        # Get channel-specific requirements
        channel_requirements = self._get_channel_requirements(channel)
        
        # Create a more specific prompt with actual content examples
        system_prompt = f"""
        You are a Jinja2 template developer. Create a complete HTML template for {channel}.
        
        CRITICAL: Use the actual content data provided, NOT placeholder text like "Feature 1", "Description of feature 1".
        
        Generate a complete, production-ready Jinja2 template that:
        1. Uses the brand colors and fonts dynamically with Jinja2 variables
        2. Implements responsive design
        3. Follows modern CSS practices
        4. Includes proper Jinja2 syntax for dynamic content
        5. Matches the {channel} format requirements
        6. Uses the actual content from the outline (headline, subheadline, sections, cta)
        7. Iterates through sections to display real content, not placeholders
        """
        
        user_prompt = f"""
        Requirements:
        {channel_requirements}
        
        Brand Data:
        - Colors: {brand.get('colors', {})}
        - Fonts: {brand.get('fonts_detected', [])}
        - Name: {brand.get('name')}
        
        Content Structure (USE THIS REAL CONTENT):
        - Headline: {outline.get('headline')}
        - Subheadline: {outline.get('subheadline')}
        - CTA: {outline.get('cta')}
        - Sections: {len(outline.get('sections', []))}
        
        Section Details:
        {json.dumps(outline.get('sections', []), indent=2)}
        
        Example of how to use sections:
        {{% for section in sections %}}
        <div class="feature">
            <h2>{{{{ section.title }}}}</h2>
            <p>{{{{ section.description }}}}</p>
            {{% if section.bullets %}}
            <ul>
                {{% for bullet in section.bullets %}}
                <li>{{{{ bullet }}}}</li>
                {{% endfor %}}
            </ul>
            {{% endif %}}
        </div>
        {{% endfor %}}
        
        DO NOT use placeholder text like "Feature 1", "Description of feature 1". Use the real content from the sections array.
        """
        
        try:
            # For template generation, we need raw text, not JSON
            # So we'll use a different approach
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Use the LLM client directly for raw text generation
            if hasattr(self.llm, 'client'):
                # OpenAI
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": combined_prompt}],
                    temperature=0.1,
                    max_tokens=2000
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
            print(f"⚠️ Template generation failed: {e}")
            return self._get_fallback_template(channel)
    
    def generate_hero_image_prompt(self, strategy: Dict, outline: Dict, brand: Dict, channel: str) -> str:
        """Generate optimized image prompt for hero image generation"""
        start_time = time.time()
        
        system_prompt = f"""
        Create an image generation prompt for a hero image that matches this content.
        
        Generate a detailed, specific prompt for an AI image generator that will create:
        1. A hero image appropriate for {channel}
        2. Visual style matching the brand tone: {brand.get('tone')}
        3. Colors that complement: {brand.get('colors', {}).get('primary')}, {brand.get('colors', {}).get('secondary')}
        4. Professional, high-quality appearance
        
        Return ONLY the image prompt, no explanations or additional text.
        """
        
        user_prompt = f"""
        Brand: {brand.get('name')} - {brand.get('tagline')}
        Channel: {channel}
        Headline: {outline.get('headline')}
        Content Angle: {strategy.get('positioning', '')}
        """
        
        try:
            # For image prompts, we need raw text
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            if hasattr(self.llm, 'client'):
                # OpenAI
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": combined_prompt}],
                    temperature=0.1,
                    max_tokens=300
                )
                image_prompt = response.choices[0].message.content
            else:
                # Fallback
                image_prompt = f"professional {channel} hero image for {brand.get('name', 'brand')}"
            
            self.log_workflow_step(
                'image_prompt_generation',
                {'channel': channel, 'headline': outline.get('headline')},
                {'prompt_length': len(image_prompt)},
                time.time() - start_time
            )
            
            return image_prompt.strip()
        except Exception as e:
            print(f"⚠️ Image prompt generation failed: {e}")
            return f"professional {channel} hero image for {brand.get('name', 'brand')}"
    
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

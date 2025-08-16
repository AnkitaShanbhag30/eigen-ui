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
        """Generate detailed content outline using enhanced LLM approach with multiple calls"""
        start_time = time.time()
        
        # First LLM call: Generate audience-specific messaging
        audience_prompt = f"""
        You are a content strategist specializing in {channel} content for {brand.get('name')}.
        
        Brand Context:
        - Industry: {brand.get('tagline', '')}
        - Tone: {brand.get('tone', 'professional')}
        - Target: {brand.get('keywords', [])}
        
        Strategy: {strategy.get('positioning', '')}
        
        Create ENGAGING, AUDIENCE-SPECIFIC messaging that:
        1. Speaks directly to {brand.get('keywords', ['businesses'])[0]} 
        2. Uses compelling, action-oriented language
        3. Addresses specific pain points and desires
        4. Creates emotional connection and urgency
        5. Is tailored for {channel} format
        
        Return ONLY the messaging framework, no explanations.
        """
        
        try:
            # Generate audience-specific messaging
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": audience_prompt}],
                    temperature=0.8,
                    max_tokens=200
                )
                audience_messaging = response.choices[0].message.content.strip()
            else:
                audience_messaging = f"Transform your {brand.get('keywords', ['business'])[0]} with AI-powered solutions"
            
            # Second LLM call: Generate compelling headline and subheadline
            headline_prompt = f"""
            You are a copywriter specializing in conversion-focused headlines.
            
            Brand: {brand.get('name')}
            Channel: {channel}
            Audience: {brand.get('keywords', ['businesses'])[0]}
            Messaging: {audience_messaging}
            
            Create a COMPELLING, CONVERSION-FOCUSED headline and subheadline that:
            1. Grabs attention immediately
            2. Addresses the audience's biggest pain point
            3. Promises a clear, specific benefit
            4. Uses power words and emotional triggers
            5. Is optimized for {channel} format
            6. Avoids generic, boring language
            
            Return ONLY: "Headline: [headline] | Subheadline: [subheadline]"
            """
            
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": headline_prompt}],
                    temperature=0.7,
                    max_tokens=150
                )
                headline_result = response.choices[0].message.content.strip()
                # Parse headline and subheadline
                if "Headline:" in headline_result and "Subheadline:" in headline_result:
                    headline = headline_result.split("Headline:")[1].split("|")[0].strip()
                    subheadline = headline_result.split("Subheadline:")[1].strip()
                else:
                    headline = f"Transform Your {brand.get('keywords', ['Business'])[0]} with {brand.get('name')}"
                    subheadline = audience_messaging
            else:
                headline = f"Transform Your {brand.get('keywords', ['Business'])[0]} with {brand.get('name')}"
                subheadline = audience_messaging
            
            # Third LLM call: Generate engaging, non-repetitive sections
            sections_prompt = f"""
            You are a content strategist creating engaging {channel} content.
            
            Brand: {brand.get('name')}
            Headline: {headline}
            Subheadline: {subheadline}
            Channel: {channel}
            
            Create 4-5 ENGAGING, NON-REPETITIVE content sections that:
            1. Each has a unique angle and purpose
            2. Builds a compelling narrative arc
            3. Uses specific, actionable language
            4. Addresses different aspects of the audience's journey
            5. Includes concrete examples and benefits
            6. Is tailored for {channel} format
            7. Avoids generic, repetitive language
            
            Each section should have:
            - A compelling title (not generic like "Features" or "Benefits")
            - 2-3 specific, actionable bullet points
            - A brief description that creates interest
            
            Return ONLY the sections in this format:
            Section 1: [Title] | [Description] | [Bullet 1] | [Bullet 2] | [Bullet 3]
            Section 2: [Title] | [Description] | [Bullet 1] | [Bullet 2] | [Bullet 3]
            """
            
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": sections_prompt}],
                    temperature=0.8,
                    max_tokens=400
                )
                sections_result = response.choices[0].message.content.strip()
                
                # Parse sections
                sections = []
                for line in sections_result.split('\n'):
                    if 'Section' in line and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            section = {
                                'title': parts[0].split(':')[1].strip(),
                                'description': parts[1].strip(),
                                'bullets': [parts[2].strip(), parts[3].strip(), parts[4].strip()]
                            }
                            sections.append(section)
                
                if not sections:
                    # Fallback sections
                    sections = [
                        {
                            'title': 'The AI Revolution in Your Industry',
                            'description': 'Discover how cutting-edge AI technology is transforming the way businesses operate and succeed.',
                            'bullets': [
                                'Real-time personalization that adapts to customer behavior',
                                'Predictive analytics that anticipate market trends',
                                'Automated optimization that scales with your business'
                            ]
                        },
                        {
                            'title': 'Proven Results That Speak for Themselves',
                            'description': 'Join thousands of businesses already experiencing unprecedented growth and success.',
                            'bullets': [
                                'Average 40% increase in conversion rates',
                                '3x improvement in customer engagement',
                                'ROI achieved within 30 days'
                            ]
                        }
                    ]
            else:
                # Fallback sections
                sections = [
                    {
                        'title': 'The AI Revolution in Your Industry',
                        'description': 'Discover how cutting-edge AI technology is transforming the way businesses operate and succeed.',
                        'bullets': [
                            'Real-time personalization that adapts to customer behavior',
                            'Predictive analytics that anticipate market trends',
                            'Automated optimization that scales with your business'
                        ]
                    }
                ]
            
            # Fourth LLM call: Generate compelling CTA
            cta_prompt = f"""
            You are a conversion copywriter specializing in compelling calls-to-action.
            
            Brand: {brand.get('name')}
            Channel: {channel}
            Audience: {brand.get('keywords', ['businesses'])[0]}
            
            Create a COMPELLING, CONVERSION-FOCUSED CTA that:
            1. Creates urgency and excitement
            2. Offers clear, specific value
            3. Uses action-oriented language
            4. Addresses the audience's primary desire
            5. Is optimized for {channel} format
            6. Avoids generic language like "Learn More" or "Get Started"
            
            Return ONLY the CTA text, no explanations.
            """
            
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": cta_prompt}],
                    temperature=0.7,
                    max_tokens=50
                )
                cta = response.choices[0].message.content.strip()
            else:
                cta = f"Transform Your {brand.get('keywords', ['Business'])[0]} Today"
            
            outline = {
                'headline': headline,
                'subheadline': subheadline,
                'sections': sections,
                'cta': cta
            }
            
            self.log_workflow_step(
                'content_outline',
                {'strategy': strategy, 'channel': channel},
                {'outline': outline},
                time.time() - start_time
            )
            
            return outline
            
        except Exception as e:
            print(f"⚠️ Enhanced content outline generation failed: {e}")
            # Fallback to basic outline
            return {
                'headline': f"Transform Your {brand.get('keywords', ['Business'])[0]} with {brand.get('name')}",
                'subheadline': f"Discover how {brand.get('name')} can revolutionize your business with AI-powered solutions.",
                'sections': [
                    {
                        'title': 'AI-Powered Innovation',
                        'description': 'Leverage cutting-edge technology to stay ahead of the competition.',
                        'bullets': ['Advanced AI algorithms', 'Real-time optimization', 'Scalable solutions']
                    }
                ],
                'cta': f"Start Your Transformation Today"
            }
    
    def generate_template_code(self, strategy: Dict, outline: Dict, brand: Dict, channel: str) -> str:
        """Generate dynamic J2 template using enhanced LLM approach"""
        start_time = time.time()
        
        # Enhanced prompt for better template generation
        system_prompt = f"""
        You are an expert Jinja2 template developer and UI/UX designer specializing in modern, clean web design.
        
        CRITICAL REQUIREMENTS:
        1. Create a MODERN, CLEAN design inspired by shadcn/ui and modern SaaS websites (Notion, Linear, Vercel style)
        2. Use the EXACT content from the outline - NO placeholder text, NO generic content
        3. Create MODERN COMPONENTS: clean navigation, impactful hero, feature cards with subtle depth, clean statistics grids, testimonial cards, modern contact forms, professional footer
        4. Use MODERN CSS FEATURES: CSS custom properties, subtle box-shadows (0 1px 3px rgba(0,0,0,0.1)), modern border-radius (8px, 12px, 16px), proper spacing using rem units, clean transitions
        5. INCLUDE IMAGE SECTIONS throughout using {{{{ hero_image_path }}}} variable
        6. Use the brand colors and fonts from the brand data
        7. Make it look like premium, modern SaaS websites with plenty of whitespace and subtle shadows
        8. NO placeholder text like "Stat 1", "Testimonial 1 text", etc. - use REAL content from the outline
        """
        
        user_prompt = f"""
        Brand: {brand.get('name')}
        Channel: {channel}
        Colors: {brand.get('colors', {})}
        Fonts: {brand.get('fonts_detected', ['Inter', 'Arial', 'sans-serif'])}
        
        Content Outline:
        - Headline: {outline.get('headline', '')}
        - Subheadline: {outline.get('subheadline', '')}
        - CTA: {outline.get('cta', '')}
        - Sections: {len(outline.get('sections', []))} sections
        
        Section Details:
        {chr(10).join([f"- {section.get('title', '')}: {section.get('description', '')}" for section in outline.get('sections', [])])}
        
        Create a complete HTML template that:
        1. Uses ALL the real content from the outline above
        2. Replaces any placeholder text with actual content
        3. Creates engaging, modern sections for each content piece
        4. Uses the hero_image_path variable for images
        5. Has a professional, modern design aesthetic
        6. Is fully responsive and accessible
        """
        
        try:
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=3000
                )
                template_code = response.choices[0].message.content.strip()
            else:
                template_code = self._get_fallback_template(outline, brand, channel)
            
            # Post-process template to ensure no placeholder text remains
            template_code = self._clean_template_placeholders(template_code, outline, brand)
            
            self.log_workflow_step(
                'template_code',
                {'strategy': strategy, 'outline': outline, 'brand': brand, 'channel': channel},
                {'template_code': template_code},
                time.time() - start_time
            )
            
            return template_code
            
        except Exception as e:
            print(f"⚠️ Template generation failed: {e}")
            return self._get_fallback_template(outline, brand, channel)
    
    def _clean_template_placeholders(self, template_code: str, outline: Dict, brand: Dict) -> str:
        """Clean up any remaining placeholder text in the template"""
        # Replace common placeholders with real content
        replacements = {
            'Stat 1': '40% Increase in Conversions',
            'Stat 2': '3x Customer Engagement',
            'Stat 3': '30-Day ROI',
            'Stat description': 'Proven results from real customers',
            'Testimonial 1 text': f"'{brand.get('name')} transformed our business completely. The AI personalization is incredible!' - Sarah M., CEO",
            'Testimonial 2 text': f"'{brand.get('name')} helped us achieve 3x better customer engagement. Game changer!' - Mike R., Marketing Director",
            'testimonial1_image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjUiIGZpbGw9IiNGM0Y0RjYiLz4KPHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDVMMTQgMTJMMjAgMTNMMTQgMTRMMTAgMjFMMTAgMTRMMTAgNVoiIGZpbGw9IiM2Nzc0OEIiLz4KPC9zdmc+Cjwvc3ZnPgo=',
            'testimonial2_image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjUiIGZpbGw9IiNGM0Y0RjYiLz4KPHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDVMMTQgMTJMMjAgMTNMMTQgMTRMMTAgMjFMMTAgMTRMMTAgNVoiIGZpbGw9IiM2Nzc0OEIiLz4KPC9zdmc+Cjwvc3ZnPgo='
        }
        
        for placeholder, replacement in replacements.items():
            template_code = template_code.replace(placeholder, replacement)
        
        return template_code
    
    def generate_hero_image_prompt(self, strategy: Dict, outline: Dict, brand: Dict, channel: str) -> str:
        """Generate a compelling hero image prompt using a two-step LLM approach"""
        start_time = time.time()
        
        # First LLM call: Generate abstract visual concept
        concept_prompt = f"""
        You are a visual concept artist specializing in brand imagery.
        
        Brand: {brand.get('name')}
        Industry: {brand.get('tagline', '')}
        Channel: {channel}
        Headline: {outline.get('headline', '')}
        
        Create a SINGLE, CLEAR visual concept that:
        1. Is ABSTRACT and SYMBOLIC (no text, words, or readable content)
        2. Represents the brand's core value proposition
        3. Is visually striking and modern
        4. Works well for {channel} format
        5. Can be described in 1-2 sentences
        6. Avoids any text, letters, or readable symbols
        
        Return ONLY the visual concept description, no explanations.
        """
        
        try:
            # Generate visual concept
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": concept_prompt}],
                    temperature=0.9,
                    max_tokens=100
                )
                visual_concept = response.choices[0].message.content.strip()
            else:
                visual_concept = "A futuristic geometric pattern with interconnected nodes and flowing lines"
            
            # Second LLM call: Convert to detailed image generation prompt
            image_prompt = f"""
            You are an expert at creating image generation prompts.
            
            Visual Concept: {visual_concept}
            Brand Colors: {brand.get('colors', {}).get('primary', '#000000')}, {brand.get('colors', {}).get('secondary', '#666666')}
            Style: Modern, clean, professional
            
            Create a DETAILED image generation prompt that:
            1. Describes the visual concept clearly
            2. Specifies artistic style and composition
            3. Uses the brand colors
            4. Is optimized for AI image generation
            5. ABSOLUTELY NO TEXT, WORDS, OR READABLE CONTENT
            6. Focuses on shapes, colors, patterns, and composition
            
            Return ONLY the image generation prompt, no explanations.
            """
            
            if hasattr(self.llm, 'client'):
                response = self.llm.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": image_prompt}],
                    temperature=0.3,
                    max_tokens=150
                )
                final_prompt = response.choices[0].message.content.strip()
            else:
                final_prompt = f"Create {visual_concept} using {brand.get('colors', {}).get('primary', '#000000')} and {brand.get('colors', {}).get('secondary', '#666666')} colors, modern geometric style, clean composition, no text"
            
            # Ensure no text-related words in the prompt
            text_indicators = ['text', 'word', 'letter', 'font', 'type', 'writing', 'read', 'message']
            for indicator in text_indicators:
                if indicator in final_prompt.lower():
                    final_prompt = final_prompt.replace(indicator, 'geometric shape')
                    final_prompt = final_prompt.replace(indicator.capitalize(), 'Geometric shape')
            
            self.log_workflow_step(
                'hero_image_prompt',
                {'strategy': strategy, 'outline': outline, 'brand': brand, 'channel': channel},
                {'prompt': final_prompt},
                time.time() - start_time
            )
            
            return final_prompt
            
        except Exception as e:
            print(f"⚠️ Hero image prompt generation failed: {e}")
            # Fallback to clean, text-free prompt
            return f"Create a modern, abstract geometric design using {brand.get('colors', {}).get('primary', '#000000')} and {brand.get('colors', {}).get('secondary', '#666666')} colors, clean composition, no text or readable content"
    
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
        final_html = self._render_dynamic_template(template_code, brand, outline, hero_image_path, output_dir)
        
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
    
    def _render_dynamic_template(self, template_code: str, brand: Dict, outline: Dict, hero_image_path: Optional[str], output_dir: str) -> str:
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
            
            # Fix image paths for proper display
            if hero_image_path and os.path.exists(hero_image_path):
                # Convert to relative path for web display
                context['hero_image_path'] = os.path.relpath(hero_image_path, output_dir)
                # Also provide absolute path as fallback
                context['hero_image_absolute'] = hero_image_path
            else:
                # Use placeholder if no image
                context['hero_image_path'] = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xMDAgMTUwTDIwMCAxMDBMMzAwIDE1MEwyMDAgMjAwTDEwMCAxNTBaIiBmaWxsPSIjRjFGM0Y0Ii8+Cjx0ZXh0IHg9IjIwMCIgeT0iMTgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNjc3NDhCIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiPkltYWdlIFBsYWNlaG9sZGVyPC90ZXh0Pgo8L3N2Zz4K'
                context['hero_image_absolute'] = None
            
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
    
    def _get_fallback_template(self, outline: Dict, brand: Dict, channel: str) -> str:
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

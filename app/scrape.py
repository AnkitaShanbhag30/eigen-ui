import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse
import os
import json
from dataclasses import dataclass
from playwright.sync_api import sync_playwright
import base64

@dataclass
class LayoutElement:
    """Represents a layout element with its properties"""
    tag: str
    classes: List[str]
    id: Optional[str]
    text_content: str
    position: Dict[str, int]  # x, y, width, height
    styles: Dict[str, str]
    children_count: int
    is_visible: bool

@dataclass
class DesignPattern:
    """Represents a design pattern found on the page"""
    type: str  # 'grid', 'card', 'hero', 'navigation', 'footer', 'sidebar'
    elements: List[LayoutElement]
    layout_type: str  # 'horizontal', 'vertical', 'grid', 'flexbox'
    spacing: Dict[str, int]  # margins, padding
    alignment: str  # 'left', 'center', 'right', 'justify'

def fetch_html(url: str, timeout_ms: int = 7000) -> Optional[str]:
    """Fetch HTML content with timeout"""
    try:
        timeout_sec = timeout_ms / 1000
        response = requests.get(url, timeout=timeout_sec)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_meta(html: str, base_url: str) -> Dict[str, str]:
    """Extract meta tags and Open Graph data"""
    soup = BeautifulSoup(html, 'html.parser')
    meta = {}
    
    # Basic meta tags
    title_tag = soup.find('title')
    if title_tag:
        meta['title'] = title_tag.get_text(strip=True)
    
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag:
        meta['description'] = desc_tag.get('content', '').strip()
    
    # Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title:
        meta['og_title'] = og_title.get('content', '').strip()
    
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    if og_desc:
        meta['og_description'] = og_desc.get('content', '').strip()
    
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    if og_image:
        meta['og_image'] = urljoin(base_url, og_image.get('content', ''))
    
    return meta

def find_images(html: str, base_url: str, max_images: int = 3) -> List[Dict[str, str]]:
    """Find candidate images including logos"""
    soup = BeautifulSoup(html, 'html.parser')
    images = []
    
    # Look for logo images first
    logo_candidates = []
    for img in soup.find_all('img'):
        alt = img.get('alt', '').lower()
        src = img.get('src', '')
        if src and ('logo' in alt or 'logo' in src.lower()):
            logo_candidates.append({
                'src': urljoin(base_url, src),
                'alt': alt,
                'is_logo': True
            })
    
    # Add other images
    other_images = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        if src and img not in [c for c in logo_candidates]:
            other_images.append({
                'src': urljoin(base_url, src),
                'alt': alt,
                'is_logo': False
            })
    
    # Prioritize logos, then add others up to max_images
    images.extend(logo_candidates)
    images.extend(other_images[:max_images - len(logo_candidates)])
    
    return images[:max_images]

def find_css_links(html: str, base_url: str) -> List[str]:
    """Find CSS links for font analysis"""
    soup = BeautifulSoup(html, 'html.parser')
    css_links = []
    
    # Link tags
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href:
            css_links.append(urljoin(base_url, href))
    
    # Style tags with @import
    for style in soup.find_all('style'):
        content = style.get_text()
        import_matches = re.findall(r'@import\s+url\(["\']?([^"\']+)["\']?\)', content)
        for match in import_matches:
            css_links.append(urljoin(base_url, match))
    
    return css_links

def visible_text_samples(html: str, max_chars: int = 1500) -> List[str]:
    """Extract visible text samples for tone analysis"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean it
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # Split into sentences and take chunks
    sentences = re.split(r'[.!?]+', text)
    samples = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20 and current_length < max_chars:
            samples.append(sentence)
            current_length += len(sentence)
            if len(samples) >= 3:  # Max 3 samples
                break
    
    return samples

def download_image(url: str, save_path: str) -> bool:
    """Download image to local path"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False 

def extract_social_media(html: str, base_url: str) -> Dict[str, str]:
    """Extract social media links and presence"""
    soup = BeautifulSoup(html, 'html.parser')
    social_media = {}
    
    # Common social media patterns
    social_patterns = {
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com'],
        'instagram': ['instagram.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'github': ['github.com'],
        'discord': ['discord.gg', 'discord.com'],
        'slack': ['slack.com'],
        'telegram': ['t.me', 'telegram.org']
    }
    
    # Find all links
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        for platform, patterns in social_patterns.items():
            if any(pattern in href for pattern in patterns):
                social_media[platform] = link.get('href')
                break
    
    return social_media

def extract_contact_info(html: str, base_url: str) -> Dict[str, str]:
    """Extract contact information from the page"""
    soup = BeautifulSoup(html, 'html.parser')
    contact_info = {}
    
    # Look for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = soup.get_text()
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['emails'] = list(set(emails[:3]))  # Max 3 unique emails
    
    # Look for phone numbers
    phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phones = re.findall(phone_pattern, text)
    if phones:
        contact_info['phones'] = [''.join(phone) for phone in phones[:3]]
    
    # Look for contact forms
    contact_forms = soup.find_all(['form', 'input'], attrs={'type': ['email', 'tel', 'text']})
    if contact_forms:
        contact_info['has_contact_form'] = True
    
    # Look for address information
    address_keywords = ['address', 'street', 'city', 'state', 'zip', 'country']
    for keyword in address_keywords:
        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        if elements:
            contact_info['has_address'] = True
            break
    
    return contact_info

def extract_navigation(html: str, base_url: str) -> List[str]:
    """Extract main navigation items"""
    soup = BeautifulSoup(html, 'html.parser')
    navigation = []
    
    # Look for main navigation elements
    nav_elements = soup.find_all(['nav', 'ul', 'ol'], class_=re.compile(r'nav|menu|header', re.IGNORECASE))
    
    for nav in nav_elements:
        links = nav.find_all('a')
        for link in links:
            text = link.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 50:  # Reasonable nav item length
                navigation.append(text)
    
    # Remove duplicates and return
    return list(dict.fromkeys(navigation))  # Preserves order

def extract_content_structure(html: str) -> Dict[str, int]:
    """Analyze the content structure of the page"""
    soup = BeautifulSoup(html, 'html.parser')
    structure = {}
    
    # Count different content types
    structure['headings'] = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    structure['paragraphs'] = len(soup.find_all('p'))
    structure['lists'] = len(soup.find_all(['ul', 'ol']))
    structure['images'] = len(soup.find_all('img'))
    structure['links'] = len(soup.find_all('a'))
    structure['forms'] = len(soup.find_all('form'))
    structure['tables'] = len(soup.find_all('table'))
    
    # Check for specific content sections
    content_sections = ['article', 'section', 'main', 'aside', 'header', 'footer']
    for section in content_sections:
        count = len(soup.find_all(section))
        if count > 0:
            structure[f'{section}s'] = count
    
    return structure

def extract_business_info(html: str, base_url: str) -> Dict[str, str]:
    """Extract business-related information"""
    soup = BeautifulSoup(html, 'html.parser')
    business_info = {}
    
    # Look for company information
    company_keywords = ['about', 'company', 'team', 'mission', 'vision', 'values', 'story']
    for keyword in company_keywords:
        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        if elements:
            business_info[f'has_{keyword}'] = True
    
    # Look for pricing information
    pricing_keywords = ['pricing', 'plans', 'cost', 'price', 'subscription', 'billing']
    for keyword in pricing_keywords:
        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        if elements:
            business_info['has_pricing'] = True
            break
    
    # Look for product/service information
    product_keywords = ['product', 'service', 'solution', 'feature', 'benefit']
    for keyword in product_keywords:
        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        if elements:
            business_info['has_products'] = True
            break
    
    # Look for testimonials/reviews
    testimonial_keywords = ['testimonial', 'review', 'customer', 'client', 'feedback']
    for keyword in testimonial_keywords:
        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        if elements:
            business_info['has_testimonials'] = True
            break
    
    return business_info

def analyze_color_scheme(html: str, base_url: str) -> Dict[str, Any]:
    """Analyze the color scheme from CSS, inline styles, and CSS variables"""
    soup = BeautifulSoup(html, 'html.parser')
    color_scheme = {
        'primary': None,
        'secondary': None,
        'accents': [],
        'backgrounds': [],
        'text_colors': []
    }
    
    # Enhanced color patterns to catch more color formats
    color_patterns = [
        r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})',  # Hex colors
        r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',  # RGB
        r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)',  # RGBA
        r'hsla?\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%',  # HSL/HSLA
        r'var\(--([^)]+)\)',  # CSS variables
    ]
    
    all_colors = []
    
    # 1. Extract colors from inline styles
    for element in soup.find_all(attrs={'style': True}):
        style = element.get('style', '')
        for pattern in color_patterns:
            matches = re.findall(pattern, style)
            for match in matches:
                if isinstance(match, tuple):
                    # RGB/HSL format
                    if len(match) >= 3:
                        r, g, b = int(match[0]), int(match[1]), int(match[2])
                        hex_color = f"#{r:02x}{g:02x}{b:02x}"
                        all_colors.append(hex_color)
                elif match.startswith('#'):
                    all_colors.append(match)
                elif match.startswith('var'):
                    # Handle CSS variables
                    var_name = match.strip('var(--)')
                    all_colors.append(f"var-{var_name}")
    
    # 2. Extract colors from <style> tags
    for style_tag in soup.find_all('style'):
        css_content = style_tag.get_text()
        for pattern in color_patterns:
            matches = re.findall(pattern, css_content)
            for match in matches:
                if isinstance(match, tuple):
                    # RGB/HSL format
                    if len(match) >= 3:
                        r, g, b = int(match[0]), int(match[1]), int(match[2])
                        hex_color = f"#{r:02x}{g:02x}{b:02x}"
                        all_colors.append(hex_color)
                elif match.startswith('#'):
                    all_colors.append(match)
                elif match.startswith('var'):
                    var_name = match.strip('var(--)')
                    all_colors.append(f"var-{var_name}")
    
    # 3. Extract colors from CSS variables
    css_var_pattern = r'--([^:]+):\s*([^;]+);'
    for style_tag in soup.find_all('style'):
        css_content = style_tag.get_text()
        var_matches = re.findall(css_var_pattern, css_content)
        for var_name, var_value in var_matches:
            # Check if the variable value is a color
            for pattern in color_patterns[:-1]:  # Exclude CSS variable pattern
                if re.search(pattern, var_value):
                    all_colors.append(f"var-{var_name}")
                    break
    
    # 4. Look for common color keywords in class names and IDs
    color_keywords = ['blue', 'red', 'green', 'yellow', 'purple', 'pink', 'orange', 'gray', 'black', 'white']
    for element in soup.find_all(class_=True):
        classes = element.get('class', [])
        for cls in classes:
            cls_lower = cls.lower()
            for keyword in color_keywords:
                if keyword in cls_lower:
                    # Try to extract the actual color value
                    if hasattr(element, 'style') and element.get('style'):
                        style = element.get('style', '')
                        for pattern in color_patterns[:-1]:
                            matches = re.findall(pattern, style)
                            if matches:
                                all_colors.extend(matches)
    
    # 5. Look for colors in data attributes
    for element in soup.find_all(attrs={'data-color': True}):
        color_value = element.get('data-color')
        if color_value and re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color_value):
            all_colors.append(color_value)
    
    # 6. Look for colors in meta tags (theme-color)
    theme_color = soup.find('meta', attrs={'name': 'theme-color'})
    if theme_color and theme_color.get('content'):
        content = theme_color.get('content')
        if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', content):
            all_colors.append(content)
    
    # Clean and deduplicate colors
    clean_colors = []
    for color in all_colors:
        if color.startswith('#'):
            clean_colors.append(color)
        elif color.startswith('var-'):
            clean_colors.append(color)
    
    # Remove duplicates while preserving order
    unique_colors = list(dict.fromkeys(clean_colors))
    
    # Filter out very light/white colors and very dark/black colors
    filtered_colors = []
    for color in unique_colors:
        if color.startswith('#'):
            # Convert hex to RGB for brightness check
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                # Only include colors that aren't too light or too dark
                if 30 < brightness < 225:
                    filtered_colors.append(color)
            except:
                filtered_colors.append(color)
        else:
            filtered_colors.append(color)
    
    color_scheme['accents'] = filtered_colors[:15]  # Limit to 15 colors
    
    # Set primary and secondary if we have enough colors
    if len(filtered_colors) >= 2:
        color_scheme['primary'] = filtered_colors[0]
        color_scheme['secondary'] = filtered_colors[1]
    elif len(filtered_colors) == 1:
        color_scheme['primary'] = filtered_colors[0]
    
    return color_scheme

def detect_typography(html: str, base_url: str) -> Dict[str, Any]:
    """Detect typography information from the page"""
    soup = BeautifulSoup(html, 'html.parser')
    typography = {
        'families': [],
        'weights': [],
        'sizes': []
    }
    
    # Look for font-family in inline styles
    font_pattern = r'font-family:\s*([^;]+)'
    weight_pattern = r'font-weight:\s*([^;]+)'
    size_pattern = r'font-size:\s*([^;]+)'
    
    # Extract from inline styles
    for element in soup.find_all(attrs={'style': True}):
        style = element.get('style', '')
        
        # Extract font families
        families = re.findall(font_pattern, style)
        for family in families:
            # Clean up font family names
            clean_family = family.strip().strip('"\'')
            if clean_family and clean_family not in typography['families']:
                typography['families'].append(clean_family)
        
        # Extract font weights
        weights = re.findall(weight_pattern, style)
        for weight in weights:
            clean_weight = weight.strip()
            if clean_weight and clean_weight not in typography['weights']:
                typography['weights'].append(clean_weight)
        
        # Extract font sizes
        sizes = re.findall(size_pattern, style)
        for size in sizes:
            clean_size = size.strip()
            if clean_size and clean_size not in typography['sizes']:
                typography['sizes'].append(clean_size)
    
    # Look for typography in CSS
    css_text = soup.find_all('style')
    for css in css_text:
        css_content = css.get_text()
        
        families = re.findall(font_pattern, css_content)
        for family in families:
            clean_family = family.strip().strip('"\'')
            if clean_family and clean_family not in typography['families']:
                typography['families'].append(clean_family)
        
        weights = re.findall(weight_pattern, css_content)
        for weight in weights:
            clean_weight = weight.strip()
            if clean_weight and clean_weight not in typography['weights']:
                typography['weights'].append(clean_weight)
        
        sizes = re.findall(size_pattern, css_content)
        for size in sizes:
            clean_size = size.strip()
            if clean_size and clean_size not in typography['sizes']:
                typography['sizes'].append(clean_size)
    
    # Clean up font families - remove CSS artifacts and broken quotes
    clean_families = []
    for family in typography['families']:
        # Remove CSS artifacts
        if 'body{' in family or '--token' in family or 'rgb(' in family:
            continue
        
        # Clean up broken quotes and commas
        clean_family = family.replace('", "', ', ').replace('"}', '').replace('"', '').strip()
        if clean_family and len(clean_family) > 2 and clean_family not in clean_families:
            clean_families.append(clean_family)
    
    # Also look for Google Fonts links
    for link in soup.find_all('link', attrs={'rel': 'stylesheet'}):
        href = link.get('href', '')
        if 'fonts.googleapis.com' in href:
            # Extract font names from Google Fonts URL
            font_match = re.search(r'family=([^&]+)', href)
            if font_match:
                font_names = font_match.group(1).split('|')
                for font_name in font_names:
                    clean_name = font_name.replace('+', ' ').strip()
                    if clean_name and clean_name not in clean_families:
                        clean_families.append(clean_name)
    
    # Limit results and clean up
    typography['families'] = clean_families[:8]  # Increased limit
    typography['weights'] = typography['weights'][:5]
    typography['sizes'] = typography['sizes'][:5]
    
    return typography

def extract_ui_structure(html: str, url: str) -> Dict[str, Any]:
    """Extract comprehensive UI structure and layout patterns"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract layout structure
    layout_data = {
        'page_structure': extract_page_structure(soup),
        'design_patterns': extract_design_patterns(soup),
        'spacing_system': extract_spacing_system(soup),
        'layout_grid': extract_layout_grid(soup),
        'component_patterns': extract_component_patterns(soup),
        'visual_hierarchy': extract_visual_hierarchy(soup),
        'responsive_breakpoints': extract_responsive_breakpoints(soup),
        'interaction_patterns': extract_interaction_patterns(soup),
        'css_structure': extract_css_structure(html, url),
        'screenshot_path': None,
        'layout_analysis': {}
    }
    
    return layout_data

def extract_page_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract the overall page structure and sections"""
    structure = {
        'header': extract_section_structure(soup, ['header', 'nav', '.header', '.nav', '.navigation']),
        'hero': extract_section_structure(soup, ['main', '.hero', '.banner', '.jumbotron']),
        'content': extract_section_structure(soup, ['main', '.content', '.main-content', 'article']),
        'sidebar': extract_section_structure(soup, ['aside', '.sidebar', '.side-content']),
        'footer': extract_section_structure(soup, ['footer', '.footer', '.site-footer']),
        'sections': extract_content_sections(soup)
    }
    
    return structure

def extract_section_structure(soup: BeautifulSoup, selectors: List[str]) -> Optional[Dict[str, Any]]:
    """Extract structure for a specific section"""
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return {
                'tag': element.name,
                'classes': element.get('class', []),
                'id': element.get('id'),
                'text_content': element.get_text(strip=True)[:200],
                'children_count': len(element.find_all()),
                'has_images': bool(element.find_all('img')),
                'has_buttons': bool(element.find_all(['button', 'a'])),
                'layout_type': detect_layout_type(element)
            }
    return None

def extract_content_sections(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract all content sections and their structure"""
    sections = []
    
    # Look for common section patterns
    section_selectors = [
        'section', '.section', '.content-section', '.block',
        '[class*="section"]', '[class*="block"]', '[class*="content"]'
    ]
    
    for selector in section_selectors:
        elements = soup.select(selector)
        for element in elements[:10]:  # Limit to first 10 sections
            section_data = {
                'tag': element.name,
                'classes': element.get('class', []),
                'title': extract_section_title(element),
                'content_type': detect_content_type(element),
                'layout': detect_layout_type(element),
                'elements': extract_element_details(element),
                'spacing': extract_element_spacing(element)
            }
            sections.append(section_data)
    
    return sections

def extract_section_title(element) -> Optional[str]:
    """Extract title from a section element"""
    # Look for headings
    heading = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if heading:
        return heading.get_text(strip=True)
    
    # Look for aria-label or title attributes
    aria_label = element.get('aria-label')
    if aria_label:
        return aria_label
    
    title_attr = element.get('title')
    if title_attr:
        return title_attr
    
    return None

def detect_content_type(element) -> str:
    """Detect the type of content in a section"""
    text = element.get_text().lower()
    
    if any(word in text for word in ['feature', 'benefit', 'advantage']):
        return 'features'
    elif any(word in text for word in ['testimonial', 'review', 'quote']):
        return 'testimonials'
    elif any(word in text for word in ['pricing', 'plan', 'cost']):
        return 'pricing'
    elif any(word in text for word in ['contact', 'email', 'phone']):
        return 'contact'
    elif any(word in text for word in ['about', 'story', 'mission']):
        return 'about'
    elif any(word in text for word in ['cta', 'call', 'action']):
        return 'cta'
    else:
        return 'general'

def detect_layout_type(element) -> str:
    """Detect the layout type of an element"""
    classes = element.get('class', [])
    class_str = ' '.join(classes).lower()
    
    if any('grid' in cls for cls in classes):
        return 'grid'
    elif any('flex' in cls for cls in classes):
        return 'flexbox'
    elif any('block' in cls for cls in classes):
        return 'block'
    else:
        return 'default'

def extract_element_details(element) -> Dict[str, Any]:
    """Extract detailed information about an element"""
    return {
        'tag': element.name,
        'classes': element.get('class', []),
        'id': element.get('id'),
        'text_content': element.get_text(strip=True)[:100],
        'children_count': len(element.find_all()),
        'has_images': bool(element.find_all('img')),
        'has_buttons': bool(element.find_all(['button', 'a']))
    }

def extract_inline_styles(element) -> Dict[str, str]:
    """Extract inline styles from an element"""
    styles = {}
    style_attr = element.get('style', '')
    
    if style_attr:
        # Parse inline styles
        style_pairs = style_attr.split(';')
        for pair in style_pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                styles[key.strip()] = value.strip()
    
    return styles

def extract_element_spacing(element) -> Dict[str, Any]:
    """Extract spacing information for an element"""
    return {
        'margin': element.get('style', ''),
        'padding': element.get('style', ''),
        'gap': element.get('style', '')
    }

def extract_design_patterns(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract common design patterns from the page"""
    patterns = []
    
    # Grid patterns
    grid_elements = soup.find_all(['div', 'section'], class_=re.compile(r'grid|row|col'))
    if grid_elements:
        patterns.append({
            'type': 'grid',
            'elements': [{
                'tag': el.name,
                'classes': el.get('class', []),
                'id': el.get('id'),
                'text_content': el.get_text(strip=True)[:100],
                'position': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'styles': extract_inline_styles(el),
                'children_count': len(el.find_all()),
                'is_visible': True
            } for el in grid_elements[:5]],
            'layout_type': 'grid',
            'spacing': {},
            'alignment': 'left'
        })
    
    # Card patterns
    card_elements = soup.find_all(['div', 'article'], class_=re.compile(r'card|tile|box'))
    if card_elements:
        patterns.append({
            'type': 'card',
            'elements': [{
                'tag': el.name,
                'classes': el.get('class', []),
                'id': el.get('id'),
                'text_content': el.get_text(strip=True)[:100],
                'position': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'styles': extract_inline_styles(el),
                'children_count': len(el.find_all()),
                'is_visible': True
            } for el in card_elements[:5]],
            'layout_type': 'card',
            'spacing': {},
            'alignment': 'left'
        })
    
    # Hero patterns
    hero_elements = soup.find_all(['div', 'section'], class_=re.compile(r'hero|banner|jumbotron'))
    if hero_elements:
        patterns.append({
            'type': 'hero',
            'elements': [{
                'tag': el.name,
                'classes': el.get('class', []),
                'id': el.get('id'),
                'text_content': el.get_text(strip=True)[:100],
                'position': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'styles': extract_inline_styles(el),
                'children_count': len(el.find_all()),
                'is_visible': True
            } for el in hero_elements[:3]],
            'layout_type': 'hero',
            'spacing': {},
            'alignment': 'center'
        })
    
    return patterns

def extract_spacing_system(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract the spacing system used on the page"""
    spacing = {
        'margins': extract_spacing_values(soup, 'margin'),
        'padding': extract_spacing_values(soup, 'padding'),
        'gaps': extract_spacing_values(soup, 'gap'),
        'common_values': find_common_spacing_values(soup)
    }
    
    return spacing

def extract_layout_grid(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract grid layout information"""
    grid_info = {
        'grid_systems': [],
        'column_patterns': [],
        'breakpoints': []
    }
    
    # Look for CSS Grid usage
    grid_elements = soup.find_all(class_=re.compile(r'grid|grid-'))
    if grid_elements:
        grid_info['grid_systems'].append({
            'type': 'css_grid',
            'count': len(grid_elements),
            'examples': [el.get('class', [])[0] for el in grid_elements[:3]]
        })
    
    # Look for Flexbox usage
    flex_elements = soup.find_all(class_=re.compile(r'flex|flexbox'))
    if flex_elements:
        grid_info['grid_systems'].append({
            'type': 'flexbox',
            'count': len(flex_elements),
            'examples': [el.get('class', [])[0] for el in flex_elements[:3]]
        })
    
    return grid_info

def extract_component_patterns(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract common component patterns"""
    components = {
        'buttons': [],
        'forms': [],
        'navigation': [],
        'cards': []
    }
    
    # Button patterns
    buttons = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button'))
    if buttons:
        components['buttons'] = [{
            'type': 'button',
            'count': len(buttons),
            'examples': [el.get('class', [])[0] if el.get('class') else el.name for el in buttons[:3]]
        }]
    
    # Form patterns
    forms = soup.find_all('form')
    if forms:
        components['forms'] = [{
            'type': 'form',
            'count': len(forms),
            'examples': [el.get('class', [])[0] if el.get('class') else 'form' for el in forms[:3]]
        }]
    
    # Navigation patterns
    nav_elements = soup.find_all(['nav', 'ul'], class_=re.compile(r'nav|menu'))
    if nav_elements:
        components['navigation'] = [{
            'type': 'navigation',
            'count': len(nav_elements),
            'examples': [el.get('class', [])[0] if el.get('class') else el.name for el in nav_elements[:3]]
        }]
    
    # Card patterns
    cards = soup.find_all(['div', 'article'], class_=re.compile(r'card|tile|box'))
    if cards:
        components['cards'] = [{
            'type': 'card',
            'count': len(cards),
            'examples': [el.get('class', [])[0] if el.get('class') else el.name for el in cards[:3]]
        }]
    
    return components

def extract_visual_hierarchy(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract visual hierarchy information"""
    hierarchy = {
        'headings': {},
        'text_sizes': [],
        'emphasis': []
    }
    
    # Analyze heading hierarchy
    for i in range(1, 7):
        headings = soup.find_all(f'h{i}')
        if headings:
            hierarchy['headings'][f'h{i}'] = len(headings)
    
    # Look for emphasis patterns
    emphasis_elements = soup.find_all(['strong', 'b', 'em', 'i'])
    if emphasis_elements:
        hierarchy['emphasis'] = [el.name for el in emphasis_elements[:10]]
    
    return hierarchy

def extract_spacing_values(soup: BeautifulSoup, property_name: str) -> List[str]:
    """Extract specific spacing property values"""
    values = set()
    
    # Look in inline styles
    for element in soup.find_all(style=True):
        style = element.get('style', '')
        matches = re.findall(rf'{property_name}:\s*([^;]+)', style)
        values.update(matches)
    
    # Look in CSS classes (common patterns)
    for element in soup.find_all(class_=True):
        classes = element.get('class', [])
        for cls in classes:
            if property_name in cls:
                # Extract numeric values from class names like 'm-4', 'p-6', 'gap-8'
                match = re.search(rf'{property_name[0]}-(\d+)', cls)
                if match:
                    values.add(f"{match.group(1)}px")
    
    return list(values)

def find_common_spacing_values(soup: BeautifulSoup) -> List[str]:
    """Find commonly used spacing values"""
    all_spacing = []
    
    # Common spacing patterns
    spacing_patterns = ['m-', 'p-', 'gap-', 'space-', 'mt-', 'mb-', 'ml-', 'mr-']
    
    for element in soup.find_all(class_=True):
        classes = element.get('class', [])
        for cls in classes:
            for pattern in spacing_patterns:
                if pattern in cls:
                    match = re.search(rf'{pattern}(\d+)', cls)
                    if match:
                        all_spacing.append(int(match.group(1)))
    
    # Count occurrences and return most common
    from collections import Counter
    counter = Counter(all_spacing)
    return [str(val) for val, count in counter.most_common(5)]

def extract_responsive_breakpoints(soup: BeautifulSoup) -> List[str]:
    """Extract responsive breakpoint patterns"""
    breakpoints = []
    
    # Look for common breakpoint patterns in CSS classes
    breakpoint_patterns = ['sm:', 'md:', 'lg:', 'xl:', '2xl:']
    for pattern in breakpoint_patterns:
        elements = soup.find_all(class_=re.compile(pattern))
        if elements:
            breakpoints.append(pattern.rstrip(':'))
    
    # Look for media query patterns
    media_patterns = ['mobile', 'tablet', 'desktop', 'responsive']
    for pattern in media_patterns:
        elements = soup.find_all(class_=re.compile(pattern))
        if elements:
            breakpoints.append(pattern)
    
    return list(set(breakpoints))

def extract_interaction_patterns(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract interaction patterns and behaviors"""
    interactions = {
        'hover_effects': [],
        'click_handlers': [],
        'form_interactions': []
    }
    
    # Hover effects
    hover_elements = soup.find_all(class_=re.compile(r'hover|hover:'))
    if hover_elements:
        interactions['hover_effects'] = [{
            'type': 'hover',
            'count': len(hover_elements),
            'examples': [el.get('class', [])[0] for el in hover_elements[:3]]
        }]
    
    # Click handlers
    click_elements = soup.find_all(onclick=True)
    if click_elements:
        interactions['click_handlers'] = [{
            'type': 'click',
            'count': len(click_elements),
            'examples': [el.name for el in click_elements[:3]]
        }]
    
    # Form interactions
    form_elements = soup.find_all(['input', 'select', 'textarea'])
    if form_elements:
        interactions['form_interactions'] = [{
            'type': 'form',
            'count': len(form_elements),
            'examples': [el.name for el in form_elements[:3]]
        }]
    
    return interactions

def capture_page_screenshot(url: str, output_path: str) -> bool:
    """Capture a full-page screenshot using Playwright"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.goto(url, wait_until='networkidle')
            
            # Capture full page screenshot
            screenshot = page.screenshot(full_page=True)
            
            with open(output_path, 'wb') as f:
                f.write(screenshot)
            
            browser.close()
            return True
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False

def extract_css_structure(html: str, base_url: str) -> Dict[str, Any]:
    """Extract CSS structure and organization"""
    soup = BeautifulSoup(html, 'html.parser')
    
    css_structure = {
        'inline_styles': extract_inline_css(soup),
        'css_classes': extract_css_classes(soup),
        'css_variables': extract_css_variables(soup),
        'media_queries': extract_media_queries(soup)
    }
    
    return css_structure

def extract_inline_css(soup: BeautifulSoup) -> Dict[str, int]:
    """Extract inline CSS usage patterns"""
    inline_styles = {}
    
    for element in soup.find_all(style=True):
        style = element.get('style', '')
        properties = re.findall(r'([a-zA-Z-]+):\s*([^;]+)', style)
        
        for prop, value in properties:
            if prop in inline_styles:
                inline_styles[prop] += 1
            else:
                inline_styles[prop] = 1
    
    return inline_styles

def extract_css_classes(soup: BeautifulSoup) -> Dict[str, int]:
    """Extract CSS class usage patterns"""
    class_usage = {}
    
    for element in soup.find_all(class_=True):
        classes = element.get('class', [])
        for cls in classes:
            if cls in class_usage:
                class_usage[cls] += 1
            else:
                class_usage[cls] = 1
    
    return class_usage

def extract_css_variables(soup: BeautifulSoup) -> List[str]:
    """Extract CSS custom properties (variables)"""
    variables = []
    
    for element in soup.find_all('style'):
        content = element.get_text()
        var_matches = re.findall(r'--([a-zA-Z-]+):\s*([^;]+)', content)
        variables.extend([f"--{var}" for var, value in var_matches])
    
    return variables

def extract_media_queries(soup: BeautifulSoup) -> List[str]:
    """Extract media query breakpoints"""
    breakpoints = []
    
    for element in soup.find_all('style'):
        content = element.get_text()
        media_matches = re.findall(r'@media\s+\(([^)]+)\)', content)
        breakpoints.extend(media_matches)
    
    return breakpoints 

def extract_dominant_colors_from_image(image_path: str, max_colors: int = 8) -> Dict[str, Any]:
    """Extract dominant colors from an image using PIL and clustering"""
    try:
        from PIL import Image
        import numpy as np
        from sklearn.cluster import KMeans
        
        # Open and resize image for faster processing
        img = Image.open(image_path)
        img = img.resize((150, 150))  # Resize for faster processing
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert image to array of pixels
        pixels = np.array(img).reshape(-1, 3)
        
        # Use K-means to find dominant colors
        kmeans = KMeans(n_clusters=max_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get the colors and their counts
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Count occurrences of each color
        color_counts = np.bincount(labels)
        
        # Sort colors by frequency (most common first)
        sorted_indices = np.argsort(color_counts)[::-1]
        sorted_colors = colors[sorted_indices]
        sorted_counts = color_counts[sorted_indices]
        
        # Convert to hex format
        hex_colors = []
        for color in sorted_colors:
            r, g, b = color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            hex_colors.append(hex_color)
        
        # Filter out very light/white and very dark/black colors
        filtered_colors = []
        for i, hex_color in enumerate(hex_colors):
            r, g, b = sorted_colors[i]
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            # Only include colors that aren't too light or too dark
            if 30 < brightness < 225:
                filtered_colors.append(hex_color)
        
        if not filtered_colors:
            filtered_colors = hex_colors[:3]  # Fallback to original colors
        
        return {
            'primary': filtered_colors[0] if filtered_colors else None,
            'secondary': filtered_colors[1] if len(filtered_colors) > 1 else None,
            'palette': filtered_colors[:max_colors],
            'counts': sorted_counts.tolist()
        }
        
    except ImportError:
        # Fallback if PIL or sklearn not available
        return {
            'primary': None,
            'secondary': None,
            'palette': [],
            'counts': []
        }
    except Exception as e:
        print(f"Error extracting colors from image: {e}")
        return {
            'primary': None,
            'secondary': None,
            'palette': [],
            'counts': []
        } 
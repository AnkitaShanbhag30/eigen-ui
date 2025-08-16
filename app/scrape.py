import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import os

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

def analyze_color_scheme(html: str, base_url: str) -> Dict[str, any]:
    """Analyze the color scheme from CSS and inline styles"""
    soup = BeautifulSoup(html, 'html.parser')
    color_scheme = {
        'primary': None,
        'secondary': None,
        'accents': [],
        'backgrounds': [],
        'text_colors': []
    }
    
    # Extract colors from inline styles
    color_pattern = r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})|rgb\([^)]+\)|rgba\([^)]+\)'
    
    # Look for colors in style attributes
    for element in soup.find_all(attrs={'style': True}):
        style = element.get('style', '')
        colors = re.findall(color_pattern, style)
        for color in colors:
            if color.startswith('#'):
                color_scheme['accents'].append(color)
    
    # Look for colors in CSS classes (basic extraction)
    css_text = soup.find_all('style')
    for css in css_text:
        colors = re.findall(color_pattern, css.get_text())
        for color in colors:
            if color.startswith('#'):
                color_scheme['accents'].append(color)
    
    # Remove duplicates and limit results
    color_scheme['accents'] = list(dict.fromkeys(color_scheme['accents']))[:10]
    
    # Set primary and secondary if we have enough colors
    if len(color_scheme['accents']) >= 2:
        color_scheme['primary'] = color_scheme['accents'][0]
        color_scheme['secondary'] = color_scheme['accents'][1]
    
    return color_scheme

def detect_typography(html: str, base_url: str) -> Dict[str, any]:
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
    
    # Limit results
    typography['families'] = typography['families'][:5]
    typography['weights'] = typography['weights'][:5]
    typography['sizes'] = typography['sizes'][:5]
    
    return typography 
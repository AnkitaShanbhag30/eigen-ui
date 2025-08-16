import os
import json
import re
from typing import Dict, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_json(self, system: str, user: str) -> Dict:
        """Generate JSON response from system and user prompts"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI provider using the openai library"""
    
    def __init__(self):
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_json(self, system: str, user: str) -> Dict:
        """Generate JSON response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try to parse the entire response as JSON
                return json.loads(content)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {}

class GeminiProvider(LLMProvider):
    """Google Gemini provider using google-generativeai"""
    
    def __init__(self):
        import google.generativeai as genai
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_json(self, system: str, user: str) -> Dict:
        """Generate JSON response using Gemini"""
        try:
            # Combine system and user prompts
            combined_prompt = f"{system}\n\n{user}"
            
            response = self.model.generate_content(combined_prompt)
            content = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try to parse the entire response as JSON
                return json.loads(content)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {}

def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider"""
    provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    
    if provider == 'openai':
        return OpenAIProvider()
    elif provider == 'gemini':
        return GeminiProvider()
    else:
        print(f"Unknown provider '{provider}', defaulting to OpenAI")
        return OpenAIProvider() 
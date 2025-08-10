"""
OpenAI Service untuk Social Media Automation V2
Menggunakan OpenAI API untuk generate konten yang sesuai dengan platform
"""

import os
import openai
from typing import Dict, List, Optional
import json

class OpenAIService:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
            self.api_key = None
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.api_key is not None
    
    def generate_post_content(self, topic: str, platform: str, tone: str = 'professional', 
                            length: str = 'medium') -> str:
        """Generate post content untuk platform tertentu"""
        
        if not self.is_available():
            return self._get_fallback_content(topic, platform)
        
        try:
            # Platform-specific prompts
            platform_prompts = {
                'facebook': {
                    'style': 'engaging and conversational',
                    'length_guide': 'medium length (100-200 words)',
                    'features': 'Include emojis and call-to-action'
                },
                'twitter': {
                    'style': 'concise and impactful',
                    'length_guide': 'short (under 280 characters)',
                    'features': 'Include relevant hashtags'
                },
                'linkedin': {
                    'style': 'professional and insightful',
                    'length_guide': 'longer form (200-500 words)',
                    'features': 'Include professional insights and industry perspective'
                },
                'instagram': {
                    'style': 'visual-focused and trendy',
                    'length_guide': 'medium length with hashtags',
                    'features': 'Include relevant hashtags and visual descriptions'
                },
                'medium': {
                    'style': 'thoughtful and in-depth',
                    'length_guide': 'long form article style',
                    'features': 'Include subheadings and detailed explanations'
                },
                'guest_post': {
                    'style': 'authoritative and valuable',
                    'length_guide': 'comprehensive article',
                    'features': 'Include actionable insights and expert perspective'
                }
            }
            
            platform_info = platform_prompts.get(platform.lower(), platform_prompts['facebook'])
            
            # Length specifications
            length_specs = {
                'short': 'Keep it brief and to the point',
                'medium': 'Provide moderate detail',
                'long': 'Be comprehensive and detailed'
            }
            
            # Tone specifications
            tone_specs = {
                'professional': 'Use professional, business-appropriate language',
                'casual': 'Use casual, friendly language',
                'humorous': 'Include light humor where appropriate',
                'inspirational': 'Use motivational and uplifting language',
                'educational': 'Focus on teaching and informing'
            }
            
            prompt = f"""
Create a {platform} post about "{topic}".

Requirements:
- Platform: {platform}
- Style: {platform_info['style']}
- Length: {platform_info['length_guide']} ({length_specs.get(length, 'moderate detail')})
- Tone: {tone_specs.get(tone, 'professional and engaging')}
- Features: {platform_info['features']}

Additional guidelines:
- Make it engaging and valuable to the audience
- Include relevant keywords naturally
- Ensure it's appropriate for the platform's audience
- If it's for guest posting, make it authoritative and valuable

Topic: {topic}

Generate only the post content, no additional explanations.
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content expert who creates engaging, platform-specific content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            print(f"Error generating content with OpenAI: {e}")
            return self._get_fallback_content(topic, platform)
    
    def generate_hashtags(self, content: str, platform: str, count: int = 10) -> List[str]:
        """Generate relevant hashtags untuk content"""
        
        if not self.is_available():
            return self._get_fallback_hashtags(content, platform)
        
        try:
            prompt = f"""
Generate {count} relevant hashtags for this {platform} post:

"{content}"

Requirements:
- Make hashtags relevant to the content
- Include mix of popular and niche hashtags
- Appropriate for {platform} platform
- No spaces in hashtags
- Return only hashtags, one per line, with # symbol

Generate {count} hashtags:
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media hashtag expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [tag.strip() for tag in hashtags_text.split('\n') if tag.strip().startswith('#')]
            
            return hashtags[:count]
            
        except Exception as e:
            print(f"Error generating hashtags with OpenAI: {e}")
            return self._get_fallback_hashtags(content, platform)
    
    def improve_content(self, original_content: str, platform: str, 
                       improvement_type: str = 'engagement') -> str:
        """Improve existing content"""
        
        if not self.is_available():
            return original_content
        
        try:
            improvement_prompts = {
                'engagement': 'Make it more engaging and likely to get interactions',
                'clarity': 'Make it clearer and easier to understand',
                'professional': 'Make it more professional and polished',
                'casual': 'Make it more casual and conversational',
                'seo': 'Optimize it for better search visibility'
            }
            
            improvement_instruction = improvement_prompts.get(improvement_type, 'improve overall quality')
            
            prompt = f"""
Improve this {platform} post to {improvement_instruction}:

Original content:
"{original_content}"

Requirements:
- Keep the core message intact
- Make it appropriate for {platform}
- {improvement_instruction}
- Maintain the original length approximately
- Return only the improved content

Improved content:
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content improvement expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            improved_content = response.choices[0].message.content.strip()
            return improved_content
            
        except Exception as e:
            print(f"Error improving content with OpenAI: {e}")
            return original_content
    
    def generate_title(self, content: str, platform: str = 'general') -> str:
        """Generate title untuk content"""
        
        if not self.is_available():
            return self._get_fallback_title(content)
        
        try:
            prompt = f"""
Generate a compelling title for this content:

"{content[:500]}..."

Requirements:
- Make it attention-grabbing
- Appropriate for {platform}
- Keep it concise but descriptive
- Make it click-worthy
- Return only the title, no quotes or additional text

Title:
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a headline writing expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            title = response.choices[0].message.content.strip()
            return title
            
        except Exception as e:
            print(f"Error generating title with OpenAI: {e}")
            return self._get_fallback_title(content)
    
    def _get_fallback_content(self, topic: str, platform: str) -> str:
        """Fallback content when OpenAI is not available"""
        
        fallback_templates = {
            'facebook': f"🚀 Excited to share insights about {topic}! What are your thoughts on this? Let's discuss in the comments below! 💬 #SocialMedia #Engagement",
            'twitter': f"Exploring {topic} today 🔍 What's your take on this? #Twitter #Discussion",
            'linkedin': f"Sharing some thoughts on {topic}. In today's professional landscape, understanding this topic is crucial for success. What has been your experience? #LinkedIn #Professional",
            'instagram': f"✨ Diving deep into {topic} today! Swipe to see more insights 📸 #Instagram #Content #Inspiration",
            'medium': f"# Understanding {topic}\n\nIn this article, we'll explore the key aspects of {topic} and how it impacts our daily lives...",
            'guest_post': f"# The Complete Guide to {topic}\n\nAs an expert in this field, I want to share valuable insights about {topic} that can help you..."
        }
        
        return fallback_templates.get(platform.lower(), f"Here are some insights about {topic} that I wanted to share with you.")
    
    def _get_fallback_hashtags(self, content: str, platform: str) -> List[str]:
        """Fallback hashtags when OpenAI is not available"""
        
        common_hashtags = {
            'facebook': ['#SocialMedia', '#Engagement', '#Community', '#Share', '#Connect'],
            'twitter': ['#Twitter', '#SocialMedia', '#Trending', '#Discussion', '#Share'],
            'linkedin': ['#LinkedIn', '#Professional', '#Business', '#Career', '#Networking'],
            'instagram': ['#Instagram', '#Content', '#Inspiration', '#Photography', '#Creative'],
            'medium': ['#Medium', '#Writing', '#Content', '#Blog', '#Article'],
            'guest_post': ['#GuestPost', '#Content', '#Marketing', '#SEO', '#Blog']
        }
        
        return common_hashtags.get(platform.lower(), ['#SocialMedia', '#Content', '#Share'])
    
    def _get_fallback_title(self, content: str) -> str:
        """Fallback title when OpenAI is not available"""
        
        # Extract first sentence or first 50 characters
        first_sentence = content.split('.')[0] if '.' in content else content[:50]
        return first_sentence.strip() + ('...' if len(content) > 50 else '')
    
    def test_connection(self) -> Dict:
        """Test OpenAI API connection"""
        
        if not self.is_available():
            return {
                'success': False,
                'message': 'OpenAI API key not configured'
            }
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'Hello, OpenAI API is working!'"}
                ],
                max_tokens=20
            )
            
            return {
                'success': True,
                'message': 'OpenAI API connection successful',
                'response': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'OpenAI API connection failed: {str(e)}'
            }


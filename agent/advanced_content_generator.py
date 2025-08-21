"""
Advanced Content Generator for Founder Socials AI Agent

This module provides sophisticated content generation with customizable options,
professional prompts, and platform-specific optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from .ai_client import AIClient

logger = logging.getLogger(__name__)

class WritingStyle(Enum):
    """Content writing styles"""
    DESCRIPTIVE = "descriptive"
    NARRATIVE = "narrative"
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"

class TargetAudience(Enum):
    """Target audience types"""
    STARTUP_FOUNDERS = "startup_founders"
    INVESTORS = "investors"
    DEVELOPERS = "developers"
    BUSINESS_PROFESSIONALS = "business_professionals"
    ENTREPRENEURS = "entrepreneurs"
    GENERAL_PUBLIC = "general_public"
    INDUSTRY_EXPERTS = "industry_experts"
    CUSTOMERS = "customers"

class ContentTone(Enum):
    """Content tone options"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CASUAL = "casual"
    FORMAL = "formal"
    ENTHUSIASTIC = "enthusiastic"
    THOUGHTFUL = "thoughtful"
    CONFIDENT = "confident"

class ContentPurpose(Enum):
    """Content purpose/goal"""
    EDUCATE = "educate"
    ENGAGE = "engage"
    INSPIRE = "inspire"
    SELL = "sell"
    INFORM = "inform"
    ENTERTAIN = "entertain"
    BUILD_AUTHORITY = "build_authority"
    DRIVE_TRAFFIC = "drive_traffic"

class AdvancedContentGenerator:
    """
    Advanced content generator with sophisticated prompts and customization options
    """
    
    def __init__(self, config: Dict):
        """Initialize the advanced content generator"""
        self.config = config
        self.ai_client = AIClient(config.get('ai', {}))
        self.startup_info = config.get('startup', {})
        
        # Professional content templates
        self.content_templates = self._load_content_templates()
        
        logger.info("Advanced Content Generator initialized")
    
    def _load_content_templates(self) -> Dict:
        """Load professional content templates"""
        return {
            'facebook': {
                'hooks': [
                    "🚀 Exciting news from the startup world:",
                    "💡 Here's what we learned building our startup:",
                    "🎯 Startup founders, this one's for you:",
                    "📈 Growth hack that changed our business:",
                    "💬 Let's talk about something important:",
                ],
                'structures': [
                    "Hook → Problem → Solution → CTA",
                    "Story → Lesson → Application → Question",
                    "Stat → Insight → Example → CTA",
                    "Question → Answer → Value → CTA"
                ]
            },
            'twitter': {
                'hooks': [
                    "🧵 Thread on",
                    "💡 Quick insight:",
                    "🚀 Startup lesson:",
                    "📊 Data point:",
                    "⚡ Hot take:",
                ],
                'structures': [
                    "Hook → Insight → Example → CTA",
                    "Question → Answer → Value",
                    "Stat → Context → Takeaway",
                    "Problem → Solution → Benefit"
                ]
            },
            'linkedin': {
                'hooks': [
                    "I've been thinking about",
                    "Here's what 3 years of building a startup taught me:",
                    "Unpopular opinion in the startup world:",
                    "The biggest mistake I see founders make:",
                    "Data from 100+ startup conversations:",
                ],
                'structures': [
                    "Hook → Context → Insight → Lesson → CTA",
                    "Problem → Analysis → Solution → Result → Takeaway",
                    "Story → Challenge → Solution → Outcome → Lesson",
                    "Question → Investigation → Finding → Application → CTA"
                ]
            }
        }
    
    async def generate_advanced_content(
        self,
        topic: str,
        platform: str,
        content_type: str,
        writing_style: WritingStyle,
        target_audience: TargetAudience,
        content_tone: ContentTone,
        content_purpose: ContentPurpose,
        additional_options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate advanced content with sophisticated customization
        
        Args:
            topic: Content topic
            platform: Target platform
            content_type: Type of content (post, article, thread)
            writing_style: Writing style preference
            target_audience: Target audience
            content_tone: Content tone
            content_purpose: Content purpose/goal
            additional_options: Additional customization options
            
        Returns:
            Generated content with metadata
        """
        logger.info(f"Generating advanced content: {topic} for {platform}")
        
        try:
            # Build sophisticated prompt
            prompt = self._build_advanced_prompt(
                topic, platform, content_type, writing_style,
                target_audience, content_tone, content_purpose, additional_options
            )
            
            # Generate content
            content = await self.ai_client.generate_text(prompt, max_tokens=4000)
            
            # Post-process content
            processed_content = await self._post_process_content(
                content, platform, content_type, additional_options
            )
            
            # Generate metadata
            metadata = self._generate_content_metadata(
                topic, platform, content_type, writing_style,
                target_audience, content_tone, content_purpose
            )
            
            result = {
                'content': processed_content,
                'metadata': metadata,
                'word_count': len(processed_content.split()),
                'character_count': len(processed_content),
                'estimated_read_time': self._calculate_read_time(processed_content),
                'engagement_score': self._calculate_engagement_score(processed_content, platform),
                'suggestions': await self._generate_improvement_suggestions(processed_content, platform)
            }
            
            logger.info(f"Advanced content generated successfully: {len(processed_content)} chars")
            return result
            
        except Exception as e:
            logger.error(f"Error generating advanced content: {e}")
            raise
    
    def _build_advanced_prompt(
        self,
        topic: str,
        platform: str,
        content_type: str,
        writing_style: WritingStyle,
        target_audience: TargetAudience,
        content_tone: ContentTone,
        content_purpose: ContentPurpose,
        additional_options: Optional[Dict] = None
    ) -> str:
        """Build sophisticated, professional prompt"""
        
        # Get platform-specific requirements
        platform_specs = self._get_platform_specifications(platform)
        
        # Get audience insights
        audience_insights = self._get_audience_insights(target_audience)
        
        # Get style guidelines
        style_guidelines = self._get_style_guidelines(writing_style, content_tone)
        
        # Build comprehensive prompt
        if platform.lower() == 'facebook':
            return self._build_facebook_prompt(
                topic, content_type, writing_style, target_audience,
                content_tone, content_purpose, platform_specs, audience_insights,
                style_guidelines, additional_options
            )
        elif platform.lower() == 'twitter':
            return self._build_twitter_prompt(
                topic, content_type, writing_style, target_audience,
                content_tone, content_purpose, platform_specs, audience_insights,
                style_guidelines, additional_options
            )
        elif platform.lower() == 'linkedin':
            return self._build_linkedin_prompt(
                topic, content_type, writing_style, target_audience,
                content_tone, content_purpose, platform_specs, audience_insights,
                style_guidelines, additional_options
            )
        else:
            return self._build_generic_prompt(
                topic, platform, content_type, writing_style, target_audience,
                content_tone, content_purpose, platform_specs, audience_insights,
                style_guidelines, additional_options
            )
    
    def _build_facebook_prompt(
        self, topic: str, content_type: str, writing_style: WritingStyle,
        target_audience: TargetAudience, content_tone: ContentTone,
        content_purpose: ContentPurpose, platform_specs: Dict,
        audience_insights: Dict, style_guidelines: Dict,
        additional_options: Optional[Dict] = None
    ) -> str:
        """Build Facebook-specific professional prompt"""
        
        hooks = self.content_templates['facebook']['hooks']
        structures = self.content_templates['facebook']['structures']
        
        return f"""
You are a world-class social media content strategist and copywriter specializing in Facebook content that drives engagement and business results.

CONTENT BRIEF:
Topic: "{topic}"
Platform: Facebook
Content Type: {content_type}
Writing Style: {writing_style.value.replace('_', ' ').title()}
Target Audience: {target_audience.value.replace('_', ' ').title()}
Content Tone: {content_tone.value.title()}
Content Purpose: {content_purpose.value.replace('_', ' ').title()}

STARTUP CONTEXT:
- Company: {self.startup_info.get('name', 'our startup')}
- Industry: {self.startup_info.get('industry', 'Technology')}
- Value Proposition: {self.startup_info.get('value_proposition', 'Innovative solutions')}
- Brand Voice: {self.startup_info.get('brand_voice', 'Professional and innovative')}
- Website: {self.startup_info.get('website', 'our website')}
- Product: {self.startup_info.get('product_name', 'our product')}

🚨 CRITICAL: NO PLACEHOLDERS ALLOWED
- Never use brackets like [Link to blog post], [Your Name], [Company Name]
- Never use placeholder text like "Your Startup Name" or "your-website.com"
- Use the actual company information provided above
- For links, use generic calls-to-action like "Check out our website" or "Learn more in our bio"
- If specific information isn't available, write generically without placeholders

FACEBOOK CONTENT REQUIREMENTS:
🎯 ENGAGEMENT OPTIMIZATION:
- Character limit: {platform_specs['max_chars']} characters maximum
- Optimal length: {platform_specs['optimal_length']} characters for maximum engagement
- Include 3-4 relevant hashtags maximum (Facebook users prefer fewer hashtags)
- Use emojis strategically to increase visual appeal and engagement

📱 FACEBOOK-SPECIFIC BEST PRACTICES:
- Hook readers in the first 2 lines (before "See More" truncation)
- Write for mobile users (short paragraphs, easy scanning)
- Include a clear call-to-action that drives meaningful interaction
- Use storytelling elements that encourage sharing
- Ask engaging questions to drive comments

🎨 WRITING STYLE REQUIREMENTS ({writing_style.value}):
{style_guidelines['description']}
{style_guidelines['techniques']}

👥 AUDIENCE OPTIMIZATION ({target_audience.value}):
{audience_insights['description']}
{audience_insights['pain_points']}
{audience_insights['motivations']}
{audience_insights['preferred_content']}

🎭 TONE REQUIREMENTS ({content_tone.value}):
- Maintain {content_tone.value} tone throughout
- Ensure tone matches startup's brand voice
- Balance professionalism with approachability

🎯 PURPOSE OPTIMIZATION ({content_purpose.value}):
- Primary goal: {content_purpose.value.replace('_', ' ')}
- Include clear value proposition
- End with compelling call-to-action aligned with purpose

CONTENT STRUCTURE OPTIONS (choose most appropriate):
{chr(10).join([f"• {structure}" for structure in structures])}

ENGAGEMENT ELEMENTS TO INCLUDE:
- Compelling hook from: {', '.join(hooks[:3])}
- Visual elements (emojis, spacing)
- Question or poll to drive comments
- Shareable insight or tip
- Clear next step for audience

STARTUP CREDIBILITY SIGNALS:
- Reference relevant experience or data
- Include social proof if applicable
- Demonstrate expertise in {self.startup_info.get('industry', 'technology')}
- Align with company's value proposition

MANDATORY OPTIMIZATION:
1. Count every character to ensure under {platform_specs['max_chars']} total
2. Front-load the most engaging content (first 125 characters visible before "See More")
3. Use line breaks for readability on mobile
4. Include 1-2 relevant hashtags naturally integrated
5. End with clear call-to-action

DELIVERABLE:
Write a complete Facebook post that maximizes engagement while achieving the specified purpose. The content should be ready to publish immediately and optimized for Facebook's algorithm and user behavior patterns.

Do not use markdown formatting (**bold**, *italic*). Use natural emphasis, emojis, and strategic formatting only.
"""
    
    def _build_twitter_prompt(
        self, topic: str, content_type: str, writing_style: WritingStyle,
        target_audience: TargetAudience, content_tone: ContentTone,
        content_purpose: ContentPurpose, platform_specs: Dict,
        audience_insights: Dict, style_guidelines: Dict,
        additional_options: Optional[Dict] = None
    ) -> str:
        """Build Twitter-specific professional prompt"""
        
        hooks = self.content_templates['twitter']['hooks']
        structures = self.content_templates['twitter']['structures']
        
        if content_type == 'thread':
            return f"""
You are a Twitter growth expert and content strategist specializing in viral Twitter threads that drive engagement and follower growth.

THREAD BRIEF:
Topic: "{topic}"
Platform: Twitter
Content Type: Thread ({additional_options.get('thread_length', 5)} tweets)
Writing Style: {writing_style.value.replace('_', ' ').title()}
Target Audience: {target_audience.value.replace('_', ' ').title()}
Content Tone: {content_tone.value.title()}
Content Purpose: {content_purpose.value.replace('_', ' ').title()}

STARTUP CONTEXT:
- Company: {self.startup_info.get('name', 'Unknown Startup')}
- Industry: {self.startup_info.get('industry', 'Technology')}
- Value Proposition: {self.startup_info.get('value_proposition', 'Innovative solutions')}

TWITTER THREAD REQUIREMENTS:
🧵 THREAD STRUCTURE:
- Tweet 1: Hook + Preview of value
- Tweets 2-{additional_options.get('thread_length', 5)-1}: Core content with clear progression
- Final Tweet: Conclusion + CTA + Thread recap

📱 TWEET SPECIFICATIONS:
- Each tweet: Maximum 280 characters
- Include tweet numbers (1/{additional_options.get('thread_length', 5)}, 2/{additional_options.get('thread_length', 5)}, etc.)
- Use strategic line breaks for readability
- 1-2 hashtags per tweet maximum

🎯 ENGAGEMENT OPTIMIZATION:
- Hook that promises specific value in first tweet
- Each tweet should provide standalone value
- Include questions, polls, or engagement drivers
- Use emojis for visual appeal and structure
- End with clear call-to-action

CONTENT REQUIREMENTS:
{style_guidelines['description']}
{audience_insights['preferred_content']}

DELIVERABLE:
Create a {additional_options.get('thread_length', 5)}-tweet thread with clear progression, maximum engagement potential, and alignment with startup goals.
"""
        else:
            return f"""
You are a Twitter growth expert specializing in high-engagement single tweets that drive meaningful interaction and business results.

TWEET BRIEF:
Topic: "{topic}"
Platform: Twitter
Content Type: Single Tweet
Writing Style: {writing_style.value.replace('_', ' ').title()}
Target Audience: {target_audience.value.replace('_', ' ').title()}
Content Tone: {content_tone.value.title()}
Content Purpose: {content_purpose.value.replace('_', ' ').title()}

STARTUP CONTEXT:
- Company: {self.startup_info.get('name', 'Unknown Startup')}
- Industry: {self.startup_info.get('industry', 'Technology')}
- Value Proposition: {self.startup_info.get('value_proposition', 'Innovative solutions')}

TWITTER REQUIREMENTS:
🚨 CRITICAL CONSTRAINTS:
- EXACTLY ONE TWEET ONLY
- Maximum 280 characters total (count every character, space, emoji)
- NO thread indicators (1/n, see below, thread 🧵)
- Complete message in single tweet

🎯 ENGAGEMENT OPTIMIZATION:
- Compelling hook in first 10 words
- Clear value proposition
- Include 1-2 strategic hashtags
- Use emojis for visual appeal
- Ask question or include CTA if space allows

WRITING REQUIREMENTS ({writing_style.value}):
{style_guidelines['description']}

AUDIENCE OPTIMIZATION ({target_audience.value}):
{audience_insights['pain_points']}
{audience_insights['motivations']}

STRUCTURE OPTIONS:
{chr(10).join([f"• {structure}" for structure in structures])}

MANDATORY VERIFICATION:
1. Count every character including spaces, emojis, hashtags
2. Ensure message is complete and valuable as standalone tweet
3. Verify under 280 characters
4. Include clear value for target audience
5. Align with content purpose

DELIVERABLE:
One high-engagement tweet under 280 characters that delivers maximum value and drives meaningful interaction.
"""
    
    def _build_linkedin_prompt(
        self, topic: str, content_type: str, writing_style: WritingStyle,
        target_audience: TargetAudience, content_tone: ContentTone,
        content_purpose: ContentPurpose, platform_specs: Dict,
        audience_insights: Dict, style_guidelines: Dict,
        additional_options: Optional[Dict] = None
    ) -> str:
        """Build LinkedIn-specific professional prompt"""
        
        hooks = self.content_templates['linkedin']['hooks']
        structures = self.content_templates['linkedin']['structures']
        
        return f"""
You are a LinkedIn thought leader and professional content strategist specializing in business content that builds authority and drives professional engagement.

CONTENT BRIEF:
Topic: "{topic}"
Platform: LinkedIn
Content Type: {content_type}
Writing Style: {writing_style.value.replace('_', ' ').title()}
Target Audience: {target_audience.value.replace('_', ' ').title()}
Content Tone: {content_tone.value.title()}
Content Purpose: {content_purpose.value.replace('_', ' ').title()}

STARTUP CONTEXT:
- Company: {self.startup_info.get('name', 'our startup')}
- Industry: {self.startup_info.get('industry', 'Technology')}
- Value Proposition: {self.startup_info.get('value_proposition', 'Innovative solutions')}
- Professional Background: {self.startup_info.get('background', 'Startup leadership')}
- Website: {self.startup_info.get('website', 'our website')}
- Product: {self.startup_info.get('product_name', 'our product')}

🚨 CRITICAL: NO PLACEHOLDERS ALLOWED
- Never use brackets like [Link to blog post], [Your Name], [Company Name]
- Never use placeholder text like "Your Startup Name" or "your-website.com"
- Use the actual company information provided above
- For links, use generic calls-to-action like "Check out our website" or "Learn more in our bio"
- If specific information isn't available, write generically without placeholders

LINKEDIN CONTENT REQUIREMENTS:
💼 PROFESSIONAL OPTIMIZATION:
- Character limit: {platform_specs['max_chars']} characters maximum
- Optimal length: {platform_specs['optimal_length']} characters for engagement
- Professional tone with authentic personal voice
- Include 3-5 relevant hashtags maximum
- Use strategic line breaks for readability

🎯 LINKEDIN ALGORITHM OPTIMIZATION:
- Hook readers in first 3 lines (before "see more")
- Include industry insights or data points
- Encourage professional discussion and comments
- Share authentic experiences and lessons learned
- Provide actionable takeaways for professionals

📈 BUSINESS VALUE REQUIREMENTS:
- Demonstrate thought leadership in {self.startup_info.get('industry', 'technology')}
- Share credible business insights
- Include relevant professional experience
- Provide value to professional network
- Build startup/founder credibility

WRITING STYLE REQUIREMENTS ({writing_style.value}):
{style_guidelines['description']}
{style_guidelines['professional_adaptation']}

AUDIENCE OPTIMIZATION ({target_audience.value}):
{audience_insights['description']}
{audience_insights['professional_interests']}
{audience_insights['business_challenges']}

CONTENT STRUCTURE OPTIONS:
{chr(10).join([f"• {structure}" for structure in structures])}

ENGAGEMENT ELEMENTS:
- Compelling hook from: {', '.join(hooks[:3])}
- Professional storytelling
- Data points or insights when relevant
- Question to drive professional discussion
- Clear call-to-action for business goals

CREDIBILITY SIGNALS:
- Reference relevant business experience
- Include industry-specific insights
- Demonstrate startup/business expertise
- Share authentic leadership perspectives
- Connect to broader business trends

MANDATORY OPTIMIZATION:
1. Front-load most engaging content (first 140 characters before "see more")
2. Use paragraph breaks for mobile readability
3. Include 3-5 relevant professional hashtags
4. End with engaging question or clear CTA
5. Ensure professional yet approachable tone

DELIVERABLE:
Write a complete LinkedIn post that builds thought leadership, drives professional engagement, and advances business goals while providing genuine value to the professional community.

Do not use markdown formatting. Use natural emphasis and professional formatting only.
"""
    
    def _get_platform_specifications(self, platform: str) -> Dict:
        """Get platform-specific technical requirements"""
        specs = {
            'facebook': {
                'max_chars': 63206,
                'optimal_length': 400,
                'max_hashtags': 3,
                'optimal_hashtags': 2,
                'line_break_strategy': 'mobile_friendly'
            },
            'twitter': {
                'max_chars': 280,
                'optimal_length': 240,
                'max_hashtags': 2,
                'optimal_hashtags': 1,
                'line_break_strategy': 'minimal'
            },
            'linkedin': {
                'max_chars': 3000,
                'optimal_length': 1500,
                'max_hashtags': 5,
                'optimal_hashtags': 3,
                'line_break_strategy': 'professional'
            }
        }
        return specs.get(platform.lower(), specs['facebook'])
    
    def _get_audience_insights(self, target_audience: TargetAudience) -> Dict:
        """Get detailed audience insights for targeting"""
        insights = {
            TargetAudience.STARTUP_FOUNDERS: {
                'description': 'Ambitious entrepreneurs building innovative companies',
                'pain_points': 'Limited resources, market uncertainty, scaling challenges, fundraising pressure',
                'motivations': 'Growth, innovation, market disruption, building something meaningful',
                'preferred_content': 'Practical advice, success stories, industry insights, actionable strategies',
                'professional_interests': 'Business growth, leadership, innovation, market trends',
                'business_challenges': 'Scaling operations, team building, market fit, investor relations'
            },
            TargetAudience.INVESTORS: {
                'description': 'VCs, angels, and institutional investors seeking opportunities',
                'pain_points': 'Deal flow quality, market analysis, due diligence efficiency, portfolio performance',
                'motivations': 'ROI maximization, market insight, deal sourcing, portfolio value creation',
                'preferred_content': 'Market analysis, investment thesis, startup metrics, industry trends',
                'professional_interests': 'Investment opportunities, market dynamics, startup performance',
                'business_challenges': 'Deal evaluation, market timing, portfolio management, exit strategies'
            },
            TargetAudience.DEVELOPERS: {
                'description': 'Software engineers, technical leads, and technology professionals',
                'pain_points': 'Technical complexity, changing technologies, work-life balance, career growth',
                'motivations': 'Technical mastery, innovation, problem-solving, career advancement',
                'preferred_content': 'Technical insights, development practices, technology trends, career advice',
                'professional_interests': 'Technology advancement, software engineering, technical leadership',
                'business_challenges': 'Technical debt, scalability, team collaboration, technology choices'
            },
            TargetAudience.BUSINESS_PROFESSIONALS: {
                'description': 'Corporate executives, managers, and business development professionals',
                'pain_points': 'Market competition, operational efficiency, team performance, strategic planning',
                'motivations': 'Career growth, business success, market leadership, professional recognition',
                'preferred_content': 'Business strategy, leadership insights, market analysis, professional development',
                'professional_interests': 'Business strategy, leadership, market dynamics, professional growth',
                'business_challenges': 'Strategic planning, team management, market positioning, operational excellence'
            }
        }
        return insights.get(target_audience, insights[TargetAudience.BUSINESS_PROFESSIONALS])
    
    def _get_style_guidelines(self, writing_style: WritingStyle, content_tone: ContentTone) -> Dict:
        """Get detailed style and tone guidelines"""
        style_guides = {
            WritingStyle.DESCRIPTIVE: {
                'description': 'Rich, detailed writing that paints clear pictures and provides comprehensive information',
                'techniques': 'Use vivid language, specific details, sensory elements, and comprehensive explanations',
                'professional_adaptation': 'Balance detail with business relevance, use concrete examples'
            },
            WritingStyle.NARRATIVE: {
                'description': 'Story-driven content that engages through compelling narratives and personal experiences',
                'techniques': 'Use story structure, character development, conflict/resolution, and emotional connection',
                'professional_adaptation': 'Frame business insights within compelling stories and case studies'
            },
            WritingStyle.INFORMATIVE: {
                'description': 'Clear, factual content focused on educating and providing valuable information',
                'techniques': 'Use clear structure, factual accuracy, logical flow, and educational value',
                'professional_adaptation': 'Present business information clearly with actionable insights'
            },
            WritingStyle.PERSUASIVE: {
                'description': 'Compelling content designed to influence opinions and drive specific actions',
                'techniques': 'Use strong arguments, evidence-based claims, emotional appeals, and clear CTAs',
                'professional_adaptation': 'Build business cases with evidence and logical reasoning'
            },
            WritingStyle.CONVERSATIONAL: {
                'description': 'Friendly, approachable writing that feels like a natural conversation',
                'techniques': 'Use casual language, questions, direct address, and relatable examples',
                'professional_adaptation': 'Maintain professionalism while being approachable and accessible'
            }
        }
        return style_guides.get(writing_style, style_guides[WritingStyle.INFORMATIVE])
    
    async def _post_process_content(self, content: str, platform: str, content_type: str, options: Optional[Dict] = None) -> str:
        """Post-process generated content for optimization"""
        # Remove markdown formatting
        content = content.replace('**', '').replace('*', '').replace('_', '')
        
        # Platform-specific optimizations
        if platform.lower() == 'twitter' and content_type != 'thread':
            # Ensure single tweet compliance
            if len(content) > 280:
                content = content[:277] + "..."
        
        # Clean up formatting
        content = content.strip()
        
        return content
    
    def _generate_content_metadata(self, topic: str, platform: str, content_type: str, 
                                 writing_style: WritingStyle, target_audience: TargetAudience,
                                 content_tone: ContentTone, content_purpose: ContentPurpose) -> Dict:
        """Generate metadata for the content"""
        return {
            'topic': topic,
            'platform': platform,
            'content_type': content_type,
            'writing_style': writing_style.value,
            'target_audience': target_audience.value,
            'content_tone': content_tone.value,
            'content_purpose': content_purpose.value,
            'generated_at': datetime.now().isoformat(),
            'generator_version': '2.0_advanced'
        }
    
    def _calculate_read_time(self, content: str) -> int:
        """Calculate estimated read time in seconds"""
        words = len(content.split())
        # Average reading speed: 200 words per minute
        return max(1, round(words / 200 * 60))
    
    def _calculate_engagement_score(self, content: str, platform: str) -> float:
        """Calculate predicted engagement score (0-100)"""
        score = 50  # Base score
        
        # Check for engagement elements
        if '?' in content:
            score += 10  # Questions drive engagement
        if any(emoji in content for emoji in ['🚀', '💡', '🎯', '📈', '💪']):
            score += 5   # Emojis increase engagement
        if content.count('#') >= 1:
            score += 5   # Hashtags help discoverability
        
        # Platform-specific adjustments
        if platform.lower() == 'twitter' and len(content) <= 240:
            score += 10  # Optimal Twitter length
        elif platform.lower() == 'linkedin' and 500 <= len(content) <= 1500:
            score += 10  # Optimal LinkedIn length
        
        return min(100, score)
    
    async def _generate_improvement_suggestions(self, content: str, platform: str) -> List[str]:
        """Generate suggestions for content improvement"""
        suggestions = []
        
        # Check length optimization
        if platform.lower() == 'twitter' and len(content) > 240:
            suggestions.append("Consider shortening for optimal Twitter engagement")
        
        # Check for engagement elements
        if '?' not in content:
            suggestions.append("Add a question to drive comments and engagement")
        
        if '#' not in content:
            suggestions.append("Include 1-2 relevant hashtags for better discoverability")
        
        # Check for emojis
        emoji_count = sum(1 for char in content if ord(char) > 127)
        if emoji_count == 0:
            suggestions.append("Consider adding emojis for visual appeal")
        
        return suggestions
    
    def _build_generic_prompt(self, topic: str, platform: str, content_type: str,
                            writing_style: WritingStyle, target_audience: TargetAudience,
                            content_tone: ContentTone, content_purpose: ContentPurpose,
                            platform_specs: Dict, audience_insights: Dict,
                            style_guidelines: Dict, additional_options: Optional[Dict] = None) -> str:
        """Build generic prompt for other platforms"""
        return f"""
Create professional {platform} content about "{topic}" with the following specifications:

Writing Style: {writing_style.value.replace('_', ' ').title()}
Target Audience: {target_audience.value.replace('_', ' ').title()}
Content Tone: {content_tone.value.title()}
Content Purpose: {content_purpose.value.replace('_', ' ').title()}

Startup Context:
- Company: {self.startup_info.get('name', 'Unknown')}
- Industry: {self.startup_info.get('industry', 'Technology')}

Platform Requirements:
- Maximum {platform_specs['max_chars']} characters
- Optimal length: {platform_specs['optimal_length']} characters
- Include {platform_specs['optimal_hashtags']} relevant hashtags

Audience Insights:
{audience_insights['description']}
{audience_insights['preferred_content']}

Style Requirements:
{style_guidelines['description']}

Create engaging, valuable content that serves the specified purpose and resonates with the target audience.
"""

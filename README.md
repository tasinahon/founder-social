# Founder Socials AI Agent

An intelligent AI agent that helps startup founders create, optimize, and publish blog posts and social media content automatically.

## Features

### 🎯 Content Planning
- Generate content ideas based on startup industry and target audience
- Create editorial calendars with optimal posting schedules
- Research trending topics and competitor content
- Suggest content themes and campaigns

### ✍️ Content Creation
- Write engaging blog posts with SEO optimization
- Create platform-specific social media posts
- Generate multiple content variations for A/B testing
- Maintain brand voice and messaging consistency

### 🚀 Content Publishing
- Automatic posting to multiple platforms:
  - Blog platforms (WordPress, Medium, Ghost)
  - Social media (Twitter/X, LinkedIn, Facebook, Instagram)
- Scheduled posting with optimal timing
- Cross-platform content adaptation

### 📊 Analytics & Optimization
- Track content performance across platforms
- Provide engagement insights and recommendations
- Optimize content based on performance data
- Generate performance reports

## Architecture

```
founder-socials/
├── agent/                 # Core AI agent logic
├── mcp_servers/          # MCP server integrations
├── api/                  # External API integrations
├── ui/                   # Web dashboard
├── config/               # Configuration files
├── templates/            # Content templates
└── data/                 # Content and analytics data
```

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure the agent:**
```bash
cp config/config.yaml config/config.yaml
# Edit config.yaml with your API keys and startup information
```

3. **Run the agent:**
```bash
# Option 1: Using the startup script (recommended)
python run.py

# Option 2: Using the main application
python main.py

# Option 3: CLI mode for specific commands
python main.py --mode cli --command plan --weeks 4
```

4. **Access the web dashboard:**
   - Main Dashboard: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## Usage Examples

### Web Interface
1. **Dashboard**: Overview of content performance and quick actions
2. **Plan Content**: Generate AI-powered editorial calendars
3. **Create Content**: Generate blog posts and social media content
4. **Publish**: Manage content publishing across platforms
5. **Analytics**: View performance metrics and insights
6. **Optimize**: Get AI recommendations for content strategy
7. **Settings**: Configure startup details and API credentials

### Command Line Interface

**Generate content plan:**
```bash
python main.py --mode cli --command plan --weeks 8 --blog-frequency 2 --social-frequency 5
```

**Create content:**
```bash
python main.py --mode cli --command generate --topic "How we built our MVP" --content-type blog --platform general
```

**Run full pipeline:**
```bash
python main.py --mode cli --command publish --auto-publish
```

**Get analytics:**
```bash
python main.py --mode cli --command analytics --days 30
```

**Optimize strategy:**
```bash
python main.py --mode cli --command optimize
```

## Social Media Authentication

The agent supports OAuth authentication for social media platforms through the web interface:

### Supported Platforms
- **Twitter/X**: OAuth 2.0 with PKCE
- **LinkedIn**: OAuth 2.0
- **Facebook**: OAuth 2.0
- **Instagram**: OAuth 2.0

### Setup Instructions

1. **Configure API Credentials** in `config/config.yaml`:
   ```yaml
   api_keys:
     twitter:
       client_id: "your-twitter-client-id"
       client_secret: "your-twitter-client-secret"
     linkedin:
       client_id: "your-linkedin-client-id"
       client_secret: "your-linkedin-client-secret"
     # ... other platforms
   ```

2. **Connect Accounts** via the web interface:
   - Go to Settings → Social Media Connections
   - Click "Connect" for each platform
   - Complete OAuth flow in your browser
   - Grant necessary permissions

3. **Platform-Specific Setup**:
   - **Twitter**: Create app in [Twitter Developer Portal](https://developer.twitter.com)
   - **LinkedIn**: Create app in [LinkedIn Developers](https://www.linkedin.com/developers)
   - **Facebook**: Create app in [Facebook Developers](https://developers.facebook.com)
   - **Instagram**: Use Facebook app with Instagram Basic Display

### Redirect URIs
Add these redirect URIs to your platform apps:
- `http://localhost:8000/auth/twitter/callback`
- `http://localhost:8000/auth/linkedin/callback`
- `http://localhost:8000/auth/facebook/callback`
- `http://localhost:8000/auth/instagram/callback`

## AI Providers

The agent supports multiple AI providers for content generation:

### Supported Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo (via OpenAI API)
- **Azure OpenAI**: GPT-4, GPT-3.5-turbo (via Azure OpenAI Service)
- **DeepSeek-R1**: Advanced reasoning model (via Azure OpenAI)
- **GPT-4o**: Latest OpenAI model (via Azure AI Inference)

### Configuration

Configure your preferred AI provider in `config/config.yaml`:

```yaml
ai:
  provider: "gpt4o"  # openai, azure_openai, deepseek_r1, gpt4o
  
  # OpenAI Configuration
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4-turbo-preview"
    temperature: 0.7
  
  # Azure OpenAI Configuration
  azure_openai:
    api_key: "your-azure-openai-api-key"
    azure_endpoint: "https://your-resource.openai.azure.com/"
    model: "gpt-4-turbo-preview"
    api_version: "2024-12-01-preview"
    temperature: 0.7
  
  # DeepSeek-R1 Configuration
  deepseek_r1:
    api_key: "your-deepseek-api-key"
    azure_endpoint: "https://your-resource.openai.azure.com/"
    api_version: "2024-12-01-preview"
    temperature: 0.7
  
  # GPT-4o Configuration (Recommended)
  gpt4o:
    api_key: "your-gpt4o-api-key"
    endpoint: "https://your-resource.openai.azure.com/openai/deployments/gpt-4o"
    temperature: 0.7
```

### Testing AI Integration

Run the test scripts to verify your AI provider configuration:

```bash
# Test DeepSeek-R1
python test_simple_deepseek.py

# Test GPT-4o
python test_gpt4o.py

# Test all Azure AI providers
python test_azure_ai.py
```

## Configuration

The agent supports multiple platforms and can be configured via `config/config.yaml`:

- **AI Providers**: OpenAI, Azure OpenAI, DeepSeek-R1, GPT-4o
- **Social Media Platforms**: Twitter/X, LinkedIn, Facebook, Instagram (OAuth)
- **Blog Platforms**: WordPress, Medium, Ghost
- **Analytics**: Google Analytics, Search Console
- **Content Optimization**: SEO tools, readability checkers

## MCP Servers Used

- **File System MCP**: Content storage and management
- **Git MCP**: Version control for content
- **Web Search MCP**: Research and trend analysis
- **Database MCP**: Analytics and metadata storage

## License

MIT License - see LICENSE file for details. 
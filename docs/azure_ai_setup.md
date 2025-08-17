# Azure AI Integration Setup Guide

This guide covers setting up Azure OpenAI and DeepSeek-R1 integration for the Founder Socials AI Agent.

## Overview

The agent now supports three AI providers:
1. **OpenAI** - Direct API access
2. **Azure OpenAI** - OpenAI models hosted on Azure
3. **DeepSeek-R1** - Advanced reasoning model via Azure AI Inference

## Prerequisites

- Azure subscription
- Azure OpenAI Service resource (for Azure OpenAI)
- Azure AI Services resource (for DeepSeek-R1)
- Python 3.8+ with pip

## Azure OpenAI Setup

### 1. Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Azure OpenAI" resource
3. Choose your subscription and resource group
4. Select a region close to you
5. Choose a pricing tier
6. Deploy the resource

### 2. Deploy Models

1. Go to your Azure OpenAI resource
2. Navigate to "Model deployments"
3. Deploy the models you want to use:
   - `gpt-4-turbo-preview`
   - `gpt-4`
   - `gpt-35-turbo`

### 3. Get Credentials

1. Go to "Keys and Endpoint" in your Azure OpenAI resource
2. Copy the endpoint URL
3. Copy one of the API keys

### 4. Configure the Agent

Update your `config/config.yaml`:

```yaml
ai:
  provider: "azure_openai"
  azure_openai:
    api_key: "your-azure-openai-api-key"
    azure_endpoint: "https://your-resource.openai.azure.com/"
    model: "gpt-4-turbo-preview"
    api_version: "2024-12-01-preview"
    temperature: 0.7
```

## DeepSeek-R1 Setup

### 1. Create Azure AI Services Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "AI Services" resource
3. Choose your subscription and resource group
4. Select a region
5. Choose a pricing tier
6. Deploy the resource

### 2. Deploy DeepSeek-R1 Model

1. Go to your AI Services resource
2. Navigate to "Model deployments"
3. Deploy the "DeepSeek-R1" model
4. Note the deployment name and endpoint

### 3. Get Credentials

1. Go to "Keys and Endpoint" in your AI Services resource
2. Copy the endpoint URL
3. Copy one of the API keys

### 4. Configure the Agent

Update your `config/config.yaml`:

```yaml
ai:
  provider: "deepseek_r1"
  deepseek_r1:
    api_key: "your-deepseek-api-key"
    endpoint: "https://your-resource.services.ai.azure.com/models"
    api_version: "2024-05-01-preview"
    temperature: 0.7
```

## Example Configuration

Here's a complete example configuration with all three providers:

```yaml
# AI Provider Settings
ai:
  provider: "deepseek_r1"  # Primary provider
  
  # OpenAI Configuration
  openai:
    api_key: "your-openai-api-key-here"
    model: "gpt-4-turbo-preview"
    temperature: 0.7
  
  # Azure OpenAI Configuration
  azure_openai:
    api_key: "your-azure-openai-api-key-here"
    azure_endpoint: "https://your-resource.openai.azure.com/"
    model: "gpt-4-turbo-preview"
    api_version: "2024-12-01-preview"
    temperature: 0.7
  
  # DeepSeek-R1 Configuration (Recommended)
  deepseek_r1:
    api_key: "your-deepseek-api-key-here"
    endpoint: "https://your-resource.services.ai.azure.com/models"
    api_version: "2024-05-01-preview"
    temperature: 0.7

# API Keys for OAuth Authentication
api_keys:
  openai:
    api_key: "your-openai-api-key-here"
  azure_openai:
    api_key: "your-azure-openai-api-key-here"
    azure_endpoint: "https://your-resource.openai.azure.com/"
  deepseek_r1:
    api_key: "your-deepseek-api-key-here"
    endpoint: "https://your-resource.services.ai.azure.com/models"
```

## Testing the Integration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Test Script

```bash
python test_azure_ai.py
```

This will test:
- Azure OpenAI connection and text generation
- DeepSeek-R1 connection and text generation
- Content generation with the configured provider

### 3. Expected Output

```
Starting Azure AI integration tests...

==================================================
Testing Azure OpenAI...
Azure OpenAI client initialized successfully
Azure OpenAI response: In today's rapidly evolving business landscape...

==================================================
Testing DeepSeek-R1...
DeepSeek-R1 client initialized successfully
DeepSeek-R1 response: The integration of artificial intelligence...

==================================================
Testing content generation...
Blog post generated: 1247 characters
Blog post preview: ---
title: "The Future of AI in Startups"
author: "Test Startup"
date: "2024-01-15"
...

Test Results:
Azure OpenAI: ✓ PASS
DeepSeek-R1: ✓ PASS
Content Generation: ✓ PASS

🎉 DeepSeek-R1 integration is working correctly!
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API key is correct
   - Check that your endpoint URL is properly formatted
   - Ensure your Azure resource is active

2. **Model Deployment Issues**
   - Verify the model is deployed in your Azure resource
   - Check the deployment name matches your configuration
   - Ensure you have sufficient quota

3. **Network Issues**
   - Check your internet connection
   - Verify firewall settings allow Azure API calls
   - Try using a different region if latency is high

4. **Rate Limiting**
   - Check your Azure resource quota
   - Implement retry logic for rate-limited requests
   - Consider upgrading your pricing tier

### Error Messages

- `"Azure OpenAI API key or endpoint not provided"`: Check your configuration
- `"DeepSeek-R1 API key or endpoint not provided"`: Verify DeepSeek-R1 settings
- `"Model not found"`: Ensure the model is deployed in Azure
- `"Rate limit exceeded"`: Check your quota and implement retries

## Best Practices

1. **Security**
   - Store API keys in environment variables
   - Use Azure Key Vault for production deployments
   - Rotate API keys regularly

2. **Performance**
   - Use appropriate temperature settings for your use case
   - Implement caching for repeated requests
   - Monitor API usage and costs

3. **Reliability**
   - Implement retry logic for failed requests
   - Use fallback providers if available
   - Monitor API response times

4. **Cost Optimization**
   - Choose appropriate pricing tiers
   - Monitor usage patterns
   - Use caching to reduce API calls

## Migration from Anthropic

If you're migrating from Anthropic Claude to DeepSeek-R1:

1. **Update Configuration**
   - Change `provider` from `"anthropic"` to `"deepseek_r1"`
   - Remove Anthropic API key
   - Add DeepSeek-R1 configuration

2. **Test Content Generation**
   - Run the test script to verify functionality
   - Check content quality and style
   - Adjust temperature and other parameters as needed

3. **Update Dependencies**
   - Remove `anthropic` from requirements.txt
   - Add `azure-ai-inference` and `azure-core`

## Support

For issues with:
- **Azure OpenAI**: Check [Azure OpenAI documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- **DeepSeek-R1**: Check [Azure AI Services documentation](https://docs.microsoft.com/en-us/azure/ai-services/)
- **Agent Integration**: Check the main README.md or create an issue

## License

This integration follows the same license as the main project (MIT). 
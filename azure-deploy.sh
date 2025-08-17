# Azure Web App Deployment Script
# Run this in Azure Cloud Shell or local Azure CLI

# 1. Login to Azure
az login

# 2. Create Resource Group (if needed)
az group create --name founder-socials-rg --location eastus

# 3. Create App Service Plan
az appservice plan create --name founder-socials-plan --resource-group founder-socials-rg --sku B1 --is-linux

# 4. Create Web App with container
az webapp create --resource-group founder-socials-rg --plan founder-socials-plan --name founder-socials-app --deployment-container-image-name python:3.11-slim

# 5. Configure deployment from local files
az webapp deployment source config-zip --resource-group founder-socials-rg --name founder-socials-app --src founder-socials-deployment.zip

# 6. Set environment variables
az webapp config appsettings set --resource-group founder-socials-rg --name founder-socials-app --settings \
    AZURE_OPENAI_API_KEY="A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ" \
    AZURE_OPENAI_ENDPOINT="https://ai-founder-3699.openai.azure.com/" \
    GPT4O_API_KEY="A02OOjVTyTDPX0UFljXCRWNEazqTF5Sdq5hlXV3CN2eVD1ljSHWwJQQJ99ALAC5RqLJXJ3w3AAAAACOGfOHQ" \
    GPT4O_ENDPOINT="https://ai-founder-3699.openai.azure.com/openai/deployments/gpt-4o" \
    TWITTER_CLIENT_ID="T05ETUk4WlBaZ2ZaekhkaDg0TUo6MTpjaQ" \
    TWITTER_CLIENT_SECRET="Zo4nqnAAc_Cv9DGZf1DklDQzkGoR1uQPiR2y0b50CevzKzQWFV" \
    FACEBOOK_APP_ID="1937644817012952" \
    FACEBOOK_APP_SECRET="6753b4e4cb87066014d9ec1cd7bb34f3" \
    LINKEDIN_CLIENT_ID="78ye1cdk35bvui" \
    LINKEDIN_CLIENT_SECRET="WPL_AP1.La452ZR7LbixU1Th.91JzRQ==" \
    PORT="8000" \
    ENVIRONMENT="production"

# 7. Configure startup command
az webapp config set --resource-group founder-socials-rg --name founder-socials-app --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo "Deployment complete! Your app will be available at: https://founder-socials-app.azurewebsites.net"

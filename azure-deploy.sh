#!/bin/bash
# Azure Web App Deployment Script

set -e

echo "=========================================="
echo "Azure Web App Deployment Script"
echo "=========================================="

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-ba-agent-rg}"
APP_NAME="${APP_NAME:-ba-agent-backend}"
LOCATION="${LOCATION:-eastus}"
PLAN_NAME="${PLAN_NAME:-ba-agent-plan}"
SKU="${SKU:-B1}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  App Name: $APP_NAME"
echo "  Location: $LOCATION"
echo "  Plan: $PLAN_NAME"
echo "  SKU: $SKU"
echo ""

# Check if logged in
echo -e "${YELLOW}Checking Azure login...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}Not logged in to Azure. Please run: az login${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Logged in${NC}"

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
echo -e "${GREEN}✓ Resource group created${NC}"

# Create App Service Plan
echo -e "${YELLOW}Creating App Service Plan...${NC}"
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku $SKU \
  --is-linux \
  --output none
echo -e "${GREEN}✓ App Service Plan created${NC}"

# Create Web App
echo -e "${YELLOW}Creating Web App...${NC}"
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --runtime "PYTHON:3.12" \
  --output none
echo -e "${GREEN}✓ Web App created${NC}"

# Configure app settings
echo -e "${YELLOW}Configuring app settings...${NC}"
echo -e "${YELLOW}Please set the following environment variables in Azure Portal:${NC}"
echo "  - GEMINI_API_KEY"
echo "  - DATABASE_URL"
echo "  - PINECONE_API_KEY"
echo "  - PINECONE_INDEX_NAME"
echo ""

# Set basic settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    FLASK_DEBUG="False" \
    PORT="8000" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ENABLE_ORYX_BUILD="true" \
  --output none

echo -e "${GREEN}✓ Basic settings configured${NC}"

# Set startup command
echo -e "${YELLOW}Setting startup command...${NC}"
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info main:app" \
  --output none
echo -e "${GREEN}✓ Startup command set${NC}"

# Enable Always On
echo -e "${YELLOW}Enabling Always On...${NC}"
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --always-on true \
  --output none
echo -e "${GREEN}✓ Always On enabled${NC}"

# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment source show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query url -o tsv 2>/dev/null || echo "")

if [ -z "$DEPLOYMENT_URL" ]; then
    echo -e "${YELLOW}Configuring local Git deployment...${NC}"
    DEPLOYMENT_URL=$(az webapp deployment source config-local-git \
      --resource-group $RESOURCE_GROUP \
      --name $APP_NAME \
      --query url -o tsv)
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Configuration Complete!"
echo "==========================================${NC}"
echo ""
echo "Web App URL: https://$APP_NAME.azurewebsites.net"
echo "Deployment URL: $DEPLOYMENT_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Set environment variables in Azure Portal:"
echo "   - GEMINI_API_KEY"
echo "   - DATABASE_URL"
echo "   - PINECONE_API_KEY"
echo "   - PINECONE_INDEX_NAME"
echo ""
echo "2. Deploy your code:"
echo "   git remote add azure $DEPLOYMENT_URL"
echo "   git push azure main"
echo ""
echo "3. Or use Azure Portal → Deployment Center"
echo ""



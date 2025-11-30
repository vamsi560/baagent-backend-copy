# Azure Web App Deployment Guide

This guide covers deploying the BA Agent Backend to Azure Web App for Linux.

## Prerequisites

1. **Azure Account** with active subscription
2. **Azure CLI** installed and configured
3. **Git** repository with your code
4. **Python 3.12** (Azure Web App supports 3.8-3.12)

## Quick Start

### Option 1: Azure Portal (Recommended for First Deployment)

1. **Create Azure Web App:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource" → "Web App"
   - Fill in:
     - **Name**: `ba-agent-backend` (or your preferred name)
     - **Runtime stack**: Python 3.12
     - **Operating System**: Linux
     - **Region**: Choose closest to your users
     - **App Service Plan**: Create new or use existing
   - Click "Review + create" → "Create"

2. **Configure Application Settings:**
   - Go to your Web App → Configuration → Application settings
   - Add the following environment variables:

   ```
   # Required
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=postgresql+psycopg2://user:password@host:5432/database
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=ba-agent-documents
   
   # Optional but recommended
   FLASK_DEBUG=False
   PORT=8000
   PYTHON_VERSION=3.12
   SCM_DO_BUILD_DURING_DEPLOYMENT=true
   
   # Azure-specific
   WEBSITES_PORT=8000
   WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
   ```

3. **Set Startup Command:**
   - Go to Configuration → General settings
   - **Startup Command**: 
     ```
     gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info main:app
     ```

4. **Deploy Code:**
   - Go to Deployment Center
   - Choose your source (GitHub, Azure DevOps, Local Git, etc.)
   - Follow the deployment wizard

### Option 2: Azure CLI

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="ba-agent-rg"
APP_NAME="ba-agent-backend"
LOCATION="eastus"
PLAN_NAME="ba-agent-plan"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service Plan (Linux, B1 Basic tier)
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --runtime "PYTHON:3.12"

# Configure app settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    GEMINI_API_KEY="your_gemini_api_key" \
    DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/db" \
    PINECONE_API_KEY="your_pinecone_api_key" \
    PINECONE_INDEX_NAME="ba-agent-documents" \
    FLASK_DEBUG="False" \
    PORT="8000" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Set startup command
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info main:app"

# Deploy from local Git
az webapp deployment source config-local-git \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME

# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment source show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query url -o tsv)

echo "Deployment URL: $DEPLOYMENT_URL"

# Add remote and push
git remote add azure $DEPLOYMENT_URL
git push azure main
```

## Configuration Files

### 1. `requirements-azure.txt`
- Uses CPU-only PyTorch to reduce deployment size
- Includes all necessary dependencies
- Optimized for Azure Web App

### 2. `startup.sh`
- Startup script for Azure Web App
- Uses Gunicorn for production
- Falls back to Flask dev server if Gunicorn unavailable

### 3. `.deployment` (Auto-created)
Azure will create this automatically, but you can create it manually:

```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://...` |
| `PINECONE_API_KEY` | Pinecone API key | `pcsk_...` |
| `PINECONE_INDEX_NAME` | Pinecone index name | `ba-agent-documents` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_DEBUG` | Enable Flask debug mode | `False` |
| `PORT` | Application port | `8000` |
| `PYTHON_VERSION` | Python version | `3.12` |
| `WEBSITES_PORT` | Azure Web App port | `8000` |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `us-east-1` |

## Database Setup

### Azure Database for PostgreSQL

1. **Create PostgreSQL Server:**
   ```bash
   az postgres flexible-server create \
     --resource-group $RESOURCE_GROUP \
     --name ba-agent-db \
     --location $LOCATION \
     --admin-user dbadmin \
     --admin-password "YourSecurePassword123!" \
     --sku-name Standard_B1ms \
     --tier Burstable \
     --version 14 \
     --storage-size 32
   ```

2. **Enable pgvector Extension:**
   ```bash
   az postgres flexible-server parameter set \
     --resource-group $RESOURCE_GROUP \
     --server-name ba-agent-db \
     --name azure.extensions \
     --value vector
   ```

3. **Create Database:**
   ```bash
   az postgres flexible-server db create \
     --resource-group $RESOURCE_GROUP \
     --server-name ba-agent-db \
     --database-name ba_agent
   ```

4. **Update Connection String:**
   ```
   DATABASE_URL=postgresql+psycopg2://dbadmin:YourSecurePassword123!@ba-agent-db.postgres.database.azure.com:5432/ba_agent
   ```

## Deployment Methods

### Method 1: Git Deployment (Recommended)

1. **Configure Deployment Source:**
   - Azure Portal → Deployment Center
   - Choose source (GitHub, Azure DevOps, etc.)
   - Authorize and select repository

2. **Automatic Deployment:**
   - Every push to main branch triggers deployment
   - Build logs available in Deployment Center

### Method 2: Azure CLI

```bash
# Deploy from local directory
az webapp up \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --runtime "PYTHON:3.12"
```

### Method 3: ZIP Deploy

```bash
# Create deployment package
zip -r deploy.zip . -x "*.git*" "*.venv*" "__pycache__*"

# Deploy
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --src deploy.zip
```

### Method 4: VS Code Extension

1. Install "Azure App Service" extension
2. Right-click project → "Deploy to Web App"
3. Select your Web App
4. Wait for deployment

## Build Configuration

### Using requirements-azure.txt

Azure will automatically detect `requirements.txt`. To use `requirements-azure.txt`:

1. **Option A: Rename file**
   ```bash
   mv requirements-azure.txt requirements.txt
   ```

2. **Option B: Set build command**
   - Azure Portal → Configuration → General settings
   - **Build Command**: `pip install -r requirements-azure.txt`

### Build Customization

Create `.deployment` file:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
PRE_BUILD_COMMAND=pip install --upgrade pip
POST_BUILD_COMMAND=python deploy_vector_db.py
```

## Monitoring and Logging

### Application Logs

1. **Enable Logging:**
   - Azure Portal → App Service logs
   - Enable "Application Logging (Filesystem)"
   - Set level to "Information"

2. **View Logs:**
   ```bash
   az webapp log tail \
     --resource-group $RESOURCE_GROUP \
     --name $APP_NAME
   ```

3. **Download Logs:**
   ```bash
   az webapp log download \
     --resource-group $RESOURCE_GROUP \
     --name $APP_NAME \
     --log-file app-logs.zip
   ```

### Application Insights

1. **Create Application Insights:**
   ```bash
   az monitor app-insights component create \
     --app ba-agent-insights \
     --location $LOCATION \
     --resource-group $RESOURCE_GROUP
   ```

2. **Connect to Web App:**
   - Azure Portal → Your Web App → Application Insights
   - Click "Turn on Application Insights"
   - Select your Application Insights resource

## Performance Optimization

### 1. Enable Always On
- Azure Portal → Configuration → General settings
- Enable "Always On" (prevents cold starts)

### 2. Scale Up/Out
- **Scale Up**: Increase App Service Plan tier
- **Scale Out**: Add more instances
- Azure Portal → Scale up (App Service plans) or Scale out (App Service)

### 3. Enable Caching
- Consider Azure Redis Cache for session storage
- Configure in Application settings

## Troubleshooting

### Common Issues

#### 1. Module Not Found Errors
```bash
# SSH into Web App
az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME

# Check installed packages
pip list

# Reinstall requirements
pip install -r requirements-azure.txt
```

#### 2. Port Binding Issues
- Ensure `WEBSITES_PORT` matches your application port
- Check startup command uses correct port

#### 3. Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check firewall rules allow Azure services
- Test connection from Azure Cloud Shell

#### 4. Large Deployment Size
- Use `requirements-azure.txt` (CPU-only PyTorch)
- Check `.deploymentignore` excludes unnecessary files
- Enable build optimization

### Debugging

1. **Enable Remote Debugging:**
   - Azure Portal → Configuration → General settings
   - Enable "Remote debugging"

2. **SSH Access:**
   ```bash
   az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME
   ```

3. **View Real-time Logs:**
   ```bash
   az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME
   ```

## Security Best Practices

1. **Use Managed Identity** for Azure services
2. **Store secrets in Azure Key Vault**
3. **Enable HTTPS only**
4. **Configure CORS properly**
5. **Use Application Gateway** for WAF protection
6. **Enable authentication** if needed

## Cost Optimization

1. **Use Basic/Standard tier** for development
2. **Scale down** during non-business hours
3. **Use Azure Dev/Test pricing** if eligible
4. **Monitor usage** with Cost Management

## Next Steps

1. **Set up CI/CD pipeline** (Azure DevOps, GitHub Actions)
2. **Configure staging slots** for zero-downtime deployments
3. **Set up monitoring alerts**
4. **Configure backup strategy**
5. **Set up custom domain** and SSL certificate

## Support

- [Azure Web Apps Documentation](https://docs.microsoft.com/azure/app-service/)
- [Python on Azure](https://docs.microsoft.com/azure/developer/python/)
- [Azure Support](https://azure.microsoft.com/support/)



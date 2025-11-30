# Azure Web App - Quick Start Guide

## 🚀 Quick Deployment (5 minutes)

### Step 1: Prepare Files

1. **Use Azure-specific requirements:**
   ```bash
   # Option A: Rename for Azure
   cp requirements-azure.txt requirements.txt
   
   # Option B: Keep both and Azure will use requirements.txt
   ```

2. **Verify files exist:**
   - ✅ `requirements-azure.txt` (or `requirements.txt`)
   - ✅ `startup.sh`
   - ✅ `main.py`
   - ✅ `.deployment`
   - ✅ `.deploymentignore`

### Step 2: Create Web App (Azure Portal)

1. Go to [Azure Portal](https://portal.azure.com)
2. Create → Web App
3. Fill in:
   - **Name**: `ba-agent-backend`
   - **Runtime**: Python 3.12
   - **OS**: Linux
   - **Region**: Your choice
4. Click "Review + create" → "Create"

### Step 3: Configure Settings

Go to **Configuration → Application settings** and add:

```
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=ba-agent-documents
FLASK_DEBUG=False
PORT=8000
WEBSITES_PORT=8000
```

### Step 4: Set Startup Command

Go to **Configuration → General settings**:

**Startup Command:**
```
gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info main:app
```

### Step 5: Deploy

**Option A: GitHub (Recommended)**
1. Go to **Deployment Center**
2. Connect your GitHub repository
3. Select branch (usually `main`)
4. Azure will auto-deploy on every push

**Option B: Local Git**
```bash
# Get deployment URL from Azure Portal → Deployment Center
git remote add azure <deployment-url>
git push azure main
```

**Option C: ZIP Deploy**
```bash
zip -r deploy.zip . -x "*.git*" "*.venv*"
az webapp deployment source config-zip \
  --resource-group <resource-group> \
  --name <app-name> \
  --src deploy.zip
```

## ✅ Verification

1. **Check deployment:**
   - Go to **Deployment Center** → View logs

2. **Test endpoint:**
   ```bash
   curl https://<app-name>.azurewebsites.net/api/health
   ```

3. **View logs:**
   ```bash
   az webapp log tail --resource-group <rg> --name <app-name>
   ```

## 🔧 Key Differences from Vercel

| Aspect | Vercel | Azure Web App |
|--------|--------|---------------|
| **Requirements File** | `requirements-vercel.txt` | `requirements-azure.txt` or `requirements.txt` |
| **Startup** | Automatic | Need `startup.sh` or startup command |
| **Port** | Automatic | Must use `PORT` env var (usually 8000) |
| **Server** | Automatic | Use Gunicorn for production |
| **Build** | Automatic | Uses Oryx build system |

## 📝 Important Notes

1. **Port Configuration:**
   - Azure sets `PORT` environment variable
   - Use port 8000 (not 5000)
   - Set `WEBSITES_PORT=8000` in app settings

2. **Startup Command:**
   - Must use Gunicorn for production
   - Flask dev server not recommended

3. **Requirements:**
   - Use `requirements-azure.txt` for CPU-only PyTorch
   - Or rename it to `requirements.txt`

4. **Database:**
   - Use Azure Database for PostgreSQL
   - Enable pgvector extension if needed
   - Configure firewall rules

## 🐛 Troubleshooting

### Build Fails
- Check build logs in Deployment Center
- Verify `requirements-azure.txt` syntax
- Ensure Python 3.12 is selected

### App Won't Start
- Check startup command is correct
- Verify port matches `WEBSITES_PORT`
- Check application logs

### Module Not Found
- SSH into app: `az webapp ssh`
- Run: `pip list` to see installed packages
- Reinstall: `pip install -r requirements-azure.txt`

## 📚 Full Documentation

See `AZURE_DEPLOYMENT_GUIDE.md` for complete details.



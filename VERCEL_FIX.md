# Vercel Deployment Fix - Removing PyTorch

## Problem
Vercel is still installing PyTorch (412 MB) even though we're using Gemini embeddings.

## Root Cause
Vercel auto-detects `requirements.txt` and installs from it. The file still had torch/sentence-transformers.

## Solution Applied

### 1. Updated `requirements.txt`
- **Removed**: torch, torchvision, torchaudio, sentence-transformers
- **Added**: google-generativeai (for Gemini embeddings)
- This is now the lightweight version for Vercel

### 2. Created `requirements-azure.txt`
- Contains torch/sentence-transformers for Azure deployments
- Use this file for Azure Web App deployments

### 3. Updated `.vercelignore`
- Added patterns to exclude ALL torch libraries if they somehow get installed

### 4. Updated `vercel.json`
- Build command now explicitly uses `requirements.txt` (which is now lightweight)

## Verification

After deployment, check:
1. No torch libraries in `.vercel/python/py3.12/_vendor/torch/`
2. Deployment size should be ~50MB instead of 4.5GB
3. Build logs should show `google-generativeai` installed, not `torch`

## For Azure Deployments

If deploying to Azure Web App, use:
```bash
pip install -r requirements-azure.txt
```

Or update Azure build command to use `requirements-azure.txt`.

## Next Steps

1. **Commit and push** these changes
2. **Redeploy** on Vercel
3. **Verify** deployment size is reduced
4. **Test** embeddings work with Gemini API

The deployment should now succeed without the 300MB limit error! 🎉


# Fix for Large CUDA Libraries in Vercel Deployment

## Problem
Vercel is detecting large PyTorch CUDA libraries (>4GB total) that aren't needed for CPU-only inference.

## Solution
We've configured the project to use CPU-only PyTorch and exclude CUDA libraries.

## Changes Made

### 1. Updated `requirements.txt`
- Added CPU-only PyTorch installation with `--extra-index-url`
- Specified CPU versions: `torch==2.1.0+cpu`, `torchvision==0.16.0+cpu`, `torchaudio==2.1.0+cpu`

### 2. Created `.vercelignore`
- Excludes large CUDA libraries from Vercel deployment
- Excludes other unnecessary files

### 3. Created `.gitignore`
- Prevents committing large files to repository
- Excludes CUDA libraries and build artifacts

### 4. Updated `database.py`
- Forces CPU-only mode with `CUDA_VISIBLE_DEVICES=''`
- Better error messages for CPU-only installation

## Deployment Steps

### Option 1: Clean Install (Recommended)
```bash
# Remove existing virtual environment
rm -rf .venv venv env

# Create new virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install CPU-only PyTorch first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip install -r requirements.txt
```

### Option 2: Update Existing Installation
```bash
# Uninstall existing PyTorch
pip uninstall torch torchvision torchaudio -y

# Install CPU-only versions
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Reinstall sentence-transformers
pip install --force-reinstall sentence-transformers
```

## Verification

After installation, verify CPU-only PyTorch:
```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")  # Should be False
print(f"Device: {torch.device('cpu')}")
```

## Vercel Deployment

1. **Commit the changes:**
   ```bash
   git add requirements.txt .vercelignore .gitignore database.py
   git commit -m "Fix: Use CPU-only PyTorch to reduce deployment size"
   git push
   ```

2. **Vercel will automatically:**
   - Use the updated `requirements.txt` with CPU-only PyTorch
   - Respect `.vercelignore` to exclude large files
   - Build should complete without CUDA libraries

3. **Monitor deployment:**
   - Check Vercel build logs for size warnings
   - Deployment should be much smaller (<500MB instead of >4GB)

## Expected Results

- **Before:** ~4.5GB deployment (with CUDA libraries)
- **After:** ~200-300MB deployment (CPU-only)
- **Performance:** No change (embedding model works fine on CPU)

## Troubleshooting

### If deployment still includes CUDA libraries:

1. **Check Vercel build logs** for PyTorch installation
2. **Verify `.vercelignore`** is in the repository root
3. **Clear Vercel build cache:**
   - Go to Vercel Dashboard → Project Settings → Build & Development Settings
   - Clear build cache and redeploy

### If embedding model fails to load:

1. **Check logs** for PyTorch version compatibility
2. **Verify CPU-only installation:**
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```
   Should print `False`

3. **Reinstall if needed:**
   ```bash
   pip uninstall torch torchvision torchaudio sentence-transformers -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   pip install sentence-transformers
   ```

## Notes

- **CPU-only is sufficient** for sentence-transformers inference
- **Embedding generation is fast enough** on CPU for production use
- **No GPU required** for this use case
- **Significantly smaller deployment** size


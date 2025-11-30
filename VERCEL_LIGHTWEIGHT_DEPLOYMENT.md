# Vercel Lightweight Deployment (No PyTorch)

## Problem
PyTorch (torch) is **412 MB** and exceeds Vercel's **300 MB** file size limit, even with CPU-only builds.

## Solution
**Remove PyTorch entirely** and use **Gemini embeddings** instead of `sentence-transformers`.

### Benefits
- ✅ **No PyTorch** - Reduces deployment size from ~4.5GB to ~50MB
- ✅ **Faster cold starts** - No model loading time
- ✅ **Better embeddings** - Gemini's `embedding-001` (768/1536/3072 dimensions vs 384)
- ✅ **No local model storage** - All embeddings via API
- ✅ **Uses existing GEMINI_API_KEY** - No additional API key needed
- ✅ **Unified API** - Same API key for both text generation and embeddings

### Trade-offs
- ⚠️ **API costs** - ~$0.15 per 1M tokens (still very affordable)
- ⚠️ **Requires internet** - Embeddings generated via API

## Quick Setup

### 1. Use Lightweight Requirements

**Option A: Rename file**
```bash
cp requirements-vercel-lightweight.txt requirements.txt
```

**Option B: Update vercel.json**
```json
{
  "buildCommand": "pip install -r requirements-vercel-lightweight.txt"
}
```

### 2. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

```
GEMINI_API_KEY=AIza... (you already have this)
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=ba-agent-documents
GEMINI_EMBEDDING_DIMENSION=768
```

**Important:** 
- Use your existing `GEMINI_API_KEY` (no new API key needed!)
- Set `GEMINI_EMBEDDING_DIMENSION` to `768`, `1536`, or `3072` (default: 768)
- Your Pinecone index must match this dimension

### 3. Update Pinecone Index

If your existing index uses 384 dimensions (sentence-transformers), you need to:

**Option A: Create new index (recommended)**
```python
# Run this once to create new index
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-key")
pc.create_index(
    name="ba-agent-documents-v2",
    dimension=768,  # or 1536, 3072 for Gemini
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

**Option B: Recreate existing index**
```python
# Delete and recreate (WARNING: loses all data)
pc.delete_index("ba-agent-documents")
pc.create_index(
    name="ba-agent-documents",
    dimension=768,  # or 1536, 3072 for Gemini
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

### 4. Redeploy Documents

After switching to OpenAI embeddings, you need to re-index your documents:

```bash
python deploy_vector_db.py
```

## Cost Estimation

Gemini Embeddings Pricing:
- `embedding-001`: **$0.15 per 1M tokens** (standard)
- **$0.075 per 1M tokens** (batch API - for high volume)

Example:
- 1 document = ~1000 tokens
- 1000 documents = 1M tokens = **$0.15** (or $0.075 with batch)
- 100,000 documents = **$15.00** (or $7.50 with batch)

**Very affordable!** Much cheaper than hosting PyTorch models.

## Comparison

| Feature | sentence-transformers | Gemini Embeddings |
|---------|---------------------|-------------------|
| **Size** | 412 MB (torch) | 0 MB (API) |
| **Cold Start** | ~5-10 seconds | Instant |
| **Dimensions** | 384 | 768/1536/3072 (configurable) |
| **Quality** | Good | Better (top MTEB rankings) |
| **Cost** | Free (local) | $0.15/1M tokens ($0.075 batch) |
| **Internet** | Not required | Required |
| **API Key** | N/A | Uses existing GEMINI_API_KEY |
| **Deployment** | ❌ Too large | ✅ Works |

## Fallback Option

If you want to keep sentence-transformers as a fallback:

1. Keep both in `requirements.txt`
2. Set `OPENAI_API_KEY` for lightweight deployment
3. Code will automatically use OpenAI if available, fallback to sentence-transformers

## Migration Checklist

- [ ] Verify `GEMINI_API_KEY` is set in Vercel (you likely already have this)
- [ ] Set `GEMINI_EMBEDDING_DIMENSION=768` in Vercel (or 1536/3072)
- [ ] Update Pinecone index to match dimension (768/1536/3072)
- [ ] Use `requirements-vercel-lightweight.txt`
- [ ] Re-index all documents
- [ ] Test search functionality
- [ ] Monitor Gemini API usage

## Troubleshooting

### "Vector database not available"
- Check `GEMINI_API_KEY` is set (you likely already have this)
- Check `PINECONE_API_KEY` is set
- Check `PINECONE_INDEX_NAME` matches your index

### "Dimension mismatch"
- Your Pinecone index must match `GEMINI_EMBEDDING_DIMENSION` (768/1536/3072)
- Update Pinecone index dimension or change `GEMINI_EMBEDDING_DIMENSION` to match

### "Gemini API error"
- Verify `GEMINI_API_KEY` is valid
- Check API quota/billing in Google AI Studio
- Ensure internet connectivity
- Check if you're using the correct model name: `models/embedding-001`

## Next Steps

1. **Deploy with lightweight requirements**
2. **Test embedding generation**
3. **Re-index documents**
4. **Monitor costs** (should be minimal)

Your deployment will now be **~50MB instead of 4.5GB**! 🎉


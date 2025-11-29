#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script to initialize Pinecone index
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

from database import PINECONE_ENABLED, PINECONE_API_KEY, PINECONE_INDEX_NAME, VECTOR_SIZE, pinecone_client, embedding_model

def setup_pinecone():
    """Initialize Pinecone index"""
    print("=" * 60)
    print("Setting up Pinecone Vector Database")
    print("=" * 60)
    
    if not PINECONE_ENABLED:
        print("ERROR: Pinecone is not enabled")
        return False
    
    if not pinecone_client:
        print("ERROR: Pinecone client not initialized")
        return False
    
    if not embedding_model:
        print("WARNING: Embedding model not initialized")
        print("   This is required for adding documents, but Pinecone setup can continue")
        print("   You may need to fix the embedding model dependencies")
    
    try:
        print(f"\nChecking Pinecone index: {PINECONE_INDEX_NAME}")
        
        # List existing indexes (new Pinecone API)
        existing_indexes = pinecone_client.list_indexes()
        index_names = [idx.name for idx in existing_indexes] if existing_indexes else []
        
        if PINECONE_INDEX_NAME in index_names:
            print(f"SUCCESS: Index '{PINECONE_INDEX_NAME}' already exists")
            
            # Get index stats
            try:
                index = pinecone_client.Index(PINECONE_INDEX_NAME)
                stats = index.describe_index_stats()
                print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
                print(f"   Namespaces: {len(stats.get('namespaces', {}))}")
            except:
                print("   (Could not retrieve stats)")
            
            return True
        else:
            print(f"Creating new index: {PINECONE_INDEX_NAME}")
            print(f"   Dimension: {VECTOR_SIZE}")
            print(f"   Metric: cosine")
            
            # Create index (new Pinecone API requires spec parameter)
            try:
                from pinecone import ServerlessSpec
                pinecone_client.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=VECTOR_SIZE,
                    metric='cosine',
                    spec=ServerlessSpec(cloud='aws', region='us-east-1')
                )
            except Exception as e:
                print(f"ERROR creating index: {e}")
                # Try without spec (for compatibility)
                try:
                    pinecone_client.create_index(
                        name=PINECONE_INDEX_NAME,
                        dimension=VECTOR_SIZE,
                        metric='cosine'
                    )
                except Exception as e2:
                    print(f"ERROR: Could not create index: {e2}")
                    return False
            
            print(f"SUCCESS: Index '{PINECONE_INDEX_NAME}' created successfully")
            return True
            
    except Exception as e:
        print(f"ERROR: Failed to setup Pinecone: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Pinecone Setup Script")
    print(f"API Key: {PINECONE_API_KEY[:20]}...")
    print(f"Index Name: {PINECONE_INDEX_NAME}")
    
    success = setup_pinecone()
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS: Pinecone setup completed successfully!")
        print("=" * 60)
        print("\nNext step: Run process_personal_auto_docs.py to add documents")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("ERROR: Pinecone setup failed!")
        print("=" * 60)
        sys.exit(1)


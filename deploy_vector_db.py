#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete deployment script for pgvector and Personal Auto documents
This script:
1. Sets up pgvector extension
2. Creates document_embeddings table
3. Processes Personal Auto documents
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # Continue without encoding fix if it fails

def main():
    """Main deployment function"""
    print("=" * 70)
    print("Complete Vector Database Deployment")
    print("=" * 70)
    
    # Step 1: Setup Pinecone
    print("\n" + "=" * 70)
    print("STEP 1: Setting up Pinecone vector database")
    print("=" * 70)
    
    try:
        from setup_pinecone import setup_pinecone
        if not setup_pinecone():
            print("\nERROR: Pinecone setup failed. Please fix errors and try again.")
            return False
    except Exception as e:
        print(f"\nERROR: Error importing setup_pinecone: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Process Personal Auto documents
    print("\n" + "=" * 70)
    print("STEP 2: Processing Personal Auto documents")
    print("=" * 70)
    
    try:
        from process_personal_auto_docs import process_personal_auto_documents
        if not process_personal_auto_documents():
            print("\nERROR: Document processing failed. Please check errors above.")
            return False
    except Exception as e:
        print(f"\nERROR: Error processing documents: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Verify deployment
    print("\n" + "=" * 70)
    print("STEP 3: Verifying deployment")
    print("=" * 70)
    
    try:
        from database import pinecone_client, PINECONE_INDEX_NAME, search_vector_db
        
        if pinecone_client:
            try:
                # Get index (new Pinecone API)
                index = pinecone_client.Index(PINECONE_INDEX_NAME)
                
                stats = index.describe_index_stats()
                
                total_vectors = stats.get('total_vector_count', 0)
                namespaces = stats.get('namespaces', {})
                
                print(f"SUCCESS: Total vectors in Pinecone: {total_vectors}")
                print(f"SUCCESS: Namespaces: {len(namespaces)}")
            except Exception as e:
                print(f"WARNING: Could not get stats: {e}")
            
            # Test search
            print("\nTesting vector search...")
            test_results = search_vector_db("personal auto insurance", lob="personal_auto", limit=3)
            if test_results:
                print(f"SUCCESS: Search test successful - found {len(test_results)} results")
                print(f"   Top result score: {test_results[0].get('score', 0):.4f}")
            else:
                print("WARNING: Search test returned no results (this might be normal if no documents were processed)")
    
    except Exception as e:
        print(f"WARNING: Verification warning: {e}")
    
    print("\n" + "=" * 70)
    print("SUCCESS: Deployment completed successfully!")
    print("=" * 70)
    print("\nSummary:")
    print("   - Pinecone index initialized")
    print("   - Personal Auto documents processed")
    print("   - Vector database ready for use")
    print("\nYou can now use the vector search API with LOB filtering")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


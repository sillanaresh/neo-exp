#!/usr/bin/env python3
"""Test script to verify Pinecone data"""

from app.vector_store import get_vector_store
from app.config import settings

def main():
    print("Connecting to Pinecone...")
    vector_store = get_vector_store()

    print("\n=== Index Statistics ===")
    stats = vector_store.index.describe_index_stats()
    print(f"Total vectors: {stats.total_vector_count}")
    print(f"Namespaces: {stats.namespaces}")
    print(f"Dimension: {stats.dimension if hasattr(stats, 'dimension') else 'N/A'}")

    print("\n=== Testing Search ===")
    query = "authentication"
    results = vector_store.search(query, top_k=3)
    print(f"Search query: '{query}'")
    print(f"Results found: {len(results)}")

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Document: {result.get('document_name', 'N/A')}")
        print(f"  Score: {result.get('score', 0):.4f}")
        print(f"  Text preview: {result.get('text', '')[:100]}...")

    print("\n=== Pinecone UI Access ===")
    print(f"Visit: https://app.pinecone.io/")
    print(f"Look for index: neo-knowledge")
    print(f"Your API key starts with: {settings.PINECONE_API_KEY[:10]}...")

if __name__ == "__main__":
    main()

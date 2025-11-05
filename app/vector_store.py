from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from app.config import settings
import time
from typing import List, Dict, Any
import hashlib

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        self._initialize_index()

    def _initialize_index(self):
        """Initialize or connect to existing Pinecone index"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            print(f"Creating new index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)

        # Get the index host URL to avoid 'Malformed domain' errors
        index_info = self.pc.describe_index(self.index_name)
        index_host = index_info.host

        # Connect using host URL instead of name
        self.index = self.pc.Index(host=index_host)
        print(f"Connected to index: {self.index_name} (host: {index_host})")

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding using OpenAI"""
        response = self.openai_client.embeddings.create(
            input=text,
            model=settings.EMBEDDING_MODEL
        )
        return response.data[0].embedding

    def add_documents(self, chunks: List[Dict[str, Any]], document_name: str):
        """Add document chunks to Pinecone"""
        vectors = []

        for i, chunk in enumerate(chunks):
            # Create unique ID for each chunk
            chunk_id = hashlib.md5(f"{document_name}_{i}_{chunk['text'][:50]}".encode()).hexdigest()

            # Create embedding
            embedding = self.create_embedding(chunk['text'])

            # Prepare metadata
            metadata = {
                'text': chunk['text'],
                'document_name': document_name,
                'chunk_index': i,
                **chunk.get('metadata', {})
            }

            vectors.append({
                'id': chunk_id,
                'values': embedding,
                'metadata': metadata
            })

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

        print(f"Added {len(vectors)} chunks from {document_name} to Pinecone")
        return len(vectors)

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if top_k is None:
            top_k = settings.TOP_K_RESULTS

        # Create query embedding
        query_embedding = self.create_embedding(query)

        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                'text': match.metadata.get('text', ''),
                'document_name': match.metadata.get('document_name', ''),
                'score': match.score,
                'metadata': match.metadata
            })

        return formatted_results

    def list_documents(self) -> dict:
        """List all unique documents in the index"""
        stats = self.index.describe_index_stats()

        # Extract total vectors
        total_count = stats.total_vector_count if hasattr(stats, 'total_vector_count') else 0

        # Convert namespaces to simple dict
        namespaces_data = {}
        if hasattr(stats, 'namespaces') and stats.namespaces:
            for ns_name, ns_obj in stats.namespaces.items():
                if hasattr(ns_obj, 'vector_count'):
                    namespaces_data[ns_name] = ns_obj.vector_count
                else:
                    namespaces_data[ns_name] = 0

        # Get unique document names by querying with dummy vector
        # Create a dummy query to fetch some results
        try:
            dummy_query = [0.0] * 1536  # Empty embedding
            results = self.index.query(
                vector=dummy_query,
                top_k=10000,  # Get many results to find all unique docs
                include_metadata=True
            )

            # Extract unique document names
            document_names = set()
            document_chunks = {}
            for match in results.matches:
                doc_name = match.metadata.get('document_name', 'Unknown')
                document_names.add(doc_name)
                # Count chunks per document
                document_chunks[doc_name] = document_chunks.get(doc_name, 0) + 1

            # Convert to sorted list with chunk counts
            documents_list = [
                {'name': name, 'chunks': document_chunks.get(name, 0)}
                for name in sorted(document_names)
            ]
        except Exception as e:
            print(f"Error fetching document list: {e}")
            documents_list = []

        return {
            'total_vectors': total_count,
            'total_files': len(documents_list),
            'namespaces': namespaces_data,
            'documents': documents_list
        }

    def delete_document(self, document_name: str):
        """Delete all chunks of a specific document"""
        # This would require fetching all IDs with this document_name
        # For now, we'll implement a simple version
        # In production, you'd want to maintain a separate index of document IDs
        print(f"Delete operation for {document_name} - requires fetching IDs")
        # TODO: Implement proper deletion by querying and deleting matching IDs

def get_vector_store():
    """
    Create a fresh VectorStore instance each time.
    This ensures we always have the latest index connection,
    avoiding 'Malformed domain' errors when indexes are deleted/recreated.
    """
    return VectorStore()

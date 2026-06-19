# core/memory_engine.py
import os
import uuid
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime
from core.config import PROJECT_ROOT

class MemoryEngine:
    """
    Vector memory engine using SentenceTransformers and ChromaDB.
    Stores and retrieves semantic memories for context injection.
    """
    
    def __init__(self, collection_name="syna_memory"):
        # Load embedding model (may take a few seconds on first run)
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB with project-relative path
        chroma_path = os.path.join(PROJECT_ROOT, "memory", "chroma_db")
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(collection_name)
        print(f"Connected to collection '{collection_name}'. Documents: {self.collection.count()}")

    def remember(self, text, metadata=None):
        """
        Converts text to vector and stores it in the vector database.
        Returns True on success.
        """
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Generate embedding
        embedding = self.model.encode([text])[0]
        
        # Add to collection with auto-generated UUID
        doc_id = str(uuid.uuid4())
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
        return True
    
    def recall(self, query, top_k=3):
        """
        Retrieves the most relevant memories for a given query.
        Returns ChromaDB results dict.
        """
        query_embedding = self.model.encode([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        return results
    
    def remember_context(self, query, top_k=3, max_distance=1.5):
        """
        Retrieves relevant memories and formats them for prompt injection.
        Returns a formatted string, or empty string if nothing relevant is found.
        """
        results = self.recall(query, top_k)
        documents = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]

        if not documents:
            return ""
        
        relevant_memories = []
        for doc, dist in zip(documents, distances):
            if dist <= max_distance:
                relevant_memories.append(f"- {doc}")

        if not relevant_memories:
            return ""
        
        return "Relevant memories:\n" + "\n".join(relevant_memories)
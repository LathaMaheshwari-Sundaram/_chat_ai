import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from config import config

# Initialize the ChromaDB client with persistent storage
# The path is retrieved from our config file
client = PersistentClient(path=config.CHROMA_PATH)

# Get or create a collection for our data lineage documents
# We use a meaningful name for our collection
collection = client.get_or_create_collection(name="data_lineage_docs")

# Load the local embedding model (SentenceTransformers)
# This model runs on your machine and does not need an API key
model = SentenceTransformer(config.EMBEDDING_MODEL)

def add_documents(docs):
    """
    Takes a list of document dictionaries and stores them in ChromaDB.
    Each doc should be: {"id": "...", "text": "..."}
    """
    # Extract texts and IDs from the input list
    ids = [doc["id"] for doc in docs]
    texts = [doc["text"] for doc in docs]
    
    # Generate embeddings for all text chunks at once
    # These vectors represent the meaning of the sentences
    embeddings = model.encode(texts).tolist()
    
    # Add the documents and their vectors to the vector database
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings
    )
    print(f"Added {len(docs)} documents to ChromaDB.")

def search(query, n=3):
    """
    Searches ChromaDB for the most relevant text chunks based on the query.
    Returns a list of the top n matching documents.
    """
    # Generate the vector for the user's question
    query_vector = model.encode([query]).tolist()
    
    # Perform the similarity search in our collection
    # It finds pieces of text that are 'close' in meaning to the question
    results = collection.query(
        query_embeddings=query_vector,
        n_results=n
    )
    
    # Return the list of matching document texts
    return results["documents"][0]

def get_collection_count():
    """
    Returns the total number of documents currently stored in the collection.
    """
    return collection.count()

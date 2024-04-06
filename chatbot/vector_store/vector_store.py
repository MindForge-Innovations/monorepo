"""
This module initializes the ChroMaDB vector store with API endpoint data.
"""

import joblib
import chromadb
from pathlib import Path
import pandas as pd
import os
import time
import requests


def initialize_vector_store():
    """
    Initialize the ChroMaDB vector store with the given data.

    Parameters
    ----------
    data_path : str
        The path to the data file containing API specifications and embeddings.
    collection_name : str
        The name of the collection to create or update in ChroMaDB.

    Returns
    -------
    None
    """
    # Create a client to interact with the ChroMaDB server
    chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    
    # Load the precomputed embeddings and API data
    spec_embeddings = joblib.load(Path(DATA_PATH))

    # Create or get the collection
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    # Extract documents, embeddings, metadatas, and ids from the data
    df = pd.DataFrame(spec_embeddings)
    documents = df.documents.tolist()
    embeddings = df.embeddings.tolist()
    metadatas = df.metadatas.tolist()
    ids = df.id.apply(str).to_list()

    # Add the data to the collection
    collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)

        
if __name__ == "__main__":
    DATA_PATH = os.getenv("DATA_PATH", "embeddings.joblib")
    CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8000"))  # Default port
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "api_endpoints")

    initialize_vector_store()

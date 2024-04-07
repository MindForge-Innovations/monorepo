"""
This module provides a FastAPI service for selecting API endpoints based on a given prompt,
leveraging OpenAI's embeddings and a ChroMaDB vector store.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import chromadb
from openai import OpenAI
import os


import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

import warnings
warnings.filterwarnings("ignore")

class OpenAIManager:
    """
    Manages the connection and interactions with the OpenAI API.
    """
    def __init__(self, user_id: str):
        """
        Initialize the OpenAI manager with the provided API key.

        Parameters
        ----------
        api_key : str
            The API key for authenticating with the OpenAI service.
        """
        self.api_key = self._get_api_key(user_id)
        self.client = OpenAI(api_key=self.api_key)

    def _get_api_key(self, user_id:str) -> str:
        """
        Retrieve the API key for authenticating with the OpenAI service.

        Returns
        -------
        str
            The API key.
        """
        # secret_name = f"openai-apikey-{user_id}"
        # api_key = os.popen(f"kubectl get secret {secret_name} -o jsonpath='{{.data.api_key}}' | base64 --decode").read().strip()

        # if not api_key:
        #     raise HTTPException(status_code=404, detail="API key not found for user")
        return os.getenv('OPENAI_API_KEY')

    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> list:
        """
        Generate an embedding for the given text using the specified model.

        Parameters
        ----------
        text : str
            The text to embed.
        model : str, optional
            The model to use for embedding.

        Returns
        -------
        list
            The embedding vector.
        """
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model=model).data[0].embedding

class SimilarAPIsRequest(BaseModel):
    prompt: str
    user_id: str
    k: Optional[int] = 10

class DocumentRequest(BaseModel):
    id: str

app = FastAPI()

chroma_client = None

@app.on_event("startup")
async def startup_event():
    global chroma_client
    host = os.getenv('CHROMA_SERVER_HOST', 'chromadb')  # Default to 'chromadb'
    port = os.getenv('CHROMA_SERVER_HTTP_PORT', '8000')  # Default to '8000'
    bearer_token = os.getenv('BEARER_TOKEN')  # No default, should be provided
    if not bearer_token:
        raise Exception("Bearer token for ChromaDB is not set")

    chroma_client = chromadb.HttpClient(
        host=host,
        port=port,
        headers={"Authorization": f"Bearer {bearer_token}"}
    )
    # import joblib
    # from pathlib import Path
    # import pandas as pd
    # DATA_PATH = '../data/embeddings.joblib'
    # COLLECTION_NAME = 'api_endpoints'
    # spec_embeddings = joblib.load(Path(DATA_PATH))
    # chroma_client = chromadb.HttpClient(
    #     host='0.0.0.0',
    #     port='8000',
    # )
    # collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    # # Extract documents, embeddings, metadatas, and ids from the data
    # df = pd.DataFrame(spec_embeddings)
    # documents = df.documents.tolist()
    # embeddings = df.embeddings.tolist()
    # metadatas = df.metadatas.tolist()
    # ids = df.id.apply(str).to_list()

    # # Add the data to the collection
    # collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)


@app.get("/status/")
async def get_status():
    """
    Check the status of the API.

    Returns
    -------
    dict
        A dictionary containing the status of the API.
    """
    return {"status": "API is running"}


@app.post("/get_similar_apis/")
async def get_similar_apis(request: SimilarAPIsRequest):
    """
    Retrieve similar APIs based on the given prompt.

    Parameters
    ----------
    request : SimilarAPIsRequest
        The request object containing the prompt, user_id, and number of results.

    Returns
    -------
    dict
        A dictionary containing the similar documents and their distances.
    """

    openai_manager = OpenAIManager(request.user_id)
    embedding = openai_manager.get_embedding(request.prompt)
    collection = chroma_client.get_collection(name="api_endpoints")
    results = collection.query(query_embeddings=[embedding], n_results=request.k)
    return {"documents": results['documents'], "distances": results['distances']}

@app.post("/get_document/")
async def get_document(request: DocumentRequest):
    """
    Retrieve a specific document by its ID.

    Parameters
    ----------
    request : DocumentRequest
        The request object containing the document ID.

    Returns
    -------
    dict
        The requested document if found, otherwise raises an HTTP 404 error.
    """
    collection = chroma_client.get_collection(name="api_endpoints")
    document = collection.get(id=request.id)
    if document:
        return document
    else:
        raise HTTPException(status_code=404, detail="Document not found")

"""
This module provides a FastAPI service for selecting API endpoints based on a given prompt,
leveraging OpenAI's embeddings and a ChroMaDB vector store.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import chromadb
from openai import OpenAI

class OpenAIManager:
    """
    Manages the connection and interactions with the OpenAI API.
    """
    def __init__(self, api_key: str):
        """
        Initialize the OpenAI manager with the provided API key.

        Parameters
        ----------
        api_key : str
            The API key for authenticating with the OpenAI service.
        """
        self.client = OpenAI(api_key=api_key)

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

app = FastAPI()

class SimilarAPIsRequest(BaseModel):
    prompt: str
    openai_key: str
    k: Optional[int] = 10

class DocumentRequest(BaseModel):
    id: str

@app.post("/get_similar_apis/")
async def get_similar_apis(request: SimilarAPIsRequest):
    """
    Retrieve similar APIs based on the given prompt.

    Parameters
    ----------
    request : SimilarAPIsRequest
        The request object containing the prompt, OpenAI key, and number of results.

    Returns
    -------
    dict
        A dictionary containing the similar documents and their distances.
    """
    openai_manager = OpenAIManager(api_key=request.openai_key)
    embedding = openai_manager.get_embedding(request.prompt)
    collection = chromadb.Client().get_collection(name="api_endpoints")
    results = collection.query(query_embeddings=[embedding], k=request.k)
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
    collection = chromadb.Client().get_collection(name="api_endpoints")
    document = collection.get(id=request.id)
    if document:
        return document
    else:
        raise HTTPException(status_code=404, detail="Document not found")

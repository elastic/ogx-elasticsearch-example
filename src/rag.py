# RAG (Retrieval-Augmented Generation) example using OGX

import os
import json
import urllib.request
import time
from pathlib import Path
from dotenv import load_dotenv
from ogx_client import Agent, AgentEventLogger, OgxClient
from io import BytesIO

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# ── Connect to OGX ──────────────────────────────────────────────────
client = OgxClient(base_url=os.getenv('OGX_URL', 'http://localhost:8321'))

VECTOR_STORE_NAME = os.getenv('ELASTICSEARCH_INDEX_NAME')
INFERENCE_MODEL = os.getenv('INFERENCE_MODEL')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

if not VECTOR_STORE_NAME or not INFERENCE_MODEL or not EMBEDDING_MODEL:
    raise ValueError("Please set ELASTICSEARCH_INDEX_NAME, INFERENCE_MODEL, and EMBEDDING_MODEL in the .env file")

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

# ── Create the vector store ────────────────────────────────────
def create_vector_store():
    vector_list = client.vector_stores.list()
    for store in vector_list.data:
        if store.name == VECTOR_STORE_NAME:
            print(f'Index already exists: {VECTOR_STORE_NAME}')
            return store.id

    print(f'Creating vector store: {VECTOR_STORE_NAME} ...', end=' ')

    vector_store = client.vector_stores.create(
        name=VECTOR_STORE_NAME,
        extra_body={
            "provider_id": "elasticsearch",
            "embedding_model": EMBEDDING_MODEL,
        }
    )
    print(f'done.')

    print("Store the file in vector store")
    # Read the PDF files in /data
    for file_path in Path(DATA_DIR).glob("*.pdf"):
        print(f'Uploading {file_path.name} ...', end=' ')
        with open(file_path, 'rb') as f:
            try:
                file_info = client.files.create(file=f, purpose="assistants")
                client.vector_stores.files.create(
                    vector_store_id=vector_store.id, file_id=file_info.id
                )
                print(f'Uploaded {file_path.name} with file ID: {file_info.id}, attached to vector store with ID: {vector_store.id}')
            except Exception as e:
                # Delete the vector_store if file upload fails to avoid orphaned vector stores
                client.vector_stores.delete(vector_store.id)
                print(f'Failed to upload {file_path.name}: {e}')
                raise e
        print(f'done.')
    return vector_store.id

if __name__ == '__main__':
    vector_store_id = create_vector_store()
    print(f'Vector store ID: {vector_store_id}')
    
    # Create agent with file_search tool (client-side wrapper)
    agent = Agent(
        client,
        model=INFERENCE_MODEL,
        instructions="You are a helpful assistant",
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],  # Agent searches this automatically
            }
        ],
    )

    # Create the session once — reusing it across turns gives the agent memory
    session_id = agent.create_session("my_session")

    while True:
        question = input("\nAsk a question about EU documents (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break

        # Just ask - agent handles retrieval automatically
        response = agent.create_turn(
            messages=[{"role": "user", "content": question}],
            session_id=session_id,
            stream=True,
        )

        for log in AgentEventLogger().log(response):
            print(log, end="")

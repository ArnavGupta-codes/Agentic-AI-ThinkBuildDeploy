import PyPDF2
from google import genai
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import transformers
import chromadb
import numpy as np
from dotenv import load_dotenv
transformers.logging.set_verbosity_error()

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

gemini_client = genai.Client(api_key=api_key)

embed_model = SentenceTransformer("intfloat/e5-base-v2")
PDF_PATH = "./Inductions_Catalogue.pdf"

client = chromadb.PersistentClient(path="./RAG_db")

def chunk_pdf(pdf_path: str, chunk_size=30):
    chunks = []
    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        current_chunk = ""
        
        for page in pdf.pages:
            text = page.extract_text()
            words = text.split()
            
            for word in words:
                current_chunk += word + " "
                if len(current_chunk.split()) >= chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
    
    return chunks

def embed(chunks, embed_model):
    embeddings = embed_model.encode(chunks, show_progress_bar = True)
    shape = embeddings.shape
    print(shape)
    return embeddings 

def create_vector_store(embeddings, chunks, client):
    collection = client.get_or_create_collection(name="RAG_db")
    collection.add(
        embeddings = embeddings.tolist(),
        documents = chunks,
        ids = [f"chunk{i}" for i in range(1, len(chunks)+1)]
    )
    print("Added embeddings successfully!")

def retrieve_relevant_chunks(query, embedding_model, client, top_k=20):
    collection = client.get_collection(name = "RAG_db")
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results = top_k
    )
    relevant_chunks = results['documents'][0]
    return relevant_chunks


def generate_answer(query, relevant_chunks, history_context=None):
        context = '\n'.join(relevant_chunks)
        chat_history = f"\nChat History:\n{history_context}\n---\n" if history_context else ""

        prompt_template = f"""
    Answer the question based only on the provided context and the chat history.
    If you cannot answer the question from the context, say "I'm sorry, I don't know".

    Context:
    ---
    {context}
    ---
    {chat_history}
    Question:
    ---
    {query}
    ---
    """

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_template
        )

        return response.text




if __name__ == "__main__":
    chunks = chunk_pdf(pdf_path=PDF_PATH, chunk_size=30)
    embeddings = embed(chunks=chunks, embed_model=embed_model)
    create_vector_store(embeddings=embeddings, chunks=chunks, client=client)
    query = input("Enter your query: ")
    retrieved_relevant_chunks = retrieve_relevant_chunks(query=query, embedding_model=embed_model, client=client)
    augmented_response = generate_answer(query=query, relevant_chunks=retrieved_relevant_chunks)
    print(augmented_response)
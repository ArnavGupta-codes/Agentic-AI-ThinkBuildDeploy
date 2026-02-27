from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

# From Lecture 3
embed_model = SentenceTransformer("intfloat/e5-base-v2")
client = chromadb.PersistentClient(path="./RAG_db")

memory = ConversationBufferWindowMemory(k=3)

def retrieve_with_memory(query: str, memory: ConversationBufferWindowMemory):
    """RAG retrieval + conversation memory"""
    
    # 1. Retrieve from vector store (Lecture 3)
    collection = client.get_collection(name="RAG_db")
    query_embedding = embed_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    context = '\n'.join(results['documents'][0])
    
    # 2. Get conversation history
    history = memory.load_memory_variables({})
    chat_history = history.get('history', '')
    
    # 3. Combine context + history
    prompt = f"""
Answer using BOTH the document context AND the conversation history.

Document Context:
---
{context}
---

Conversation History:
---
{chat_history}
---

Question: {query}
"""
    
    response = llm.predict(prompt)
    
    # 4. Save to memory
    memory.save_context({"input": query}, {"output": response})
    
    return response

print("=" * 50)
print("RAG + MEMORY (Lecture 3 + Lecture 4)")
print("=" * 50)

# Check if vector store exists
try:
    client.get_collection(name="RAG_db")
    
    response1 = retrieve_with_memory("What inductions are available?", memory)
    print(f"\nAssistant: {response1}\n")
    
    response2 = retrieve_with_memory("Can you summarize that?", memory)
    print(f"\nAssistant: {response2}\n")
    
except Exception as e:
    print("ERROR: Run the Lecture 3 code first to create the vector store!")
    print(f"Details: {e}")

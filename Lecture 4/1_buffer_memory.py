# 1_buffer_memory.py - Fixed with Stable Model

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- CONFIGURATION ---
# We use "gemini-pro" as it is the most stable model ID.
MODEL_NAME = "gemini-2.5-flash" 
# ---------------------

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

print(f"Initializing with model: {MODEL_NAME}...")

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=api_key,
    temperature=0
)

# Initialize Memory Store
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

def run_interaction():
    print("=" * 50)
    print(f"BUFFER MEMORY DEMO ({MODEL_NAME})")
    print("=" * 50)

    session_id = "user_123"
    config = {"configurable": {"session_id": session_id}}

    try:
        # Conversation 1
        user_input = "Hi, my name is Arnav!"
        print(f"\nUser: {user_input}")
        response1 = chain_with_history.invoke({"input": user_input}, config=config)
        print(f"Assistant: {response1.content}")

        # Conversation 2
        user_input = "What is 2 + 2?"
        print(f"\nUser: {user_input}")
        response2 = chain_with_history.invoke({"input": user_input}, config=config)
        print(f"Assistant: {response2.content}")

        # Conversation 3 (Recall)
        user_input = "What is my name?"
        print(f"\nUser: {user_input}")
        response3 = chain_with_history.invoke({"input": user_input}, config=config)
        print(f"Assistant: {response3.content}")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Run 'check_models.py' (provided above) to see your valid model names.")
        print("2. Paste a valid name into the MODEL_NAME variable in this script.")

if __name__ == "__main__":
    run_interaction()
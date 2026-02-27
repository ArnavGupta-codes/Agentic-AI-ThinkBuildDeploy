from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

# NOTE: Requires Redis running on localhost:6379
# Start Redis: docker run -d -p 6379:6379 redis
# Or install locally: brew install redis (Mac) / apt-get install redis (Linux)

SESSION_ID = "user_123"

# 1. Connect to Redis
try:
    message_history = RedisChatMessageHistory(
        url="redis://localhost:6379/0",
        session_id=SESSION_ID  # Unique per user
    )
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    print("Please ensure Redis is running on localhost:6379")
    exit(1)

# 2. Pass history backend to Memory
memory = ConversationBufferMemory(
    chat_memory=message_history
)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

print("=" * 50)
print(f"REDIS PERSISTENCE - Session: {SESSION_ID}")
print("=" * 50)

# First run
response1 = conversation.predict(input="My favorite color is blue")
print(f"\nAssistant: {response1}")

# Simulate restarting the Python script
print("\n[Simulating server restart...]\n")

# Create new conversation instance (but same session_id)
message_history_new = RedisChatMessageHistory(
    url="redis://localhost:6379/0",
    session_id=SESSION_ID
)

memory_new = ConversationBufferMemory(chat_memory=message_history_new)
conversation_new = ConversationChain(llm=llm, memory=memory_new)

# Should remember previous chat
response2 = conversation_new.predict(input="What's my favorite color?")
print(f"\nAssistant: {response2}")

print("\n" + "=" * 50)
print("PERSISTED HISTORY FROM REDIS")
print("=" * 50)
print(memory_new.load_memory_variables({}))

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

# Keep only last K=2 interactions
memory = ConversationBufferWindowMemory(k=2)

# Create a conversation chain with memory
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

print("=" * 50)
print("WINDOW MEMORY DEMO - Sliding Window (K=2)")
print("=" * 50)

msgs = [
    "My name is Arnav",
    "I love pizza",
    "I have a dog named Bruno",
    "What's my name?",  # Should forget (because it was msg #1, and we are now at msg #4)
    "What do I love?",  # Should remember (within last 2)
]

for msg in msgs:
    print(f"\nUser: {msg}")
    response = conversation.predict(input=msg)
    print(f"Assistant: {response}")

print("\n" + "=" * 50)
print("FINAL MEMORY STATE (only last 2 exchanges)")
print("=" * 50)
print(memory.load_memory_variables({}))
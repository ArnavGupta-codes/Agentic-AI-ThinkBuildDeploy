from langchain.memory import ConversationSummaryBufferMemory
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

# Hybrid: Recent messages raw + Old messages summarized
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=100  # When history exceeds this, summarize old messages
)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

print("=" * 50)
print("SUMMARY BUFFER MEMORY - Production Pattern")
print("=" * 50)

messages = [
    "My dog Bruno is a golden retriever",
    "He loves chicken",
    "He's 3 years old",
    "What breed is my dog?",  # Should use summary
    "What does he eat?",  # Should use recent buffer
]

for msg in messages:
    print(f"\nUser: {msg}")
    response = conversation.predict(input=msg)
    print(f"Assistant: {response}")

print("\n" + "=" * 50)
print("HYBRID MEMORY STATE")
print("=" * 50)
memory_vars = memory.load_memory_variables({})
print(f"Summary: {memory_vars.get('history', 'N/A')}")

from langchain.memory import ConversationEntityMemory
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

# Extracts entities (people, places, things) and facts about them
memory = ConversationEntityMemory(llm=llm)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

print("=" * 50)
print("ENTITY MEMORY - Structured Knowledge Graph")
print("=" * 50)

response1 = conversation.predict(input="My dog Bruno is a golden retriever who loves chicken")
print(f"\nAssistant: {response1}\n")

response2 = conversation.predict(input="I also have a cat named Whiskers")
print(f"\nAssistant: {response2}\n")

# Months later...
response3 = conversation.predict(input="What kind of dog is Bruno?")
print(f"\nAssistant: {response3}\n")

print("\n" + "=" * 50)
print("EXTRACTED ENTITIES AND FACTS")
print("=" * 50)
print(memory.entity_store.store)

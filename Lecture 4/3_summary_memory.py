from langchain.memory import ConversationSummaryMemory
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

# Uses LLM to summarize conversation history
memory = ConversationSummaryMemory(llm=llm)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

print("=" * 50)
print("SUMMARY MEMORY DEMO - LLM Compression")
print("=" * 50)

response1 = conversation.predict(input="I'm planning a trip to Italy. I love pasta and art.")
print(f"\nAssistant: {response1}\n")

response2 = conversation.predict(input="I'll be there for 10 days in June.")
print(f"\nAssistant: {response2}\n")

response3 = conversation.predict(input="What should I pack?")
print(f"\nAssistant: {response3}\n")

# View compressed summary
print("\n" + "=" * 50)
print("COMPRESSED SUMMARY (not raw messages)")
print("=" * 50)
print(memory.load_memory_variables({}))

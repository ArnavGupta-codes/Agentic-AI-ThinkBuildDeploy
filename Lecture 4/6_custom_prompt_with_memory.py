from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

# The magic placeholder where memory is injected
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful customer support agent for an e-commerce store."),
    MessagesPlaceholder(variable_name="history"),  # Memory goes here
    ("human", "{input}")
])

memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True
)

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

print("=" * 50)
print("CUSTOM PROMPT + MEMORY INJECTION")
print("=" * 50)

response1 = chain.predict(input="I ordered item #12345")
print(f"\nAssistant: {response1}\n")

response2 = chain.predict(input="Where is it?")
print(f"\nAssistant: {response2}\n")

response3 = chain.predict(input="What was my order number again?")
print(f"\nAssistant: {response3}")

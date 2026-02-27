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

print("=" * 50)
print("TOKEN ECONOMICS DEMO")
print("=" * 50)

# Simulate a 50-message conversation
fake_history = []
for i in range(50):
    fake_history.append(f"User: Message {i}")
    fake_history.append(f"Assistant: Response {i}")

history_text = "\n".join(fake_history)

prompt_without_history = "What is 2+2?"
prompt_with_history = f"{history_text}\n\n{prompt_without_history}"

print(f"Prompt WITHOUT history: {len(prompt_without_history)} chars")
print(f"Prompt WITH 50-msg history: {len(prompt_with_history)} chars")
print(f"\nToken multiplication: {len(prompt_with_history) / len(prompt_without_history):.1f}x")

print("\n💡 This is why we compress memory!")
print("   - Buffer: Perfect recall, but grows forever")
print("   - Window: Fixed size, but forgets early messages")
print("   - Summary: Compressed, but loses detail")
print("   - Summary Buffer: Best of both (PRODUCTION CHOICE)")

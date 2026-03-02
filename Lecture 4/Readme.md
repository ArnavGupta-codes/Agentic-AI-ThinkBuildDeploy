# Lecture 4: State & Memory - Code Examples

## Overview
This directory contains practical implementations of the memory concepts from Lecture 4: **State & Memory - From Stateless LLMs to Context-Aware Agents with LangChain**.

Notes: https://docs.google.com/presentation/d/1guHqwU8mhofFJWsvGTuSDhb8EoUqthEhpqdMsoh3iLo/edit?usp=sharing

## Prerequisites
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```
For all codes except 5th use .venv/bin/<File Name> to run it
Also if you exhaust your api keys while running these create a new one and retry, all codes should be working perfectly fine

3. For Redis examples (optional):
```bash
# Using Docker
docker run -d -p 6379:6379 redis

# Or install locally
brew install redis  # Mac
sudo apt-get install redis  # Linux
```

## Files Overview

### Basic Memory Types

**1_buffer_memory.py** - ConversationBufferMemory
- Stores ALL messages (unbounded growth)
- Perfect recall
- ⚠️ Will eventually exceed context window
- **Use case**: Short sessions, prototyping

**2_window_memory.py** - ConversationBufferWindowMemory
- Keeps only last K interactions (sliding window)
- Fixed memory size
- ⚠️ Forgets early conversation
- **Use case**: Chat sessions with natural boundaries

**3_summary_memory.py** - ConversationSummaryMemory
- LLM compresses history into summary
- Infinite length conversations
- ⚠️ Loses exact details
- **Use case**: Long support tickets, therapy bots

**4_summary_buffer_memory.py** - ConversationSummaryBufferMemory ⭐
- **PRODUCTION PATTERN**: Recent messages raw + old messages summarized
- Best of buffer + summary
- **Use case**: Production chatbots (Replika, Character.ai)

### Advanced Patterns

**5_redis_persistence.py** - Production Persistence
- Survives server restarts
- Multi-user session management
- **Use case**: Any production system

**6_custom_prompt_with_memory.py** - Manual Control
- Shows `MessagesPlaceholder` injection
- Custom system prompts + memory
- **Use case**: Specialized agents (support, sales)

**7_memory_with_rag.py** - Integration with Lecture 3
- Combines RAG retrieval + conversation memory
- "Can you summarize that?" now works!
- **Use case**: Document Q&A with follow-ups

**8_entity_memory.py** - Knowledge Graphs
- Extracts entities (people, places, facts)
- Long-term factual recall
- **Use case**: Personal assistants, CRM agents

**9_token_limits_demo.py** - Economics
- Visualizes token cost explosion
- Explains WHY compression matters

## Running Examples

Start with the basics:
```bash
python 1_buffer_memory.py
python 2_window_memory.py
python 4_summary_buffer_memory.py  # Production pattern
```

Try persistence (requires Redis):
```bash
python 5_redis_persistence.py
```

Integrate with Lecture 3 RAG:
```bash
# First, ensure you ran Lecture 3 code to create vector store
python 7_memory_with_rag.py
```

## Key Takeaways from Lecture 4

### The Memory Stack
```
User Input → Backend (FastAPI/LangChain) → Redis/Postgres → LLM
                ↓                              ↓
         Fetches History              Stores new messages
```

### Memory Type Decision Tree
- **Short sessions (<10 messages)**: `ConversationBufferMemory`
- **Bounded conversations**: `ConversationBufferWindowMemory(k=5)`
- **Long conversations**: `ConversationSummaryBufferMemory` ⭐
- **Permanent facts**: `ConversationEntityMemory`

### Production Checklist
Use `ConversationSummaryBufferMemory`  
Store in Redis/Postgres (not in-memory)  
Use session IDs (UUIDs per user)  
Set TTL (expire old sessions)  
Monitor token usage  

## Common Pitfalls
Using `ConversationBufferMemory` in production (unbounded)  
Not persisting memory (loses data on restart)  
Forgetting to call `memory.save_context()` manually  
Mixing memory types without understanding trade-offs  

## Next Steps
- Lecture 5: Agentic AI Systems (Tools + Memory + RAG)
- Experiment with hybrid strategies (e.g., Entity + Summary)
- Build a chatbot with persistent memory

## References
- [LangChain Memory Docs](https://python.langchain.com/docs/modules/memory/)
- [Redis Chat History](https://python.langchain.com/docs/integrations/memory/redis_chat_message_history)
- [MemGPT Paper](https://arxiv.org/abs/2310.08560)

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.runners import Runner
from google.genai import types 
from typing import Optional, Dict, Any
from neo4j_for_adk import graphdb
from agent_module import response, make_agent_caller, create_hello_agent, llm, say_hello, say_goodbye, say_hello_stateful, say_goodbye_stateful

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.CRITICAL)

load_dotenv()

print("Libraries imported.")

# # Define a basic tool -- send a parameterized cypher query
# def say_hello(person_name: str) -> dict:
#     """Formats a welcome message to a named person. 

#     Args:
#         person_name (str): the name of the person saying hello

#     Returns:
#         dict: A dictionary containing the results of the query.
#               Includes a 'status' key ('success' or 'error').
#               If 'success', includes a 'query_result' key with an array of result rows.
#               If 'error', includes an 'error_message' key.
#     """
#     return graphdb.send_query("RETURN 'Hello to you, ' + $person_name AS reply",
#     {
#         "person_name": person_name
#     })

# # Example tool usage (optional test)
# print(say_hello("ABK"))

# Define the Cypher Agent
# hello_agent = Agent(
#     name="hello_agent_v1",
#     model=llm, # defined earlier in a variable
#     description="Has friendly chats with a user.",
#     instruction="""You are a helpful assistant, chatting with a user. 
#                 Be polite and friendly, introducing yourself and asking who the user is. 

#                 If the user provides their name, use the 'say_hello' tool to get a custom greeting.
#                 If the tool returns an error, inform the user politely. 
#                 If the tool is successful, present the reply.
#                 """,
#     tools=[say_hello], # Pass the function directly
# )

# print(f"Agent '{hello_agent.name}' created.")


greeting_subagent = Agent(
    model=llm,
    name="greeting_subagent_v1",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                "Use the 'say_hello' tool to generate the greeting. "
                "If the user provides their name, make sure to pass it to the tool. "
                "Do not engage in any other conversation or tasks.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
    tools=[say_hello],
)
print(f"Agent '{greeting_subagent.name}' created.")


farewell_subagent = Agent(
    model=llm, 
    name="farewell_subagent_v1",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
    tools=[say_goodbye],
)
print(f"Agent '{farewell_subagent.name}' created.")

root_agent = Agent(
    name="friendly_agent_team_v1",
    model=llm,
    description="The main coordinator agent. Delegates greetings/farewells to specialists.",
    instruction="""You are the main Agent coordinating a team. Your primary responsibility is to be friendly.
 
                You have specialized sub-agents: 
                1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. 
                2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. 

                Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. 
                If it's a farewell, delegate to 'farewell_agent'. 
                
                For anything else, respond appropriately or state you cannot handle it.
                """,
    tools=[], 
    sub_agents=[greeting_subagent, farewell_subagent]
)


print(f"Root Agent '{root_agent.name}' created with sub-agents: {[sa.name for sa in root_agent.sub_agents]}")

async def run_team_conversation():
    root_agent_caller = await make_agent_caller(root_agent)

    await root_agent_caller.call("Hello I'm ABK", True)

    await root_agent_caller.call("Thanks, bye!", True)

asyncio.run(run_team_conversation())

greeting_agent_stateful = Agent(
    model=llm,
    name="greeting_agent_stateful_v1",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
    description="Handles simple greetings and hellos using the 'say_hello_stateful' tool.",
    tools=[say_hello_stateful],
)
print(f"Agent '{greeting_agent_stateful.name}' redefined.")


farewell_agent_stateful = Agent(
    model=llm,
    name="farewell_agent_stateful_v1",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye_stateful' tool. Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye_stateful' tool.",
    tools=[say_goodbye_stateful],
)
print(f"Agent '{farewell_agent_stateful.name}' redefined.")

root_agent_stateful = Agent(
    name="friendly_team_stateful", # New version name
    model=llm,
    description="The main coordinator agent. Delegates greetings/farewells to specialists.",
    instruction="""You are the main Agent coordinating a team. Your primary responsibility is to be friendly.

                You have specialized sub-agents: 
                1. 'greeting_agent_stateful': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. 
                2. 'farewell_agent_stateful': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. 

                Analyze the user's query. If it's a greeting, delegate to 'greeting_agent_stateful'. If it's a farewell, delegate to 'farewell_agent_stateful'. 
                
                For anything else, respond appropriately or state you cannot handle it.
                """,
        tools=[],
        sub_agents=[greeting_agent_stateful, farewell_agent_stateful], # Include sub-agents
    )

print(f"Root Agent '{root_agent_stateful.name}' created using agents with stateful tools.")

async def run_stateful_conversation():
    root_stateful_caller = await make_agent_caller(root_agent_stateful)

    session = await root_stateful_caller.get_session()
    await root_stateful_caller.call("Hello, I'm ABK!")

    await root_stateful_caller.call("Thanks, bye!")

    session = await root_stateful_caller.get_session()

    print(f"\nFinal State: {session.state}")

asyncio.run(run_stateful_conversation())
# async def run_conversation():
#     hello_agent = create_hello_agent(llm)
#     hello_agent_caller = await make_agent_caller(hello_agent)
#     await hello_agent_caller.call("Hello I'm ABK")

#     await hello_agent_caller.call("I am excited")

# # Execute the conversation using await
# asyncio.run(run_conversation())
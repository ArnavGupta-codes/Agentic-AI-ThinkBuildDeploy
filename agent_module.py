from typing import Optional, Dict, Any
from xml.parsers.expat import model
from dotenv import load_dotenv
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types 
from neo4j_for_adk import graphdb


load_dotenv()

MODEL_GEMINI = "gemini/gemini-2.5-flash"


llm = LiteLlm(model=MODEL_GEMINI)

print(llm.llm_client.completion(model=llm.model, 
                                messages=[{"role": "user", 
                                           "content": "Are you ready?"}], 
                                tools=[]))

print("\nLLM is ready for use.")

neo4j_is_ready = graphdb.send_query("RETURN 'Neo4j is Ready!' as message")

print(neo4j_is_ready)

# TOOLS

def say_hello(person_name: str) -> dict:
    """Formats a welcome message to a named person."""
    return graphdb.send_query(
        "RETURN 'Hello to you, ' + $person_name AS reply",
        {"person_name": person_name},
    )


def say_goodbye() -> dict:
    """Provides a simple farewell message to conclude the conversation."""
    return graphdb.send_query("RETURN 'Goodbye from Cypher!' as farewell")

def say_hello_stateful(user_name:str, tool_context:ToolContext):
    """Says hello to the user, recording their name into state.
    
    Args:
        user_name (str): The name of the user.
    """
    tool_context.state["user_name"] = user_name
    print("\ntool_context.state['user_name']:", tool_context.state["user_name"])
    return graphdb.send_query(
        f"RETURN 'Hello to you, ' + $user_name + '.' AS reply",
    {
        "user_name": user_name
    })


def say_goodbye_stateful(tool_context: ToolContext) -> dict:
    """Says goodbye to the user, reading their name from state."""
    user_name = tool_context.state.get("user_name", "stranger")
    print("\ntool_context.state['user_name']:", user_name)
    return graphdb.send_query("RETURN 'Goodbye, ' + $user_name + ', nice to chat with you!' AS reply",
    {
        "user_name": user_name
    })


def create_hello_agent(llm) -> Agent:
    return Agent(
        name="hello_agent_v1",
        model=llm,
        description="Has friendly chats with a user.",
        instruction="""
        You are a helpful assistant, chatting with a user.
        Be polite and friendly, introducing yourself and asking who the user is.

        If the user provides their name, use the 'say_hello' tool.
        If the tool errors, inform the user politely.
        If successful, present the reply.
        """,
        tools=[say_hello],
    )


async def create_runner(hello_agent: Agent):
    app_name = hello_agent.name + "_app"
    user_id = hello_agent.name + "_user"
    session_id = hello_agent.name + "_session_01"
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    return Runner(
        agent=hello_agent,
        app_name=app_name,
        session_service=session_service
    )

async def response():
    user_message="Hello, I'm ABK"
    print(f"\n>>>User Message: {user_message}")

    agent = create_hello_agent(llm)
    runner = await create_runner(agent)
    app_name = agent.name + "_app"
    user_id = agent.name + "_user"
    session_id = agent.name + "_session_01"

    content = types.Content(role='user', parts=[types.Part(text=user_message)])
    final_response_text = "Agent did not produce a final response"

    verbose = False
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if verbose:
            print(f"[EVENT]    Author: {event.author}, Type: {event.type}, Final: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"\n>>>Agent Final Response: {final_response_text}")

class AgentCaller:
    """A simple wrapper class for interacting with an ADK agent."""
    
    def __init__(self, agent: Agent, runner: Runner, 
                 user_id: str, session_id: str):
        """Initialize the AgentCaller with required components."""
        self.agent = agent
        self.runner = runner
        self.user_id = user_id
        self.session_id = session_id


    def get_session(self):
        return self.runner.session_service.get_session(app_name=self.runner.app_name, user_id=self.user_id, session_id=self.session_id)

    
    async def call(self, user_message: str, verbose: bool = False):
        """Call the agent with a query and return the response."""
        print(f"\n>>> User Message: {user_message}")

        # Prepare the user's message in ADK format
        content = types.Content(role='user', parts=[types.Part(text=user_message)])

        final_response_text = "Agent did not produce a final response." 
        
        # Key Concept: run_async executes the agent logic and returns events we can interact with.
        # We iterate through events to find the final answer.
        async for event in self.runner.run_async(user_id=self.user_id, session_id=self.session_id, new_message=content):

            # if verbose:
            #     print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # is_final_response() marks the concluding message for the turn.
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle errors
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break 

        print(f"<<< Agent Response: {final_response_text}")
        return final_response_text
    
async def make_agent_caller(agent: Agent, initial_state: Optional[Dict[str, Any]] = {}) -> AgentCaller:
    """Create and return an AgentCaller instance for the given agent."""
    app_name = agent.name + "_app"
    user_id = agent.name + "_user"
    session_id = agent.name + "_session_01"
    
    # Initialize a session service and a session
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state
    )
    
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )
    
    return AgentCaller(agent, runner, user_id, session_id)

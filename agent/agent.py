import json
import logging
import os
from typing import Annotated, List

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chat_models import init_chat_model
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition, ToolNode
from mcp import ClientSession
from pydantic import BaseModel
from starlette.websockets import WebSocket
from typing_extensions import TypedDict

load_dotenv()

logger = logging.getLogger('uvicorn.error')

client = MultiServerMCPClient(
    {
        "place_assist": {
            "url": os.environ.get("MCP_PATH"),
            "transport": "streamable_http",
        }
    }
)


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


class QueryRequest(BaseModel):
    question: str


app = FastAPI()


async def create_graph(place_assist_session: ClientSession):
    llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", temperature=0)

    place_assist_tools = await load_mcp_tools(place_assist_session)
    llm_with_tool = llm.bind_tools(place_assist_tools)

    system_prompt = await load_mcp_prompt(place_assist_session, "system_prompt")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt[0].content),
        MessagesPlaceholder("messages")
    ])
    chat_llm = prompt_template | llm_with_tool

    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    graph_builder = StateGraph(State[AnyMessage])
    graph_builder.add_node("chat_node", chat_node)
    graph_builder.add_node("tool_node", ToolNode(tools=place_assist_tools))
    graph_builder.add_edge(START, "chat_node")
    graph_builder.add_conditional_edges("chat_node", tools_condition, {"tools": "tool_node", "__end__": END})
    graph_builder.add_edge("tool_node", "chat_node")
    graph = graph_builder.compile(checkpointer=MemorySaver())
    return graph


@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    logger.info("env " + os.environ.get("MCP_PATH"))
    config = {"configurable": {"thread_id": thread_id}}
    await websocket.accept()
    async with client.session("place_assist") as place_assist:
        agent = await create_graph(place_assist)
        while True:
            data = await websocket.receive_text()
            response = await agent.ainvoke({"messages": data}, config=config)
            await websocket.send_text(json.dumps({"message": response["messages"][-1].content}))

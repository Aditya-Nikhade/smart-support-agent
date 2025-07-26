import os
from dotenv import load_dotenv

from langchain_core.messages import AIMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, END

from langgraph.prebuilt import ToolNode
from app.tools import check_order_status

from app.state import AgentState
from app.rag_setup import get_faq_retriever

load_dotenv()

def escalate(state: AgentState):
    response = AIMessage(content="I am unable to handle this request. A human agent will get back to you shortly.")
    return {"messages": [response]}

def faq_retriever_node(state: AgentState):
    last_question = state['messages'][-1].content
    retriever = get_faq_retriever()
    docs = retriever.invoke(last_question)
    faq_response = AIMessage(content=f"I found this in our FAQ which might help:\n\n{docs[0].page_content}")
    return {"messages": [faq_response]}

class RouteQuery(BaseModel):
    """A Pydantic model to define the structured output we want from the LLM."""
    destination: str = Field(
        description="The next node to route to.",
        enum=["faq_retriever_node", "tool_node", "escalate"]
    )

def get_router_chain():
    llm = AzureChatOpenAI(
        temperature=0,
        model_name="gpt-4.1",
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    )
    structured_llm = llm.with_structured_output(RouteQuery)
    
    system_prompt = """You are an expert at routing a user's query to the correct place.
    Based on the user's last message, route them to `faq_retriever_node` if their question is likely to be answered by a standard FAQ. This includes general questions about refunds, shipping, support contact, or account issues.
    If the user is asking about a specific order by providing an order ID, route them to `tool_node`.
    Otherwise, if it's a complex, specific, or sensitive issue that cannot be resolved by tools or FAQs, route them to `escalate`."""
    
    router_chain = system_prompt | structured_llm
    return router_chain

def router_node(state: AgentState):
    router_chain = get_router_chain()
    result = router_chain.invoke({"input": state['messages'][-1].content})
    print(f"Router Decision: {result.destination}")
    return {"next": result.destination}


def create_graph():
    builder = StateGraph(AgentState)

    tools = [check_order_status]
    tool_node = ToolNode(tools)

    # Add the nodes to the graph
    builder.add_node("router", router_node)
    builder.add_node("escalate", escalate)
    builder.add_node("faq_retriever_node", faq_retriever_node)
    builder.add_node("tool_node", tool_node)

    # Set the entry point
    builder.set_entry_point("router")
    
    # Add conditional edges
    builder.add_conditional_edges(
        "router",
        lambda x: x["next"],
        {
            "faq_retriever_node": "faq_retriever_node",
            "tool_node": "tool_node",
            "escalate": "escalate"
        }
    )
    
    # Define final edges
    builder.add_edge("faq_retriever_node", END)
    builder.add_edge("escalate", END)
    builder.add_edge("tool_node", END)

    return builder.compile()

graph = create_graph()
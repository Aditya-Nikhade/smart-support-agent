from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph import graph

# Create a router object
support_router = APIRouter()

# Define the request body model for our API endpoint
class ChatRequest(BaseModel):
    message: str

@support_router.post("/support")
async def support_chat(request: ChatRequest):
    """
    The main chat endpoint. It receives a user message,
    runs it through the LangGraph agent, and returns the final response.
    """
    # The input to the graph is a dictionary that must match the AgentState structure.
    # We start the conversation with the user's message.
    initial_state = {"messages": [HumanMessage(content=request.message)]}
    
    # 'ainvoke' is the asynchronous method to run the graph.
    final_state = await graph.ainvoke(initial_state)
    
    # The final response is the last message in the state.
    # It could be an AIMessage or a ToolMessage.
    final_response_message = final_state['messages'][-1]

    # We return the content of that message.
    return {"reply": final_response_message.content}
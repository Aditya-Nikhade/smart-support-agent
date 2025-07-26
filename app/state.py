from typing import List, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
   messages: List[BaseMessage]
   next: str
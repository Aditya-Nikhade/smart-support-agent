from fastapi import FastAPI
from app.api_router import support_router 

app = FastAPI(
    title="Smart Support Agent API",
    description="An API for a smart support agent powered by LangGraph and Azure AI."
)

# Include the router from our app module
app.include_router(support_router)
import json
import logging
import os
import sys
from fastapi.responses import JSONResponse

import uvicorn
from fastapi import Depends, FastAPI, Request
from langchain.chat_models import ChatOpenAI
from redis import asyncio as aioredis
from pydantic import BaseModel, BaseSettings
from dotenv import load_dotenv, find_dotenv

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

from model.agents.controller import FinancialAdvisorGPT


# class Config(BaseSettings):
#     redis_url: str = "redis://redis:6379"


class HumanMessage(BaseModel):
    message: str


class AIMessage(BaseModel):
    user_id: str
    message: str


_ = load_dotenv(find_dotenv())
# config = Config()
logger = logging.getLogger(__name__)
llm = ChatOpenAI(temperature=0.9)
agent_pool = {}

# =================================
# Define Application
# =================================

app = FastAPI()

# =================================
# Define Startup Events
# =================================


@app.on_event("startup")
def get_llm_configs():
    """Retrieve llm configs."""
    with open("src/model/configs/examples/agent_singaporean_male.json") as f:
        app.state.llm_configs = json.load(f)


# =================================
# Define Endpoints
# =================================


@app.post("/chat/{user_id}", response_model=AIMessage)
def chat(
    req: Request,
    user_id: str,
    message: HumanMessage,
):
    if user_id in agent_pool:
        agent_chain = agent_pool.get(user_id)
        # retrieve request body and send human input
        agent_chain.human_step(message.message)
    else:
        # create new agent for current chat
        agent_chain = FinancialAdvisorGPT.from_llm(llm, **req.app.state.llm_configs)
        agent_chain.seed_agent()
    # retrieve agent repsonse
    resp = agent_chain.step()
    if "<END_OF_CALL>" in resp:
        del agent_pool[user_id]
    else:
        # store latest agent internals for further conversation
        agent_pool[user_id] = agent_chain
    output = AIMessage(user_id=user_id, message=resp)
    return JSONResponse(content=output.dict())


if __name__ == "__main__":
    uvicorn.run("api:app", port=8000, reload=True)

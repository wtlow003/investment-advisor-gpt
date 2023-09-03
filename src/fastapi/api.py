import json
import logging
import os
import sys

import uvicorn
from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

from model.agents.controller import InvestmentAdvisorGPT


class HealthCheck(BaseModel):
    status: str = "OK!"


class HumanMessage(BaseModel):
    message: str


class AIMessage(BaseModel):
    user_id: str
    raw_message: str


_ = load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)
llm = ChatOpenAI(temperature=0.4)
agent_pool = {}

# =================================
# Define Application
# =================================

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check

    \nEndpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).\n

    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.post(
    "/chat/{user_id}",
    tags=["conversation"],
    summary="Obtain response from Agent",
    response_model=AIMessage,
    responses={
        200: {
            "description": "Query successful.",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "f57f55fa-1bb3-4d82-abd1-862dc14e0873",
                        "message": "Hey man! How are you today?",
                    }
                }
            },
        },
    },
    status_code=status.HTTP_200_OK,
)
def chat(
    req: Request,
    user_id: str,
    message: HumanMessage,
):
    """
    ## Retrieve single response from LLM agent.

    \nEndpoint to retrieve single response from LLM agent given input. Initial call
    to the endpoint can/should be an empty string to allow LLM agent to greet the
    user first.
    .\n

    Returns:
        Returns a JSON response with the user_id and agent's response.
    """
    if user_id in agent_pool:
        agent_chain = agent_pool.get(user_id)
        # retrieve request body and send human input
        agent_chain.human_step(message.message)
    else:
        # create new agent for current chat
        agent_chain = InvestmentAdvisorGPT.from_llm(llm, **req.app.state.llm_configs)
        agent_chain.seed_agent()
    # retrieve agent response
    resp = agent_chain.step()
    # allow the user to say last word before deleting the agent
    if "<END_OF_CALL>" in resp:
        del agent_pool[user_id]
    else:
        # store latest agent internals for further conversation
        agent_pool[user_id] = agent_chain

    output = AIMessage(user_id=user_id, raw_message=resp)
    return JSONResponse(content=output.dict())


if __name__ == "__main__":
    uvicorn.run("api:app", port=8000, reload=False)

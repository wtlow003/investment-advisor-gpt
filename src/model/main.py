import json

from agents.controller import FinancialAdvisorGPT
from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import ChatOpenAI

if __name__ == "__main__":
    _ = load_dotenv(find_dotenv())

    llm = ChatOpenAI(temperature=0.9)
    with open("src/model/configs/examples/agent_singaporean_male.json") as f:
        configs = json.load(f)

    advisor_agent = FinancialAdvisorGPT.from_llm(llm, **configs)
    advisor_agent.seed_agent()

    while True:
        msg = advisor_agent.step()
        if "<END_OF_CALL>" in msg:
            break
        human_input = input("Your response: ")
        advisor_agent.human_step(human_input)
        print("=" * 10)

import glob
import json

from dotenv import load_dotenv, find_dotenv
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chat_models import ChatOpenAI

from model.agents.controller import FinancialAdvisorGPT
from model.chains import ColdCallChain, ConversationStageAnalyzerChain
from model.tools import setup_knowledge_base

if __name__ == "__main__":
    _ = load_dotenv(find_dotenv())

    llm = ChatOpenAI(temperature=0.9)
    config = dict(
        advisor_name="Jensen Low",
        advisor_role="Senior Financial Services Manager",
        company_name="Advisor Clique",
        company_business="""
    Advisors’ Clique (AC) is a group of financial consultants representing Great Eastern Financial Advisers Private Limited (GEFA).
    GEFA is a wholly owned subsidiary of Great Eastern Holdings Pte Ltd, a member of the OCBC Group.
    Advisors' Clique is dedicated to serving your financial needs and empowering you to reach your financial goals through helping to plan for your family's protection, 
    building up your nest egg, or advising on your company's insurance coverage,
    """,
        company_mission="""
    We are committed to thinking in your best interest.
    We empower clients through quality financial advice.
    We groom leaders, not managers.
    We forge new frontiers.
    """,
        company_values="The company values are: Trailblazers, Integrity, Excellence, Gratitude, Abundance, People Matter, and Collective Individualism",
        conversation_purpose="find out if the prospect is interested in the latest financial product offerings.",
        conversation_type="call",
        source_of_contact="Insurance Roadshow",
        prospect_name="Jeremy Goh",
        last_interaction_date="3 months ago",
        conversation_stage="Introduction: Start the cold call by introducing yourself warmly. This include stating your full name, company name, what the company do and credibility statement, or reason why this person you are reaching out to should remain in the conversation. This involves citing a credible source or refrence to connect to the with the other party. Remember to be polite and respectful while keeping the conversation professional.",
        conversation_history=[],
        use_tools=True,
    )

    advisor_agent = FinancialAdvisorGPT.from_llm(llm, verbose=False, **config)
    advisor_agent.seed_agent()

    while True:
        advisor_agent.step()
        if "<END_OF_CALL>" in advisor_agent.conversation_history[-1]:
            break
        human_input = input("Your response: ")
        advisor_agent.human_step(human_input)
        print("=" * 10)

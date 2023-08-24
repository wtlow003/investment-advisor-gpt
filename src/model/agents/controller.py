from typing import Dict, List, Any, Union
from pydantic import BaseModel, Field
from langchain import LLMChain
from langchain.llms import BaseLLM
from langchain.chains.base import Chain
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from termcolor import colored

from model.agents.parser import CustomOutputParser
from model.chains import ConversationStageAnalyzerChain, ColdCallChain
from model.prompts.tools import ADVISOR_TOOLS_PROMPT
from model.prompts.utils import CustomPromptTemplate
from model.tools import get_tools


class FinancialAdvisorGPT(Chain, BaseModel):
    """Controller model for the Sales Agent."""

    conversation_history: List[str] = []
    current_conversation_stage: str = "1"
    convo_stage_analyzer_chain: ConversationStageAnalyzerChain = Field(...)
    cold_call_response_chain: ColdCallChain = Field(...)

    advisor_agent_executor: Union[AgentExecutor, None] = Field(...)
    use_tools: bool = False

    conversation_stage_dict: Dict = {
        "1": "Introducton: Start the cold call by introducing yourself warmly. This include stating your full name, company name, what the company do and credibility statement, or reason why this person you are reaching out to should remain in the conversation. Cite a credible source or reference to connect to the with the other party. Remember to be polite and respectful while keeping the conversation professional.",
        "2": "Qualification: Qualify the prospect by confirming if they are the right person to talk with regards to your financial products/services. Check their age if they are legal (21 years old) to take on financial obligations or are in authority to make purchasing decisions.",
        "3": "Huge Claim: Mention a huge claim with regards to the products/services you are planning to pitch to your sale prospects. Leverage their background as identified in the previous conversation stage in <point 2>. Attract their attention and ensure them that their time is worth. Ensure your claim remains grounded by within the the facts of your products/services to remain credible.",
        "4": "Understanding the Prospect: Ask open-ended questions to uncover the prospect's life situation and figure what are their key financial needs. Listen carefully to their responses and take notes.",
        "5": "Value Proposition: Explain how your financial products/services from our knowledge base can benefit the prospect in detail. List financial benefits that may benefit the prospect. Place all focus on the prospect. Additional emphasis should also be placed on information that are relative to the prospect's situation (e.g., life circumstances, major life events). Highlight key unique selling points and value proposition of the product/service that can potentially change their life for the better.",
        "6": "Address the Doubt: Address any potential doubt or skepticism from the prospect based on either your earlier huge claim or the presentation of your financial products/services. Be prepared to provide evidence or testimonials to support your claims.",
        "7": "Closing: Ask your prospect out for a further meeting/discussion. Provide a few potential dates and times to schedule your next interaction with the prospect. Have a few options available instead if the first or two dates do not fit into the prospect's schedule. Thank the prospect for their if they are not interested in a further meeting.",
    }

    advisor_name: str = "Jensen Low"
    advisor_role: str = "Senior Financial Services Manager"
    nationality: str = "Singaporean"
    primary_language: str = "english"
    slang: str = "singlish"
    company_name: str = "Advisor Clique"
    company_business: str = "Advisors’ Clique (AC) is a group of financial consultants representing Great Eastern Financial Advisers Private Limited (GEFA). GEFA is a wholly owned subsidiary of Great Eastern Holdings Pte Ltd, a member of the OCBC Group. Advisors' Clique is dedicated to serving your financial needs and empowering you to reach your financial goals through helping to plan for your family's protection, building up your nest egg, or advising on your company's insurance coverage."
    company_mission: str = "We are committed to thinking in your best interest. We empower clients through quality financial advice. We groom leaders, not managers. We forge new frontiers."
    company_values: str = "The company values are: Trailblazers, Integrity, Excellence, Gratitude, Abundance, People Matter, and Collective Individualism."
    conversation_purpose: str = "find out if the prospect is interested in the latest financial product offerings, such as critical illness, health insurance, or wealth accumlation plans."
    conversation_type: str = "cold call"
    source_of_contact: str = "insurance roadshow"
    prospect_name: str = "Jeremy Goh"
    last_interaction_date: str = "3 months ago"

    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, "1")

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def seed_agent(self):
        # Step 1: seed the conversation
        self.current_conversation_stage = self.retrieve_conversation_stage("1")
        self.conversation_history = []

    def determine_conversation_stage(self):
        conversation_stage_id = self.convo_stage_analyzer_chain.run(
            conversation_history='"\n"'.join(self.conversation_history),
            current_conversation_stage=self.current_conversation_stage,
        )

        self.current_conversation_stage = self.retrieve_conversation_stage(
            conversation_stage_id
        )

        print(f"Conversation Stage: {self.current_conversation_stage}")

    def human_step(self, human_input):
        # process human input
        human_input = "\nUser: " + human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    def step(self):
        return self._call(inputs={})

    def _call(self, inputs: Dict[str, Any]) -> str:
        """Run one step of the sales agent."""

        # Generate agent's utterance
        if self.use_tools:
            try:
                ai_message = self.advisor_agent_executor.run(
                    tool_input="",
                    input="",
                    conversation_stage=self.current_conversation_stage,
                    conversation_history="\n".join(self.conversation_history),
                    advisor_name=self.advisor_name,
                    advisor_role=self.advisor_role,
                    nationality=self.nationality,
                    primary_language=self.primary_language,
                    slang=self.slang,
                    company_name=self.company_name,
                    company_business=self.company_business,
                    company_values=self.company_values,
                    company_mission=self.company_mission,
                    conversation_purpose=self.conversation_purpose,
                    conversation_type=self.conversation_type,
                    source_of_contact=self.source_of_contact,
                    prospect_name=self.prospect_name,
                    last_interaction_date=self.prospect_name,
                )
            # NOTE: hackish-way to deak with valid but unparseable output from llm: https://github.com/langchain-ai/langchain/issues/1358
            except ValueError as e:
                response = str(e)
                if not response.startswith("Could not parse LLM output: `"):
                    raise e
                ai_message = response.removeprefix(
                    "Could not parse LLM output: `"
                ).removesuffix("`")
        else:
            ai_message = self.cold_call_response_chain.run(
                conversation_stage=self.current_conversation_stage,
                conversation_history="\n".join(self.conversation_history),
                advisor_name=self.advisor_name,
                advisor_role=self.advisor_role,
                nationality=self.nationality,
                primary_language=self.primary_language,
                slang=self.slang,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                company_mission=self.company_mission,
                conversation_purpose=self.conversation_purpose,
                conversation_type=self.conversation_type,
                source_of_contact=self.source_of_contact,
                prospect_name=self.prospect_name,
                last_interaction_date=self.prospect_name,
            )

        # Add agent's response to conversation history
        if "<END_OF_TURN>" in ai_message:
            ai_message = ai_message.rstrip("<END_OF_TURN>")
        elif "<END_OF_CALL>" in ai_message:
            ai_message = ai_message.rstrip("<END_OF_CALL>")

        # stdout message
        print(
            colored(
                f"{self.advisor_name}: " + ai_message,
                "magenta",
            )
        )

        agent_name = self.advisor_name
        ai_message = agent_name + ": " + ai_message
        if ("<END_OF_TURN>" not in ai_message) and ("<END_OF_CALL>" not in ai_message):
            ai_message += " <END_OF_TURN>"
        self.conversation_history.append(ai_message)

        return ai_message

    @classmethod
    def from_llm(
        cls, llm: BaseLLM, verbose: bool = False, **kwargs
    ) -> "FinancialAdvisorGPT":
        """Initialize the FinancialAdvisorGPT Controller."""
        convo_stage_analyzer_chain = ConversationStageAnalyzerChain.from_llm(
            llm, verbose=verbose
        )

        cold_call_response_chain = ColdCallChain.from_llm(llm, verbose=verbose)

        if "use_tools" in kwargs and kwargs["use_tools"] is False:
            advisor_agent_executor = None
        else:
            tools = get_tools(llm)

            prompt = CustomPromptTemplate(
                template=ADVISOR_TOOLS_PROMPT,
                tools_getter=lambda x: tools,
                # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
                # This includes the `intermediate_steps` variable because that is needed
                input_variables=[
                    "input",
                    "intermediate_steps",
                    "advisor_name",
                    "advisor_role",
                    "nationality",
                    "primary_language",
                    "slang",
                    "company_name",
                    "company_business",
                    "company_mission",
                    "company_values",
                    "conversation_purpose",
                    "conversation_type",
                    "source_of_contact",
                    "last_interaction_date",
                    "prospect_name",
                    "conversation_stage",
                    "conversation_history",
                ],
            )
            llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

            # It makes assumptions about output from LLM which can break and throw an error
            output_parser = CustomOutputParser(ai_prefix=kwargs["advisor_name"])
            tool_names = [tool.name for tool in tools]
            advisor_agent_with_tools = LLMSingleActionAgent(
                llm_chain=llm_chain,
                output_parser=output_parser,
                stop=["\nObservation:"],
                allowed_tools=tool_names,
                verbose=verbose,
            )

            advisor_agent_executor = AgentExecutor.from_agent_and_tools(
                agent=advisor_agent_with_tools, tools=tools, verbose=verbose
            )

        return cls(
            convo_stage_analyzer_chain=convo_stage_analyzer_chain,
            cold_call_response_chain=cold_call_response_chain,
            advisor_agent_executor=advisor_agent_executor,
            verbose=verbose,
            **kwargs,
        )

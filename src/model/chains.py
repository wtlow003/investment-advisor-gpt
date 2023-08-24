from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from pydantic import Field

from model.prompts.chains import (
    COLD_CALL_INIT_PROMPT_TEMPLATE,
    CONVO_STAGE_ANALYZER_INIT_PROMPT_TEMPLATE,
)


class ConversationStageAnalyzerChain(LLMChain):
    """
    Chain to analyze which conversation stage should the conversation move into.
    """

    @classmethod
    def from_llm(
        cls, llm: BaseLLM, verbose: bool = True
    ) -> "ConversationStageAnalyzerChain":
        """
        Create an instance of the ConversationStageAnalyzerChain class from a given language model.

        Args:
            llm (BaseLLM): The language model to use.
            verbose (bool, optional): Flag to enable verbose mode. Defaults to True.

        Returns:
            ConversationStageAnalyzerChain: An instance of the ConversationStageAnalyzerChain class.
        """
        cls.prompt_template = CONVO_STAGE_ANALYZER_INIT_PROMPT_TEMPLATE
        prompt = PromptTemplate(
            template=CONVO_STAGE_ANALYZER_INIT_PROMPT_TEMPLATE,
            input_variables=["conversation_history"],
        )

        return cls(prompt=prompt, llm=llm, verbose=verbose)

    @property
    def _chain_type(self) -> str:
        """
        Get the chain type of the class.

        Returns:
            str: The chain type.
        """
        return self.__class__.__name__


class ColdCallChain(LLMChain):
    """
    Chain to generate the next response in the cold call interaction.
    """

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """
        Create an instance of the ColdCallChain class from a given language model.

        Args:
            llm (BaseLLM): The language model to use.
            verbose (bool, optional): Flag to enable verbose mode. Defaults to True.

        Returns:
            ColdCallChain: An instance of the ColdCallChain class.
        """
        cls.prompt_template = COLD_CALL_INIT_PROMPT_TEMPLATE
        prompt = PromptTemplate(
            template=COLD_CALL_INIT_PROMPT_TEMPLATE,
            input_variables=[
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

        return cls(prompt=prompt, llm=llm, verbose=verbose)

    @property
    def _chain_type(self) -> str:
        """
        Get the chain type of the class.

        Returns:
            str: The chain type.
        """
        return self.__class__.__name__

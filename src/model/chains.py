from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from langchain.memory.chat_memory import BaseChatMemory

from templates.chains import (
    SALES_COLD_CALL_INIT_PROMPT_TEMPLATE,
    CONVO_STAGE_ANALYZER_INIT_PROMPT_TEMPLATE,
)


class ConversationStageAnalyzerChain(LLMChain):
    """
    Chain to analyze which conversation stage should the conversation move into.
    """

    @classmethod
    def from_llm(
        cls, llm: BaseLLM, verbose: bool = True, **kwargs
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
        if "memory" in kwargs:
            memory = kwargs.get("memory")
            # for no tools usage
            return cls(prompt=prompt, llm=llm, memory=memory, verbose=verbose)
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
    def from_llm(
        cls, llm: BaseLLM, memory: BaseChatMemory, verbose: bool = True
    ) -> LLMChain:
        """
        Create an instance of the ColdCallChain class from a given language model.

        Args:
            llm (BaseLLM): The language model to use.
            verbose (bool, optional): Flag to enable verbose mode. Defaults to True.

        Returns:
            ColdCallChain: An instance of the ColdCallChain class.
        """
        cls.prompt_template = SALES_COLD_CALL_INIT_PROMPT_TEMPLATE
        prompt = PromptTemplate(
            template=SALES_COLD_CALL_INIT_PROMPT_TEMPLATE,
            input_variables=[
                "advisor_name",
                "advisor_role",
                "nationality",
                "formal_language",
                "informal_language",
                "company_name",
                "company_business",
                "prospect_name",
                "source_of_contact",
                "conversation_purpose",
                "conversation_type",
                "conversation_stage",
                "conversation_history",
            ],
        )

        return cls(prompt=prompt, llm=llm, memory=memory, verbose=verbose)

    @property
    def _chain_type(self) -> str:
        """
        Get the chain type of the class.

        Returns:
            str: The chain type.
        """
        return self.__class__.__name__

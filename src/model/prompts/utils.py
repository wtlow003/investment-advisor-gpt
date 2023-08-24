from typing import Callable, List

from langchain.prompts.base import StringPromptTemplate
from pydantic import validator


class CustomPromptTemplate(StringPromptTemplate):
    template: str
    # list of tools available
    tools_getter: Callable

    @validator("input_variables")
    def validate_input_variables(cls, v) -> List[str]:
        """Validate that input variables are correct."""
        # TODO: keep input variables somewhere as a config
        # to prevent hardcoding
        if len(v) == 0:
            raise ValueError("Missing required input_variables!")
        return v

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts
        tools = self.tools_getter(kwargs["input"])
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}," for tool in tools]
        )
        kwargs["tools_name"] = ", ".join([tool.name for tool in tools])
        return self.template.format(**kwargs)

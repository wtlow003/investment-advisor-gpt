import os
from typing import Dict, List, Tuple, Union

from langchain.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFDirectoryLoader, UnstructuredURLLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import BaseLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import BaseTool
from langchain.vectorstores import Chroma


# TODO: disabling it for now as it doesnt work
# class SearchPromotion(BaseTool):
#     name: str = "search_promotion"
#     description: str = "Search latest promotion for all product offerings. Use this when you need to answer prospect's questions on any form of promotion if he buys our products."

#     def _get_promotion_website(self) -> str:
#         url: str = "https://www.greateasternlife.com/sg/en/personal-insurance/rewards-and-promotions.html"

#         loader = UnstructuredURLLoader(
#             urls=[url],
#             mode="single",
#             post_processors=[clean, remove_punctuation, clean_extra_whitespace],
#         )
#         elements = loader.load()
#         full_text = "".join([e.page_content for e in elements])

#         return full_text

#     def _run(self, query: str) -> Union[str, None]:
#         """Use tool to get latest promotion."""

#         return self._get_promotion_website()

#     async def _arun(self) -> str:
#         """Use tool asynchronously."""
#         raise NotImplementedError("Tool does not support async at the moment.")

#     def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
#         return (), {}


def setup_knowledge_base(llm: BaseLLM, prospectus: List[str]):
    """_summary_

    Args:
        llm (BaseLLM): _description_
        prospectus (List[str]): _description_
    """

    loader = PyPDFDirectoryLoader(
        "/Users/jensen/code/financial-advisor-gpt/data", silent_errors=True
    )
    documents = loader.load()
    for doc in documents:
        source = doc.metadata["source"].removesuffix(".pdf").split("/")[-1].split("-")
        product_name = source[1:-2]
        plan_type = source[-4:-2]
        doc.metadata["product_name"] = " ".join(product_name).title()
        doc.metadata["plan_type"] = " ".join(plan_type)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    documents = text_splitter.split_documents(documents)

    if "db" in os.listdir("."):
        vectordb = Chroma(
            persist_directory="./db", embedding_function=OpenAIEmbeddings()
        )
    else:
        vectordb = Chroma.from_documents(
            documents, embedding=OpenAIEmbeddings(), persist_directory="./db"
        )
        vectordb.persist()

    knowledge_base = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        chain_type="stuff",
        retriever=vectordb.as_retriever(search_kwargs={"k": 7}),
    )

    return knowledge_base


def get_tools():
    """
    Define tools usable by the Advisor Agent.
    """

    llm = ChatOpenAI(temperature=0)
    knowledge_base = setup_knowledge_base(llm, [])
    search = GoogleSerperAPIWrapper(type="news")
    tools = [
        Tool(
            name="WebSearch",
            func=search.run,
            description="Access to google search. Always use this to obtain information about current events.",
        ),
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            description="Access to all our products. Always use this when asked about the products we offer",
        ),
        # Tool(
        #     name="SearchPromotion",
        #     func=SearchPromotion.run,
        #     description="Use this when you need to answer prospect's questions on whether if there is additional benefits or promotion if he buys our products.",
        # ),
    ]

    return tools

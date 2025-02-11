from typing import Any
from ChatProp.tools.Literature_Search.base import Scholar2ResultLLM
from langchain.base_language import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain.tools import Tool
def _get_literature_search(
        llm: BaseLanguageModel,
        verbose: bool = False,
        **kwargs: Any
    ) -> BaseTool:

    literature_search = Scholar2ResultLLM(llm=llm)
    return Tool(
        name="LiteratureSearch",
        description=(
            "Useful to answer questions that require technical "
            "knowledge. Ask a specific question."
        ),
        func=literature_search,
    )
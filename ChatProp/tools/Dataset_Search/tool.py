from typing import Any
from langchain.tools import Tool
from langchain.base_language import BaseLanguageModel
from ChatProp.config import config
from ChatProp.tools.Dataset_Search.base import TableSearcher


def _get_dateset_search(
        llm: BaseLanguageModel,
        file_path: str = config['data_dir'],
        verbose: bool = False,
        **kwargs: Any) -> Tool:
    
    table_searcher = TableSearcher.from_filepath(
        llm=llm, 
        file_path=file_path, 
        verbose=verbose
    )
    
    def dateset_search(question: str) -> str:
        try:
            result = table_searcher.invoke({
                'input': question,  
                'information': "Include units in the output."
            })
            if isinstance(result, dict):
                return result.get('answer', 'No answer returned.')
            elif isinstance(result, str):
                return result
            else:
                return 'Unexpected response format.'
        except Exception as e:
            return e
    
    return Tool(
        name="DatesetSearch",
        description=(
                "A tool that extracts accurate properties from a look-up table in the database. "
                "The input must be a detailed full sentence to answer the question."
        ),
        func=dateset_search
    )

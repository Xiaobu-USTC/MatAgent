import warnings
from typing import Dict, Callable, List
from pydantic import ValidationError
from langchain.base_language import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain_community.agent_toolkits.load_tools import load_tools, get_all_tool_names
from ChatProp.tools.Dataset_Search import _get_dateset_search
from ChatProp.tools.predictor import _get_predict_properties
from ChatProp.tools.Literature_Search import _get_literature_search
_ChemAgent_TOOLS: Dict[str, Callable[[BaseLanguageModel, bool], BaseTool]] = {
    "DatesetSearch": _get_dateset_search,
    "Predictor": _get_predict_properties,
    "LiteratureSearch": _get_literature_search
}

_load_internet_tool_names: list[str] = [
    'google-search',
    'google-search-results-json',
    'wikipedia',
]

def load_chemagent_tools(
        llm: BaseLanguageModel, 
        verbose: bool=False,
        search_internet: bool=False,    
    ) -> List[BaseTool]:
    # Initialize custom tools with verbose
    custom_tools = [model(llm=llm, verbose=verbose) for model in _ChemAgent_TOOLS.values()]

    if search_internet:
        try:
            internet_tools = load_tools(_load_internet_tool_names, llm=llm)
            custom_tools += internet_tools
        except Exception as e:
            warnings.warn(f'The internet tool does not work - {str(e)}')
    
    return custom_tools

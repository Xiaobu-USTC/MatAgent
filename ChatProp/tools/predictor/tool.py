from typing import Any
from langchain.tools import Tool
from langchain.base_language import BaseLanguageModel
from langchain.tools.base import BaseTool
from ChatProp import __root_dir__
from ChatProp.tools.predictor.base import Predictor



def _get_predict_properties(
        llm: BaseLanguageModel,
        verbose: bool = False,
        **kwargs: Any
) -> BaseTool:
    
    property_predictor = Predictor.from_llm(
        llm=llm, 
        verbose=verbose
    )

    def predict_property(question: str) -> str:
        try:
            result = property_predictor.invoke(
                {'question': question}
            )
            if isinstance(result, dict):
                return result.get('answer', 'No answer returned.')
            elif isinstance(result, str):
                return result
            else:
                return 'Unexpected response format.'
        except Exception as e:
            return f"An error occurred during CSV search: {e}"


    return Tool(
        name="predictor",
        description=(
            "Useful tool to predict material properties using pre-trained model or first principles software. "
            "More imprecise than the search_csv tool, but can be used universally. "
            "If you didn't get the properties of the substance using the search_csv tool, try using the predictor tool."
            "The input must be a detailed full sentence to answer the question."
        ),
        func=predict_property,
    )
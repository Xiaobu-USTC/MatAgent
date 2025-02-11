from langchain.chains.base import Chain
from langchain.base_language import BaseLanguageModel
from langchain.agents import AgentType, initialize_agent
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ChatProp.agent.prompt import PREFIX, FORMAT_INSTRUCTIONS, SUFFIX
from ChatProp.config import config
from ChatProp.tools import tools_load
from langchain.callbacks.manager import CallbackManagerForChainRun


class ChemAgent(Chain):
    """A Chain that integrates LangChain agents for chemical data querying."""
    llm: BaseLanguageModel  # Explicitly declare llm field
    agent: Any
    verbose: bool = False
    input_key: str = "input"
    output_key: str = "output"

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Dict[str, Any]:
        input_text = inputs[self.input_key]
        callbacks = run_manager.get_child() if run_manager else None
        output = self.agent.invoke(input_text, callbacks=callbacks)
        return {
            self.output_key: output
        }

    @classmethod
    def from_llm(
        cls: BaseModel,
        llm: BaseLanguageModel,
        verbose: bool = False,
        search_internet: bool = True,
    ) -> Chain:
        """Initializes the ChemAgent with the given LLM and configurations."""
        # Initialize tools
        tools = tools_load.load_chemagent_tools(llm=llm, verbose=verbose, search_internet=search_internet)
        
        agent_kwargs = {
            'prefix': PREFIX,
            'format_instructions': FORMAT_INSTRUCTIONS,
            'suffix': SUFFIX
        }
        # Initialize agent
        try:
            agent = initialize_agent(
                tools,
                llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=verbose,
                agent_kwargs=agent_kwargs,
                handle_parsing_errors=config["handle_errors"],
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize agent: {e}")

        return cls(agent=agent, llm=llm, verbose=verbose)

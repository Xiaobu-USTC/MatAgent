import os
import re
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List, Optional, Callable

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import tiktoken

from ChatProp.config import config
from ChatProp.tools.Dataset_Search.prompt import DF_PROMPT


class TableSearcher(Chain):
    """Tools that search using Pandas agent"""
    llm_chain: LLMChain
    df: pd.DataFrame
    encode_function: Callable
    num_max_data: int = 200
    input_key: str = 'input'  # Changed from 'question' to 'input'
    output_key: str = 'answer'
    verbose: bool = False  # Ensure verbose attribute is present

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _parse_output(self, text: str) -> Dict[str, Any]:
        if not isinstance(text, str):
            raise ValueError(f"Expected string from LLM, but got {type(text)}: {text}")
        
        thought = re.search(r"(?<!Final )Thought:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        input_ = re.search(r"Input:\s*(?:```python)?\s*```python\s*(.+?)\s*```?\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        final_thought = re.search(r"Final Thought:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        final_answer = re.search(r"Final Answer:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        observation = re.search(r"Observation:\s*(.+?)\s*(Observation|Final|Input|Thought|Question|$)", text, re.DOTALL)
        
        if (not input_) and (not final_answer):
            raise ValueError(f'unknown format from LLM: {text}')
        
        return {
            'Thought': (thought.group(1).strip() if thought else None),
            'Input': (input_.group(1).strip() if input_ else None),
            'Final Thought' : (final_thought.group(1).strip() if final_thought else None),
            'Final Answer': (final_answer.group(1).strip() if final_answer else None),
            'Observation': (observation.group(1).strip() if observation else None),
        }
    
    def _clear_name(self, text: str) -> str:
        remove_list = ['_clean_h', '_clean', '_charged', '_manual', '_ion_b', '_auto', '_SL']
        str_remove_list = r"|".join(remove_list)
        return re.sub(rf"({str_remove_list})", "", text)
    
    @staticmethod
    def _get_df(file_path: str):
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.xlsx':
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f'table must be .csv, .xlsx, or .json, not {file_path.suffix}')

        return df
    
    def _write_log(self, action, text, run_manager):
        run_manager.on_text(f"\n[Table Searcher] {action}: ", verbose=self.verbose)
        run_manager.on_text(text, verbose=self.verbose, color='yellow')
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        
        return_observation = inputs.get('return_observation', False)
        information = inputs.get('information', "If unit exists, you must include it in the final output. The name of the material exists in the column \"name\".")

        agent_scratchpad = ''
        max_iteration = config['max_iteration']

        input_ = self._clear_name(inputs[self.input_key])
        for i in range(max_iteration + 1):
            llm_output = self.llm_chain.invoke(
                input={
                    'df_index': str(list(self.df)),
                    'information': information,
                    'df_head': self.df.head().to_markdown(),
                    'input': input_,  # 已更改为 'input'
                    'agent_scratchpad': agent_scratchpad,
                    'df_exp': self.df.loc[self.df['name']=='CH4', 'energy(eV)'].to_markdown()
                },
                callbacks=callbacks,
                stop=['Observation:', 'Question:']
            )

            if isinstance(llm_output, dict):
                llm_output = llm_output.get('text', '')

            if not llm_output.strip():
                agent_scratchpad += 'Thought: '
                llm_output = self.llm_chain.invoke(
                    input={
                        'df_index': str(list(self.df)),
                        'information': information,
                        'df_head': self.df.head().to_markdown(),
                        'input': input_,  # 已更改为 'input'
                        'agent_scratchpad': agent_scratchpad
                    },
                    callbacks=callbacks,
                    stop=['Observation:', 'Question:']
                )
                if isinstance(llm_output, dict):
                    llm_output = llm_output.get('text', '')
            if re.search(r'Final Answer: (success|.* above|.* success|.* succeed|.* DataFrames?).?$', llm_output):
                thought = f'Final Thought: we have to answer the question `{input_}` using observation\n'
                agent_scratchpad += thought
                llm_output = self.llm_chain.invoke(
                    input={
                        'df_index': str(list(self.df)),
                        'df_head': self.df.head().to_markdown(),
                        'input': input_,  # 已更改为 'input'
                        'information': information,
                        'agent_scratchpad': agent_scratchpad
                    },
                    callbacks=callbacks,
                    stop=['Observation:', 'Question:']
                )
                if isinstance(llm_output, dict):
                    llm_output = llm_output.get('text', '')
                llm_output = thought + llm_output
            output = self._parse_output(llm_output)

            if output['Final Answer']:
                if output['Observation']:
                    raise ValueError(llm_output)
                
                self._write_log('Final Thought', output['Final Thought'], run_manager)

                final_answer: str = output['Final Answer']

                check_sentence = ''
                if re.search(r'nothing', final_answer):
                    final_answer = 'There are no data in database.'
                elif final_answer.endswith('.'):    
                    final_answer += check_sentence
                else:
                    final_answer = f'The answer for question "{input_}" is {final_answer}.{check_sentence}'

                self._write_log('Final Answer', final_answer, run_manager)
                return {self.output_key: final_answer}
            
            elif i >= max_iteration:
                final_answer = 'There are no data in database'
                self._write_log('Final Thought',
                                output['Final Thought'], run_manager)
                self._write_log('Final Answer', final_answer, run_manager)

                return {self.output_key: final_answer}

            else:
                self._write_log('Thought', output['Thought'], run_manager)
                self._write_log('Input', output['Input'], run_manager)
            pytool = PythonAstREPLTool(locals={'df': self.df})
            observation = str(pytool.run(output['Input'])).strip()

            num_tokens = self.encode_function(observation)
            
            if return_observation:
                if "\n" in observation:
                    self._write_log('Observation', "\n"+observation, run_manager)
                else:
                    self._write_log('Observation', observation, run_manager)
                return {self.output_key: observation}
            if "\n" in observation:
                self._write_log('Observation', "\n"+observation, run_manager)
            else:
                self._write_log('Observation', observation, run_manager)

            agent_scratchpad += 'Thought: {}\nInput: {} \nObservation: {}'\
                .format(output['Thought'], output['Input'], observation)

        raise AssertionError('Code Error! please report to author!')


    @classmethod
    def from_filepath(
        cls,
        llm: BaseLanguageModel,
        file_path: Path = Path(config['data_dir']),
        prompt: str = DF_PROMPT,
        **kwargs
    ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['df_index', 'information', 'df_head', 'input', 'agent_scratchpad']  
        )
        llm_chain = LLMChain(llm=llm, prompt=template)
        df = cls._get_df(file_path)
        encode_function = llm.get_num_tokens
        verbose = kwargs.pop('verbose', False)

        return cls(
            llm_chain=llm_chain, 
            df=df, 
            encode_function=encode_function, 
            verbose=verbose,
            **kwargs  
        )
    
    @classmethod
    def from_dataframe(
        cls,
        llm: BaseLanguageModel,
        dataframe: pd.DataFrame,
        prompt: str = DF_PROMPT,
        **kwargs
    ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['df_index', 'information', 'df_head', 'input', 'agent_scratchpad'] 
        )
        llm_chain = LLMChain(llm=llm, prompt=template)

        encode_function = llm.get_num_tokens
        verbose = kwargs.pop('verbose', False)

        return cls(
            llm_chain=llm_chain, 
            df=dataframe, 
            encode_function=encode_function, 
            verbose=verbose,
            **kwargs 
        )

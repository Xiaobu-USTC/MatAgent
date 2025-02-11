import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ["CUDA_VISIBLE_DEVICES"]='0'

import copy
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from ChatProp.models_load import ModelsLoad
from ChatProp.config import config as config_default
from ChatProp.agent.chem_agent import ChemAgent

def generate_response(question, model='gpt-4', temperature=0):
    config = copy.deepcopy(config_default)

    search_internet = config['search_internet']
    verbose = config['verbose']
    llm = ModelsLoad(model, temperature).get_llm()

    callback_manager = CallbackManager([StdOutCallbackHandler()])

    chemagent = ChemAgent.from_llm(
        llm=llm, 
        verbose=verbose, 
        search_internet=search_internet,
    )
    
    question = question
    
    try:
        output = chemagent.invoke({"input": question}, callbacks=callback_manager)
    except ValueError as ve:
        print(f"Input validation error: {ve}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    return output

if __name__ == '__main__':
    generate_response()

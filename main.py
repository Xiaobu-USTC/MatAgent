import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ["CUDA_VISIBLE_DEVICES"]='0'

import copy
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from MatAgent.models_load import ModelsLoad
from MatAgent.config import config as config_default
from MatAgent.agent.chem_agent import ChemAgent

def main(model='gpt-4', temperature=0) -> str:
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
    
    print ('#' * 50 + "\n")
    print ('Welcome to ChemAgent!')
    print("\n" + "#"*30 + ' Question ' + "#"*30)
    print ('Please enter the question below >>')
    question = input()
    
    try:
        output = chemagent.invoke({"input": question}, callbacks=callback_manager)
    except ValueError as ve:
        print(f"Input validation error: {ve}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print ('\n')
    print ("#"*10 + ' Output ' + "#" * 30)
    print (output)
    print ('\n')
    print ('Thanks for using ChemAgent!')

    return output

if __name__ == '__main__':
    main()

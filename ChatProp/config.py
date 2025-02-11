import os
from ChatProp import __root_dir__


config = {

    'search_internet': False,
    'verbose': True,
    'handle_errors': True,

    # LLM - openAI
    'temperature': 0.0,    
    'model': 'gpt-4',

    # data directory
    'model_dir': os.path.join(__root_dir__, 'model_library'),
    'data_dir': os.path.join(__root_dir__, 'database/tables/data.csv'),
    #predictor
    'predictor': os.path.join(__root_dir__, 'tools/predictor'),
    # table searcher
    
    'max_iteration': 3,
    'token_limit': False,

    # predictor
    'max_length_in_predictor' : 30,
    'accelerator' : 'cuda',
}

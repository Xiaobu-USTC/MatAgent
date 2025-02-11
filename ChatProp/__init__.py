import os

__version__ = '0.1.0'   
__root_dir__ = os.path.dirname(__file__)


from langchain_community.chat_models import ChatOpenAI
from ChatProp.agent.chem_agent import ChemAgent
from ChatProp.config import config
from ChatProp import models_load


__all__ = [
    "ChemAgent",
    "config",
    "ChatOpenAI",
    "__version__",
    'models_load',
]

from langchain_ollama.llms import OllamaLLM
from langchain_community.chat_models import ChatOpenAI
from langchain.base_language import BaseLanguageModel
import os

class ModelsLoad:
    def __init__(self, model_name: str, temperature: float = 0.1, max_tokens: int = 4096):
        self.model_name = model_name.lower()  # 统一转小写，避免大小写不一致问题
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.m_name = model_name.lower()
        self.llm = None  # 初始化时没有加载 LLM

        if self.m_name.startswith('gpt'):
            self.llm = self.get_openai_llm()
        elif self.m_name.startswith('qwen'):
            self.llm = self.get_ollama_llm()

    def get_openai_llm(self) -> BaseLanguageModel:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_api_base = os.getenv("OPENAI_API_BASE")

        CHAT_MODELS = [
            'gpt-4',
            'gpt-4-0613',
            'gpt-4-32k',
            'gpt-4-32k-0613',
            'gpt-4-0314',
            'gpt-4-32k-0314',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k',
            'gpt-3.5-turbo-instruct',
            'gpt-3.5-turbo-0613',
            'gpt-3.5-turbo-16k-0613',
            'gpt-3.5-turbo-0301',
        ]

        if self.m_name in CHAT_MODELS:
            llm = ChatOpenAI(
                model_name=self.m_name,
                temperature=self.temperature,
                openai_api_key=openai_api_key,
                openai_api_base=openai_api_base
            )
            return llm
        else:
            raise ValueError(f"Unsupported OpenAI model: {self.m_name}")

    def get_ollama_llm(self) -> BaseLanguageModel:
        """Load an Ollama model into LangChain.

        Parameters
        ----------
        model_name: The name of the Ollama model to load.
        temperature: The hyperparameter that controls the randomness of the generated text.

        Returns
        -------
        A LangChain Ollama model object.
        """
        try:
            llm = OllamaLLM(model=self.model_name, temperature=self.temperature)
            return llm
        except Exception as error:
            raise ValueError(f"Error loading Ollama model: {error}")

    def get_llm(self) -> BaseLanguageModel:
        if self.llm is None:
            raise ValueError("LLM has not been initialized.")
        return self.llm

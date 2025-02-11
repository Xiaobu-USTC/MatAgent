import os
import re

import langchain
import molbloom
import paperqa
import paperscraper
from langchain import SerpAPIWrapper
from langchain.base_language import BaseLanguageModel
from pydantic import BaseModel
from langchain.tools import BaseTool
from langchain_community.embeddings import OpenAIEmbeddings
from pypdf.errors import PdfReadError
from langchain_core.runnables import RunnableSequence



def paper_scraper(search: str, pdir: str = "query", semantic_scholar_api_key: str = None) -> dict:
    try:
        return paperscraper.search_papers(
            search,
            pdir=pdir,
            semantic_scholar_api_key=semantic_scholar_api_key,
        )
    except KeyError:
        return {}


def paper_search(llm, query, semantic_scholar_api_key=None):
    prompt = langchain.prompts.PromptTemplate(
        input_variables=["question"],
        template="""
        I would like to find scholarly papers to answer
        this question: {question}. Your response must be at
        most 10 words long.
        'A search query that would bring up papers that can answer
        this question would be: '""",
    )
    query_chain = langchain.chains.llm.LLMChain(llm=llm, prompt=prompt)
    if not os.path.isdir("./query"):  # todo: move to ckpt
        os.mkdir("query/")
    search = query_chain.run(query)
    papers = paper_scraper(search, pdir=f"query/{re.sub(' ', '', search)}", semantic_scholar_api_key=semantic_scholar_api_key)
    return papers


def scholar2result_llm(llm, query, k=5, max_sources=2, openai_api_key=None, semantic_scholar_api_key=None):
    """Useful to answer questions that require
    technical knowledge. Ask a specific question."""
    papers = paper_search(llm, query, semantic_scholar_api_key=semantic_scholar_api_key)
    if len(papers) == 0:
        return "Not enough papers found"
    docs = paperqa.Docs(
        llm=llm,
        summary_llm=llm,
        embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key),
    )
    not_loaded = 0
    for path, data in papers.items():
        try:
            docs.add(path, data["citation"])
        except (ValueError, FileNotFoundError, PdfReadError):
            not_loaded += 1

    if not_loaded > 0:
        print(f"\nFound {len(papers.items())} papers but couldn't load {not_loaded}.")
    else:
        print(f"\nFound {len(papers.items())} papers and loaded all of them.")

    answer = docs.query(query, k=k, max_sources=max_sources).formatted_answer
    return answer


class Scholar2ResultLLM(BaseTool, BaseModel):
    llm: BaseLanguageModel = None


    def __init__(self, llm, verbose=True):
        super().__init__(llm=llm, verbose=verbose)
        self.llm = llm
        # api keys
        self.openai_api_key = os.getenv('openai_api_key')
        self.semantic_scholar_api_key = os.getenv('semantic_scholar_api_key')

    def _run(self, query) -> str:
        return scholar2result_llm(
            self.llm,
            query,
            openai_api_key=self.openai_api_key,
            semantic_scholar_api_key=self.semantic_scholar_api_key
        )

    async def _arun(self, query) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("this tool does not support async")

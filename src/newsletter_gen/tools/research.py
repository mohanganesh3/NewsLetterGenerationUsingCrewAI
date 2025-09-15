from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from exa_py import Exa
import os
from datetime import datetime, timedelta
import time
import json
from tenacity import retry, stop_after_attempt, wait_exponential


# Explicit input schemas help both LangChain and CrewAI validate tool usage
class SearchAndContentsInput(BaseModel):
    search_query: str = Field(..., description="Query string to search recent web content")


class FindSimilarInput(BaseModel):
    article_url: str = Field(..., description="URL of the article to find similar content for")


class GetContentsInput(BaseModel):
    article_ids: list[str] = Field(
        ..., description="List of article IDs or URLs to fetch contents for"
    )


class SearchAndContents(BaseTool):
    name: str = "search_and_contents"
    description: str = (
        "Search the web (last 7 days) using Exa and return brief content summaries as JSON."
    )
    args_schema = SearchAndContentsInput

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _run(self, search_query: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")
        try:
            search_results = exa.search_and_contents(
                query=search_query,
                use_autoprompt=True,
                start_published_date=date_cutoff,
                text={"include_html_tags": False, "max_characters": 300},
                num_results=2,
            )
            time.sleep(1)
            return json.dumps(search_results, default=str)
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise
            raise Exception(f"Exa API error: {str(e)}")


class FindSimilar(BaseTool):
    name: str = "find_similar"
    description: str = (
        "Find similar articles to a given article URL using Exa; returns JSON."
    )
    args_schema = FindSimilarInput

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _run(self, article_url: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")
        try:
            search_results = exa.find_similar(
                url=article_url,
                start_published_date=date_cutoff,
            )
            time.sleep(1)
            return json.dumps(search_results, default=str)
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise
            raise Exception(f"Exa API error: {str(e)}")


class GetContents(BaseTool):
    name: str = "get_contents"
    description: str = (
        "Get contents of specific articles via Exa. Input: list of IDs/URLs; returns JSON."
    )
    args_schema = GetContentsInput

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _run(self, article_ids: list[str]) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        try:
            contents = exa.get_contents(article_ids, text={"max_characters": 300})
            time.sleep(1)
            return json.dumps(contents, default=str)
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise
            raise Exception(f"Exa API error: {str(e)}")


# Factory that returns tool instances

def get_tools():
    return [SearchAndContents(), FindSimilar(), GetContents()]

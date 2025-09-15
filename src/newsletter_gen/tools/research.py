from langchain_core.tools import tool
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


@tool("search_and_contents", args_schema=SearchAndContentsInput)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def search_and_contents(search_query: str) -> str:
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


@tool("find_similar", args_schema=FindSimilarInput)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def find_similar(article_url: str) -> str:
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


@tool("get_contents", args_schema=GetContentsInput)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def get_contents(article_ids: list[str]) -> str:
    exa = Exa(api_key=os.getenv("EXA_API_KEY"))
    try:
        contents = exa.get_contents(article_ids, text={"max_characters": 300})
        time.sleep(1)
        return json.dumps(contents, default=str)
    except Exception as e:
        if "413" in str(e) or "429" in str(e):
            raise
        raise Exception(f"Exa API error: {str(e)}")


def get_tools():
    # Return the Tool objects created by the @tool decorator
    return [search_and_contents, find_similar, get_contents]

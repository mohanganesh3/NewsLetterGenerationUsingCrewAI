from langchain_core.tools import BaseTool
from exa_py import Exa
import os
from datetime import datetime, timedelta
import time
from tenacity import retry, stop_after_attempt, wait_exponential


class SearchAndContents(BaseTool):
    name: str = "Search and Contents Tool"
    description: str = (
        "Searches the web for recent news (last week) using Exa API and returns content summaries."
    )

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
                num_results=2
            )
            time.sleep(1)  # Enforce 1-second delay
            return search_results
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise  # Let tenacity handle retry
            raise Exception(f"Exa API error: {str(e)}")


class FindSimilar(BaseTool):
    name: str = "Find Similar Tool"
    description: str = (
        "Searches for similar articles to a given article using the Exa API. Takes in a URL of the article."
    )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _run(self, article_url: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")

        try:
            search_results = exa.find_similar(
                url=article_url,
                start_published_date=date_cutoff
            )
            time.sleep(1)  # Enforce 1-second delay
            return search_results
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise  # Let tenacity handle retry
            raise Exception(f"Exa API error: {str(e)}")


class GetContents(BaseTool):
    name: str = "Get Contents Tool"
    description: str = (
        "Gets the contents of specific articles using the Exa API. Takes article IDs as a list, e.g., ['https://www.cnbc.com/2024/04/18/my-news-story']."
    )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _run(self, article_ids: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))

        try:
            contents = exa.get_contents(article_ids, text={"max_characters": 300})
            time.sleep(1)  # Enforce 1-second delay
            return contents
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise  # Let tenacity handle retry
            raise Exception(f"Exa API error: {str(e)}")

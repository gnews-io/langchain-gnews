from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Literal, Optional, Union

from gnews_io import Article, ArticlesResponse, Category, GNews, GNewsError
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field, model_validator

DateLike = Optional[Union[date, datetime]]

LANG = Field(default=None, description="2-letter language code, e.g. 'en', 'fr', 'de'.")
COUNTRY = Field(default=None, description="2-letter country code of the news sources, e.g. 'us', 'fr', 'in'.")


class GNewsSearchInput(BaseModel):
    q: str = Field(description='Keywords. Supports AND, OR, NOT and "exact phrases", e.g. \'"Apple" AND (iPhone OR Mac)\'.')
    lang: Optional[str] = LANG
    country: Optional[str] = COUNTRY
    from_date: DateLike = Field(
        default=None,
        description="Oldest publication date, ISO 8601, e.g. '2025-03-01'. The archive starts in 2020.",
    )
    to_date: DateLike = Field(default=None, description="Newest publication date, ISO 8601, e.g. '2025-03-31'.")
    sortby: Optional[Literal["publishedAt", "relevance"]] = Field(
        default=None, description="'publishedAt' (newest first, default) or 'relevance'."
    )


class GNewsTopHeadlinesInput(BaseModel):
    category: Category = Field(default="general", description="News category.")
    lang: Optional[str] = LANG
    country: Optional[str] = COUNTRY
    q: Optional[str] = Field(default=None, description="Optional keywords to narrow the headlines.")


class _GNewsTool(BaseTool):
    client: Any = Field(default=None, exclude=True)
    max_results: int = 10
    include_content: bool = True
    handle_tool_error: bool = True

    @model_validator(mode="before")
    @classmethod
    def _build_client(cls, values: Any) -> Any:
        if isinstance(values, dict):
            api_key = values.pop("api_key", None)
            if values.get("client") is None:
                values["client"] = GNews(api_key)
        return values

    def _fetch(self, fetch: Callable[..., ArticlesResponse], *args: Any, **params: Any) -> dict[str, Any]:
        try:
            response = fetch(*args, **params, max=self.max_results, truncate=not self.include_content)
        except GNewsError as e:
            raise ToolException(f"GNews API error: {e}") from e
        return {
            "total_articles": response.total_articles,
            "articles": [self._article(a) for a in response.articles],
        }

    def _article(self, article: Article) -> dict[str, Any]:
        result = {
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "url": article.url,
            "source": article.source.name,
            "published_at": article.published_at.isoformat(),
        }
        if not self.include_content:
            del result["content"]
        return result


class GNewsSearch(_GNewsTool):
    """Search news articles with the GNews API. The API key defaults to ``GNEWS_API_KEY``."""

    name: str = "gnews_search"
    description: str = (
        "Search news articles from 80,000+ sources in 41 languages by keywords, optionally filtered by "
        "language, source country and publication date (archive since 2020). Returns each article's "
        "title, description, text, URL, source and publication date. Use it to find news about a topic, "
        "company or person, including over a past period."
    )
    args_schema: type[BaseModel] = GNewsSearchInput

    def _run(
        self,
        q: str,
        lang: Optional[str] = None,
        country: Optional[str] = None,
        from_date: DateLike = None,
        to_date: DateLike = None,
        sortby: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._fetch(
            self.client.search, q, lang=lang, country=country, from_=from_date, to=to_date, sortby=sortby
        )


class GNewsTopHeadlines(_GNewsTool):
    """Top headlines from the GNews API. The API key defaults to ``GNEWS_API_KEY``."""

    name: str = "gnews_top_headlines"
    description: str = (
        "Get the current top headlines, ranked like Google News, for a category (general, world, nation, "
        "business, technology, entertainment, sports, science, health), a country and a language. "
        "Use it for news briefings, e.g. 'top business headlines in France today'."
    )
    args_schema: type[BaseModel] = GNewsTopHeadlinesInput

    def _run(
        self,
        category: str = "general",
        lang: Optional[str] = None,
        country: Optional[str] = None,
        q: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._fetch(self.client.top_headlines, category, lang=lang, country=country, q=q)

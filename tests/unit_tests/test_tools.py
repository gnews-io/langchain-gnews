from datetime import date, datetime, timezone

import pytest
from gnews_io import Article, ArticlesResponse, QuotaExceededError, Source

from langchain_gnews import GNewsSearch, GNewsTopHeadlines

ARTICLE = Article(
    id="a1",
    title="Title",
    description="Desc",
    content="Full text",
    url="https://example.com/a",
    image=None,
    published_at=datetime(2026, 10, 12, 8, 30, tzinfo=timezone.utc),
    lang="en",
    source=Source(id="s1", name="Example News", url="https://example.com", country="us"),
)


class FakeClient:
    def __init__(self, error=None):
        self.calls = []
        self.error = error

    def search(self, q, **params):
        return self._answer("search", {"q": q, **params})

    def top_headlines(self, category=None, **params):
        return self._answer("top_headlines", {"category": category, **params})

    def _answer(self, endpoint, params):
        self.calls.append((endpoint, params))
        if self.error:
            raise self.error
        return ArticlesResponse(total_articles=1, articles=[ARTICLE], raw={})


def test_search_returns_articles_for_the_model():
    tool = GNewsSearch(client=FakeClient())

    assert tool.invoke({"q": "NVIDIA"}) == {
        "total_articles": 1,
        "articles": [{
            "title": "Title",
            "description": "Desc",
            "content": "Full text",
            "url": "https://example.com/a",
            "source": "Example News",
            "published_at": "2026-10-12T08:30:00+00:00",
        }],
    }


def test_search_forwards_filters_and_parses_dates():
    client = FakeClient()

    GNewsSearch(client=client).invoke({
        "q": "NVIDIA",
        "lang": "en",
        "country": "us",
        "from_date": "2025-03-01",
        "to_date": "2025-03-31T23:59:59Z",
        "sortby": "relevance",
    })

    assert client.calls == [("search", {
        "q": "NVIDIA",
        "lang": "en",
        "country": "us",
        "from_": date(2025, 3, 1),
        "to": datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
        "sortby": "relevance",
        "max": 10,
        "truncate": False,
    })]


def test_max_results_sets_the_number_of_articles():
    client = FakeClient()

    GNewsSearch(client=client, max_results=25).invoke({"q": "NVIDIA"})

    assert client.calls[0][1]["max"] == 25


def test_include_content_false_drops_the_article_text():
    client = FakeClient()

    result = GNewsSearch(client=client, include_content=False).invoke({"q": "NVIDIA"})

    assert "content" not in result["articles"][0]
    assert client.calls[0][1]["truncate"] is True


def test_top_headlines_forwards_category_country_and_language():
    client = FakeClient()

    result = GNewsTopHeadlines(client=client).invoke({"category": "business", "country": "fr", "lang": "fr"})

    assert client.calls == [("top_headlines", {
        "category": "business",
        "lang": "fr",
        "country": "fr",
        "q": None,
        "max": 10,
        "truncate": False,
    })]
    assert result["articles"][0]["title"] == "Title"


def test_api_errors_are_returned_to_the_model():
    tool = GNewsSearch(client=FakeClient(error=QuotaExceededError("daily quota reached", status=403)))

    assert tool.invoke({"q": "NVIDIA"}) == "GNews API error: daily quota reached"


def test_missing_api_key_fails_at_construction(monkeypatch):
    monkeypatch.delenv("GNEWS_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GNEWS_API_KEY"):
        GNewsSearch()

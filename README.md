# langchain-gnews

LangChain tools for the [GNews API](https://gnews.io): news from 80,000+ sources in 41 languages.

| Tool | Name seen by the model | Use it for |
|---|---|---|
| `GNewsTopHeadlines` | `gnews_top_headlines` | Today's top headlines, ranked like Google News, by category, country and language: news briefings, daily digests |
| `GNewsSearch` | `gnews_search` | Articles about a topic, company or person, filtered by language, country and date, over an archive since 2020 |

Web search tools return the most relevant pages. These tools return dated news articles with their
source, filterable by country and language, including past periods.

## Install

```bash
pip install langchain-gnews
```

Get a free API key at [gnews.io/register](https://gnews.io/register), then:

```bash
export GNEWS_API_KEY="your-key"
```

## Use with an agent

Requires `langchain` and a model integration, e.g. `pip install langchain langchain-anthropic`.

```python
from langchain.agents import create_agent
from langchain_gnews import GNewsSearch, GNewsTopHeadlines

agent = create_agent("anthropic:claude-sonnet-5-5", tools=[GNewsTopHeadlines(), GNewsSearch()])
agent.invoke({"messages": [{"role": "user", "content": "Summarize this morning's top business headlines in France"}]})
```

## Use directly

```python
from langchain_gnews import GNewsSearch, GNewsTopHeadlines

GNewsTopHeadlines().invoke({"category": "business", "country": "fr", "lang": "fr"})
GNewsSearch().invoke({"q": '"NVIDIA" AND earnings', "lang": "en", "from_date": "2025-01-01", "to_date": "2025-03-31"})
```

Both return `{"total_articles": int, "articles": [{"title", "description", "content", "url", "source", "published_at"}]}`.

## Options

| Option | Default | Effect |
|---|---|---|
| `api_key` | `GNEWS_API_KEY` | GNews API key |
| `max_results` | `10` | Articles per call (up to your plan's limit) |
| `include_content` | `True` | Include the article text. Set to `False` to save tokens. |

API errors (invalid key, quota reached, rate limit) are returned to the model as tool errors
instead of raising.

## What your plan returns

| Plan | Archive | Freshness | Article text |
|---|---|---|---|
| Free | last 30 days | 12-hour delay | truncated |
| Paid | since 2020 | real time | full |

See [pricing](https://gnews.io/pricing) and the [API documentation](https://docs.gnews.io).

## Tests

```bash
pip install -e ".[test]"
pytest                      # unit tests
GNEWS_API_KEY=... pytest    # adds integration tests against the live API
```

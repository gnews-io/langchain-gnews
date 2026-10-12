from langchain_tests.unit_tests import ToolsUnitTests

from langchain_gnews import GNewsSearch, GNewsTopHeadlines


class TestGNewsSearchStandard(ToolsUnitTests):
    @property
    def tool_constructor(self):
        return GNewsSearch

    @property
    def tool_constructor_params(self):
        return {"api_key": "test-key"}

    @property
    def tool_invoke_params_example(self):
        return {"q": "NVIDIA earnings", "from_date": "2025-01-01"}

    @property
    def init_from_env_params(self):
        return {"GNEWS_API_KEY": "test-key"}, {}, {}


class TestGNewsTopHeadlinesStandard(ToolsUnitTests):
    @property
    def tool_constructor(self):
        return GNewsTopHeadlines

    @property
    def tool_constructor_params(self):
        return {"api_key": "test-key"}

    @property
    def tool_invoke_params_example(self):
        return {"category": "business", "country": "fr"}

    @property
    def init_from_env_params(self):
        return {"GNEWS_API_KEY": "test-key"}, {}, {}

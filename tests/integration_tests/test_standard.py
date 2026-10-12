import os

import pytest
from langchain_tests.integration_tests import ToolsIntegrationTests

from langchain_gnews import GNewsSearch, GNewsTopHeadlines

pytestmark = pytest.mark.skipif(not os.environ.get("GNEWS_API_KEY"), reason="GNEWS_API_KEY not set")


class TestGNewsSearchIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self):
        return GNewsSearch

    @property
    def tool_invoke_params_example(self):
        return {"q": "NVIDIA earnings"}


class TestGNewsTopHeadlinesIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self):
        return GNewsTopHeadlines

    @property
    def tool_invoke_params_example(self):
        return {"category": "business", "country": "fr"}

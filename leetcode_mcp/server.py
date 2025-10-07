from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from .api import LeetCodeAPI
from .config import settings


async def create_server(leetcode_session: str | None = None, csrftoken: str | None = None) -> FastMCP:
    server = FastMCP(name="LeeteCodeMCPServer")
    
    session = leetcode_session or settings.leetcode_session
    token = csrftoken or settings.leetcode_csrftoken

    api = LeetCodeAPI(
        leetcode_session=session,
        csrftoken=token
    )

    @server.tool(name="fetch_problem_plain_text", description="Fetches the plain text content of a LeetCode problem given its URL.")
    def fetch_problem_plain_text(link: str) -> str:
        text, _ = api.fetch_problem_plain_text(link)
        return text

    @server.tool(name="generate_template", description="Generates a language-specific code template for a given LeetCode problem slug.")
    def generate_template(problem_slug: str, code_lang: str) -> str:
        return api.generate_template(problem_slug, code_lang)

    @server.tool(name="run_code", description="Executes code against the example test cases for a LeetCode problem and returns the results.")
    def run_code(problem_slug: str, code_lang: str, code: str) -> dict:
        return api.run_code(problem_slug, code_lang, code)

    @server.tool(name="submit_code", description="Submits the code for a LeetCode problem for evaluation against the full test suite.")
    def submit_code(problem_slug: str, code_lang: str, code: str) -> dict:
        return api.submit_code(problem_slug, code_lang, code)

    @server.tool(name="get_daily_challenge", description="Retrieves today's LeetCode Daily Challenge problem with complete details, including problem description, constraints, and examples.")
    def get_daily_challenge() -> dict:
        return api.fetch_daily_challenge()

    @server.tool(name="get_problem", description="Retrieves details about a specific LeetCode problem, including its description, examples, constraints, and related information.")
    def get_problem(titleSlug: str) -> dict:
        return api.fetch_problem_simplified(titleSlug)

    @server.tool(name="search_problems", description="Searches for LeetCode problems based on multiple filter criteria including categories, tags, difficulty levels, and keywords, with pagination support.")
    def search_problems(
        category: str = "all-code-essentials",
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        searchKeywords: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        return api.search_problems(
            category=category,
            tags=tags,
            difficulty=difficulty,
            search_keywords=searchKeywords,
            limit=limit,
            offset=offset,
        )

    return server

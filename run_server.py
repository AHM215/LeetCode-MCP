import asyncio
import logging
import click
from dotenv import load_dotenv
from leetcode_mcp.server import create_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--leetcode-session",
    envvar="LEETCODE_SESSION",
    help="LeetCode session cookie.",
)
@click.option(
    "--csrftoken",
    envvar="LEETCODE_CSRFTOKEN",
    help="LeetCode CSRF token.",
)
def main(leetcode_session: str, csrftoken: str):
    load_dotenv()

    async def _run():
        s = await create_server(leetcode_session, csrftoken)
        logger.info("Starting LeetCode MCP server...")
        return s

    s = asyncio.run(_run())
    s.run()


if __name__ == "__main__":
    main()

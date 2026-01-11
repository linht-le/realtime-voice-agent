from pathlib import Path

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool, tool
from langchain_tavily import TavilySearch
from sqlalchemy import select

from app.backend.config import get_settings
from app.backend.constants.descriptions import (
    LIST_DIRECTORY_DESCRIPTION,
    READ_FILE_DESCRIPTION,
    SEARCH_DESCRIPTION,
    SEARCH_FILES_DESCRIPTION,
    SEARCH_IN_FILE_DESCRIPTION,
)
from app.backend.database.models import Tool
from app.backend.database.session import AsyncSessionLocal
from app.backend.logger import get_logger
from app.backend.services.rag_service import RAGService

logger = get_logger(__name__)


@tool(description=SEARCH_IN_FILE_DESCRIPTION)
def search_in_file(file_path: str, question: str) -> str:
    """Search semantic content within a specific file"""
    try:
        rag = RAGService()
        return rag.search_in_file(file_path, question)
    except Exception as e:
        logger.error(f"Failed to search in {file_path}: {e}")
        return f"Error: {str(e)}"


@tool(description=READ_FILE_DESCRIPTION)
def read_file(file_path: str) -> str:
    """Read file contents"""
    try:
        full_path = Path(file_path).expanduser().resolve()

        if not full_path.exists():
            return f"Error: File '{file_path}' not found"

        if not full_path.is_file():
            return f"Error: '{file_path}' is not a file"

        return f"Content of {file_path}:\n\n{full_path.read_text(encoding='utf-8')}"

    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return f"Error: {str(e)}"


@tool(description=SEARCH_FILES_DESCRIPTION)
def search_files(pattern: str, search_path: str = ".") -> str:
    """Find files by pattern"""
    try:
        base_path = Path(search_path).expanduser().resolve()

        if not base_path.exists():
            return f"Error: Directory '{search_path}' not found"

        matches = list(base_path.glob(pattern))

        if not matches:
            return f"No files found matching '{pattern}'"

        paths = [str(p) for p in matches[:100]]
        result = f"Found {len(matches)} files:\n\n" + "\n".join(f"- {p}" for p in paths)

        if len(matches) > 100:
            result += f"\n\n... and {len(matches) - 100} more"

        return result

    except Exception as e:
        logger.error(f"Failed to search files: {e}")
        return f"Error: {str(e)}"


@tool(description=LIST_DIRECTORY_DESCRIPTION)
def list_directory(directory_path: str = ".") -> str:
    """List directory contents"""
    try:
        full_path = Path(directory_path).expanduser().resolve()

        if not full_path.exists():
            return f"Error: Directory '{directory_path}' not found"

        if not full_path.is_dir():
            return f"Error: '{directory_path}' is not a directory"

        entries = sorted(full_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        dirs = [e.name + "/" for e in entries if e.is_dir()]
        files = [e.name for e in entries if e.is_file()]

        result = f"Contents of {directory_path}:\n\n"

        if dirs:
            result += "Directories:\n" + "\n".join(f"  {d}" for d in dirs[:50])
            if len(dirs) > 50:
                result += f"\n  ...{len(dirs) - 50} more"
            result += "\n\n"

        if files:
            result += "Files:\n" + "\n".join(f"  {f}" for f in files[:50])
            if len(files) > 50:
                result += f"\n  ...{len(files) - 50} more"

        if not dirs and not files:
            result += "(empty directory)"

        return result

    except Exception as e:
        logger.error(f"Failed to list directory: {e}")
        return f"Error: {str(e)}"


TOOL_GROUPS = {
    "web_search": {"impl": "search", "description": SEARCH_DESCRIPTION},
    "search_in_file": {"impl": search_in_file, "description": SEARCH_IN_FILE_DESCRIPTION},
    "read_file": {"impl": read_file, "description": READ_FILE_DESCRIPTION},
    "search_files": {"impl": search_files, "description": SEARCH_FILES_DESCRIPTION},
    "list_directory": {"impl": list_directory, "description": LIST_DIRECTORY_DESCRIPTION},
}


class ToolService:
    @staticmethod
    async def get_search_tools() -> list[BaseTool]:
        """Get search tools (Tavily if configured, otherwise DuckDuckGo)"""
        settings = get_settings()

        if settings.TAVILY_API_KEY:
            try:
                return [
                    TavilySearch(
                        tavily_api_key=settings.TAVILY_API_KEY,
                        max_results=3,
                        include_answer=True,
                        include_raw_content=False,
                        include_images=False,
                        search_depth="basic",
                        description=SEARCH_DESCRIPTION,
                    )
                ]
            except Exception:
                pass

        return [DuckDuckGoSearchResults(num_results=5, description=SEARCH_DESCRIPTION)]

    @staticmethod
    async def get_all_tools() -> list[BaseTool]:
        """Get all enabled tools with custom descriptions"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Tool))
                db_tools = {t.name: t for t in result.scalars().all()}
        except Exception as e:
            logger.warning(f"Failed to fetch tool statuses: {e}")
            db_tools = {}

        tools = []
        for tool_name, tool_config in TOOL_GROUPS.items():
            db_tool = db_tools.get(tool_name)

            if db_tool and not db_tool.enabled:
                continue

            if tool_name == "web_search":
                base_tools = await ToolService.get_search_tools()
            else:
                base_tools = [tool_config["impl"]]

            if db_tool and db_tool.description:
                base_tools = [
                    tool.model_copy(update={"description": db_tool.description})
                    for tool in base_tools
                ]

            tools.extend(base_tools)

        return tools

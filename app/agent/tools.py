from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool, tool
from langchain_tavily import TavilySearch

from app.config import get_settings
from app.rag.retriever import DocumentRetriever

# Constants
SEARCH_DESCRIPTION = "Search the internet for current events, locations, addresses, and public information. Use this for real-time data and information not in internal documents."


# Search Tools
def get_search_tools() -> list[BaseTool]:
    """Get search tools (Tavily or DuckDuckGo)"""
    settings = get_settings()

    if settings.TAVILY_API_KEY:
        try:
            return [
                TavilySearch(
                    tavily_api_key=settings.TAVILY_API_KEY,
                    max_results=5,
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


# RAG Tool
def get_document_query_tool() -> BaseTool:
    """Get tool to query vector database"""
    retriever = DocumentRetriever()

    @tool
    def query_documents(question: str) -> str:
        """Search project documentation and internal knowledge base. ALWAYS use this tool when user asks about:
        - Project implementation details (architecture, code, components)
        - Technical specifications and configurations
        - "How does X work in this/our/my project?"
        - "What is X in the documentation/docs?"
        - Any question about uploaded documents, manuals, or policies
        Do NOT use for current events, weather, or general internet information."""
        return retriever.query(question)

    return query_documents

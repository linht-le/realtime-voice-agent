import logging

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config import get_settings

logger = logging.getLogger(__name__)


class DocumentRetriever:
    def __init__(self):
        settings = get_settings()
        self.collection_name = settings.COLLECTION_NAME
        self.qdrant_url = settings.QDRANT_URL
        self.vector_store = None

    def _init_store(self):
        if self.vector_store:
            return
        client = QdrantClient(url=self.qdrant_url)
        self.vector_store = QdrantVectorStore(
            client=client,
            collection_name=self.collection_name,
            embedding=OpenAIEmbeddings(),
        )

    def query(self, question: str, k: int = 3) -> str:
        """Query vector database"""
        logger.info(f"RAG query: '{question}'")
        self._init_store()
        if not self.vector_store:
            raise RuntimeError("Vector store initialization failed")

        results = self.vector_store.similarity_search(question, k=k)
        logger.info(f"Found {len(results)} results")

        if not results:
            return "No relevant information found."

        response = f"Found {len(results)} relevant sections:\n\n"
        for i, doc in enumerate(results, 1):
            response += f"Section {i}:\n{doc.page_content}\n\n"

        return response.strip()

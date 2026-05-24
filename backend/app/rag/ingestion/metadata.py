from typing import Dict, List

from langchain_core.documents import Document


def chunks_to_documents(
    chunks: List[Dict],
) -> List[Document]:
    """
    Convert chunk dicts into LangChain Documents with metadata.
    """

    documents: List[Document] = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["content"],
                metadata={
                    "start_time": chunk.get("start_time"),
                    "end_time": chunk.get("end_time"),
                },
            )
        )

    return documents

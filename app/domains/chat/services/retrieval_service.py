from typing import Any, Dict, List


def format_chroma_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert ChromaDB query result into a clean list for the LLM."""

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted_results = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        formatted_results.append({
            "matched_text": document,
            "metadata": metadata,
            "distance": distance,
        })

    return formatted_results
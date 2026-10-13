from app.domains.chat.services.retrieval_service import format_chroma_results


def test_format_chroma_results_returns_formatted_results():
    results = {
        "documents": [
            [
                "Dark chocolate contains cocoa.",
                "White chocolate contains cocoa butter.",
            ]
        ],
        "metadatas": [
            [
                {
                    "source": "faq",
                    "type": "answer",
                },
                {
                    "source": "inventory",
                    "product_id": "choco-002",
                },
            ]
        ],
        "distances": [
            [
                0.12,
                0.25,
            ]
        ],
    }

    result = format_chroma_results(results)

    assert result == [
        {
            "matched_text": "Dark chocolate contains cocoa.",
            "metadata": {
                "source": "faq",
                "type": "answer",
            },
            "distance": 0.12,
        },
        {
            "matched_text": "White chocolate contains cocoa butter.",
            "metadata": {
                "source": "inventory",
                "product_id": "choco-002",
            },
            "distance": 0.25,
        },
    ]


def test_format_chroma_results_returns_empty_list_when_results_empty():
    results = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }

    result = format_chroma_results(results)

    assert result == []


def test_format_chroma_results_handles_missing_keys():
    result = format_chroma_results({})

    assert result == []


def test_format_chroma_results_uses_shortest_list_length():
    results = {
        "documents": [
            [
                "Document 1",
                "Document 2",
            ]
        ],
        "metadatas": [
            [
                {
                    "source": "faq",
                }
            ]
        ],
        "distances": [
            [
                0.1,
                0.2,
            ]
        ],
    }

    result = format_chroma_results(results)

    assert result == [
        {
            "matched_text": "Document 1",
            "metadata": {
                "source": "faq",
            },
            "distance": 0.1,
        }
    ]
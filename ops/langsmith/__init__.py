"""
LangSmith Ops Layer

Provides:
- Tracing setup for all LangChain calls
- Dataset management for evaluations
- Custom evaluators (faithfulness, relevance, actionability)
- Evaluation runner with LangSmith logging
"""
from .setup import (
    get_langsmith_client,
    setup_tracing,
    create_or_get_dataset,
    upload_examples_to_dataset,
    load_test_set_to_langsmith
)

__all__ = [
    "get_langsmith_client",
    "setup_tracing",
    "create_or_get_dataset",
    "upload_examples_to_dataset",
    "load_test_set_to_langsmith",
]

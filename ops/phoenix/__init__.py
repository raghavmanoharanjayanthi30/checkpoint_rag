"""
Phoenix/Arize Ops Layer

Provides OpenTelemetry tracing for RAG pipeline observability.
"""
from .instrument import setup_phoenix_tracing

__all__ = ["setup_phoenix_tracing"]

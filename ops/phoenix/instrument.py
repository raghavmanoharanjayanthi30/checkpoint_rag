"""
Phoenix/Arize Instrumentation

Sets up OpenTelemetry tracing with hosted Arize Phoenix for observability.
Captures:
- Retrieval latency
- Generation latency  
- Token usage
- Document IDs returned

Uses hosted Arize Phoenix (app.phoenix.arize.com) - no local Phoenix install needed.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def setup_phoenix_tracing(project_name: str = "checkpoint-rag"):
    """
    Initialize OpenTelemetry tracing with hosted Arize Phoenix.
    
    Requires ARIZE_SPACE_ID and ARIZE_API_KEY in .env
    """
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from openinference.instrumentation.langchain import LangChainInstrumentor
    
    # Check for Arize credentials
    space_id = os.getenv("ARIZE_SPACE_ID")
    api_key = os.getenv("ARIZE_API_KEY")
    
    if not space_id or not api_key:
        print("⚠️  ARIZE_SPACE_ID or ARIZE_API_KEY not set in .env")
        print("   Skipping Phoenix tracing setup.")
        return None
    
    print(f"🔗 Connecting to Arize Phoenix (hosted)...")
    
    # Create resource with project name
    resource = Resource.create({"service.name": project_name})
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter for Arize
    exporter = OTLPSpanExporter(
        endpoint="https://app.phoenix.arize.com/v1/traces",
        headers={
            "authorization": f"Bearer {api_key}",
        }
    )
    
    # Add span processor
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    
    # Set as global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument LangChain
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    
    print(f"✅ Phoenix tracing enabled for project: {project_name}")
    print(f"📊 View traces at: https://app.phoenix.arize.com")
    
    return tracer_provider


def run_sample_queries(n_queries: int = 5):
    """
    Run sample queries through the RAG pipeline to generate traces.
    
    Args:
        n_queries: Number of queries to run
    """
    import json
    
    # Add project root to path
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.insert(0, project_root)
    
    from src.retrieve import get_documents, format_docs, create_bm25_retriever
    from src.generate import create_rag_chain
    from src.ingest import get_file_paths, create_langchain_documents, chunk_documents, embed_chunks
    
    print(f"\n📊 Running {n_queries} sample queries to generate traces...")
    
    # Build pipeline
    print("Building RAG pipeline...")
    file_grouping = get_file_paths("./corpus")
    docs = create_langchain_documents(file_grouping)
    chunks = chunk_documents(docs)
    vectorstore = embed_chunks(chunks)
    bm25_retriever = create_bm25_retriever(chunks)
    rag_chain = create_rag_chain(vectorstore, bm25_retriever)
    print("✅ Pipeline ready")
    
    # Load test queries
    with open("evals/test_set.json") as f:
        data = json.load(f)
    
    queries = [q["query"] for q in data.get("queries", [])][:n_queries]
    
    # Run queries
    results = []
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{n_queries}] {query[:50]}...")
        try:
            response = rag_chain.invoke(query)
            results.append({
                "query": query,
                "answer": response.answer,
                "confidence": response.confidence
            })
            print(f"    ✅ {response.confidence} confidence")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({"query": query, "error": str(e)})
    
    print(f"\n✅ Completed {len(results)} queries")
    print("📊 View traces at: https://app.phoenix.arize.com")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phoenix Instrumentation")
    parser.add_argument("--queries", type=int, default=5, help="Number of sample queries")
    parser.add_argument("--project", default="checkpoint-rag", help="Project name")
    args = parser.parse_args()
    
    # Setup tracing
    tracer = setup_phoenix_tracing(project_name=args.project)
    
    if tracer:
        # Run sample queries
        run_sample_queries(n_queries=args.queries)
    else:
        print("Tracing not configured. Set ARIZE_SPACE_ID and ARIZE_API_KEY in .env")

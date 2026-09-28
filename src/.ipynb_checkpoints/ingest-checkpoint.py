import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader

def get_file_paths(root_dir_path):
    from collections import defaultdict
    doc_folder_names = ['tickets', 'runbooks', 'product-docs']
    
    all_file_paths = []

    for folder in doc_folder_names:
        folder_path = os.path.join(root_dir_path, folder)
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                # Skip hidden files like .DS_Store
                if not filename.startswith('.'):
                    all_file_paths.append(os.path.join(dirpath, filename))

    file_grouping = defaultdict(list)
    for path in all_file_paths:
        file_type = path.split('.')[-1]
        if file_type not in file_grouping:
            file_grouping[file_type] = [path]
        else:
            file_grouping[file_type].append(path)

    return file_grouping

def create_langchain_documents(file_grouping):
    from langchain_community.document_loaders import BSHTMLLoader
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.document_loaders import UnstructuredMarkdownLoader
    from langchain_core.documents import Document

    html_docs = []
    for html_path in file_grouping['html']:
        html_loader = BSHTMLLoader(html_path)
        html_doc = html_loader.load()
        html_docs += html_doc

    pdf_docs = []
    i = 0
    for pdf_path in file_grouping['pdf']:
        pdf_loader = PyPDFLoader(pdf_path)
        pdf_doc = pdf_loader.load()
        pdf_docs += pdf_doc
    
    md_docs = []
    for md_path in file_grouping['md']:
        md_loader = UnstructuredMarkdownLoader(md_path, mode = 'single')
        md_doc = md_loader.load()
        md_docs += md_doc

    # Add doc_type metadata to each category
    for doc in html_docs:
        doc.metadata['doc_type'] = 'ticket'
    
    for doc in pdf_docs:
        doc.metadata['doc_type'] = 'runbook'
    
    for doc in md_docs:
        doc.metadata['doc_type'] = 'product-doc'

    for doc in pdf_docs:
        doc.metadata['doc_type'] = 'runbook'
        # Extract subcategory from path like "runbooks/incident-response/file.pdf"
        path_parts = doc.metadata['source'].split('/')
        if 'runbooks' in path_parts:
            idx = path_parts.index('runbooks')
            if idx + 1 < len(path_parts):
                doc.metadata['category'] = path_parts[idx + 1]

    for doc in md_docs:
        doc.metadata['doc_type'] = 'product-doc'
        path_parts = doc.metadata['source'].split('/')
        if 'product-docs' in path_parts:
            idx = path_parts.index('product-docs')
            if idx + 1 < len(path_parts):
                doc.metadata['category'] = path_parts[idx + 1]

    all_docs = html_docs + pdf_docs + md_docs
    return all_docs

def chunk_documents(documents):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    chunks = text_splitter.split_documents(documents)
    #print(f"Split {len(all_docs)} docs into {len(chunks)} chunks")
    
    import hashlib

    updated_chunks = []
    for chunk in chunks:
        # Create unique ID from content hash
        chunk_id = hashlib.md5(chunk.page_content.encode()).hexdigest()
        chunk.metadata['id'] = chunk_id
        updated_chunks.append(chunk)

    return updated_chunks

def embed_chunks(chunks):
    from dotenv import load_dotenv
    load_dotenv()

    from langchain_openai import OpenAIEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone, ServerlessSpec
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Initialize Pinecone client
    pc = Pinecone()

    vectorstore = PineconeVectorStore(
        index_name="helix-support-two",
        embedding=embeddings
    )

    # from langchain_community.retrievers import BM25Retriever
    # retriever = BM25Retriever.from_documents(chunks)

    # return {
    #     'bm25': retriever,
    #     'similarity_search': vectorstore
    # }
    return vectorstore

def run_ingestion(corpus_file_path):
    file_grouping = get_file_paths(corpus_file_path)
    docs = create_langchain_documents(file_grouping)
    chunks = chunk_documents(docs)
    retriever_dict = embed_chunks(chunks)
    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="./corpus", help="Path to corpus folder")
    args = parser.parse_args()
    
    run_ingestion(args.corpus)

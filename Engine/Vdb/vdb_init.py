from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import logging
import os
from dotenv import load_dotenv

from django.conf import settings

load_dotenv()
logger = logging.getLogger(__name__)

v_db_path = os.path.join(os.getcwd(), "vdb")
if not os.path.exists(v_db_path):
    os.mkdir(v_db_path)

try:

    file_path = os.path.join(
        os.getcwd(),
        "media",
        "RAG_docs",
    )
    
    print("we got here")

    # Create a PyPDFLoader
    loader = DirectoryLoader(file_path,glob="*.pdf",loader_cls=PyPDFLoader)

    # Ensure documents are loaded
    documents = loader.load()
    if not documents:
        print("No documents were loaded. Check the file path and file format.")
        
    # splitting the text into
    child_splitter  = RecursiveCharacterTextSplitter(chunk_size=1500)

    vectorstore = Chroma(
        collection_name="manifesto",
        embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("openai_api_key","")),
        persist_directory=v_db_path,
    )
    store = InMemoryStore()
    
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=None,
    )
    
    retriever.add_documents(documents)

    # persiste the db to disk
    vectorstore.persist()
    print("vector database initializion is complete")
except Exception as e:
    print(f"An error occurred while initializing the database:\n{e}")

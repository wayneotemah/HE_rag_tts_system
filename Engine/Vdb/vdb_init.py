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

class DocSeachService:
    def __init__(self):
        """
        Initialize the database with the documents in the RAG_docs folder
        """
        
        try:
            logging.info("Initializing the database...")

            file_path = os.path.join(
                os.getcwd(),
                "media",
                "RAG_docs",
            )
            # Create a PyPDFLoader
            loader = DirectoryLoader(file_path,glob="*.pdf",loader_cls=PyPDFLoader)

            # Ensure documents are loaded
            documents = loader.load()
            if not documents:
                print("No documents were loaded. Check the file path and file format.")
                
            # splitting the text into
            child_splitter  = RecursiveCharacterTextSplitter(chunk_size=1500)

            self.vectorstore = Chroma(
                collection_name="manifesto",
                embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv("openai_api_key","")),
                persist_directory=v_db_path,
            )
            store = InMemoryStore()
            
            self.retriever = ParentDocumentRetriever(
                vectorstore=self.vectorstore,
                docstore=store,
                child_splitter=child_splitter,
                parent_splitter=None,
            )
            self.retriever.add_documents(documents)

            # persiste the db to disk
            self.vectorstore.persist()
        except Exception as e:
            logging.exception(f"An error occurred while initializing the database:\n{e}")
            raise e

    def search(self, query):
        smaller_search = self.vectorstore.similarity_search(query)
        results = self.retriever.get_relevant_documents(query)
        return  results
    
    
doc_search_service = DocSeachService()
__all__ = ["doc_search_service"]
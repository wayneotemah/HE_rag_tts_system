import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
import logging
from django.conf import settings


logger = logging.getLogger(__name__)


class VecotrDBManager:
    def __init__(self):
        self.persist_directory = os.path.join(settings.BASE_DIR, "vdb")
        self.embeddings = self.init_openai_embeddings()

    def init_openai_embeddings(self):
        embeddings_model = OpenAIEmbeddings(
            openai_api_key="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",
        )
        return embeddings_model

    def _get_db(self):
        # persisted database from disk, and use it as normal.
        vectordb = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )
        return vectordb

    def create_retriever(self):
        logger.info("Creating retriever...")
        retriever = self._get_db().as_retriever()
        return retriever

    def create_qa_chain(self):
        logger.info("Creating QA chain...")
        llm = OpenAI(
            openai_api_key="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",
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.create_retriever(),
            return_source_documents=True,
        )
        return qa_chain


vecotrdb = VecotrDBManager()


__all__ = ["vecotrdb"]
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document
import uuid
from langchain_community.vectorstores import FAISS


class MultiDocumentRetriever:

    def __init__(
        self, embedding_model, text, tab, base64_img, tab_summaries, image_summaries
    ):
        self.__embedding_model = embedding_model
        self.__documents = text + tab + base64_img
        self.__summary_docs = text + tab_summaries + image_summaries
        self.__docstore = InMemoryStore()
        self.__id_key = "doc_id"

    def create_retriever(self):
        print("Creating MultiDocumentRetriever")
        embeddings = self.__embedding_model
        doc_contents = self.__documents
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [
            Document(page_content=s, metadata={self.__id_key: doc_ids[i]})
            for i, s in enumerate(self.__summary_docs)
        ]
        

        self.__docstore.mset(list(zip(doc_ids, doc_contents)))

        vectorstore = FAISS.from_documents(summary_docs, embedding=embeddings)
        retriever_multi_vector_img = MultiVectorRetriever(
            vectorstore=vectorstore,
            docstore=self.__docstore,
            id_key=self.__id_key,
        )
        return retriever_multi_vector_img

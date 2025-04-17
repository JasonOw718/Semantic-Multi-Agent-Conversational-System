from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from utils import split_image_text_types

class MultiModalRAGChain:
    def __init__(self, retriever_multi_vector_img, llm):
        self.__retriever_multi_vector_img = retriever_multi_vector_img
        self.__llm = llm

    def __img_prompt_func(self, data_dict):
        """
        Join the context into a single string
        """
        formatted_texts = "\n".join(data_dict["context"]["texts"])
        messages = [
            {
                "type": "text",
                "text": (
                    "You are tasked with providing a detailed answer to the user's question.\n"
                    "You will be given a mix of text, tables, and images (usually charts or graphs).\n"
                    "Use all available information to answer the user's question based on the facts and context provided.\n"
                    "Incorporate any relevant graphs, tables, or images into your explanation to support your response.\n"
                    f"User-provided question: {data_dict['question']}\n\n"
                    "Text, tables, and images:\n"
                    f"{formatted_texts}"
                ),
            }
        ]

        # Adding image(s) to the messages if present
        if data_dict["context"]["images"]:
            for image in data_dict["context"]["images"]:
                messages.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    }
                )
        return [HumanMessage(content=messages)]

    def create_chain(self):
        print("Creating multimodal RAG chain")
        chain_multimodal_rag = (
            {
                "context": self.__retriever_multi_vector_img
                | RunnableLambda(split_image_text_types),
                "question": RunnablePassthrough(),
            }
            | RunnableLambda(self.__img_prompt_func)
            | self.__llm
            | StrOutputParser()
        )
        return chain_multimodal_rag

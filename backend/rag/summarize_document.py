import os
from langchain_core.messages import HumanMessage
from utils import encode_image
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from utils import IMAGE_EXTENSIONS
from langchain_google_genai import ChatGoogleGenerativeAI


class DocumentSummarizer:

    def __init__(self, llm, api_keys):
        self.__llm = llm
        self.__api_keys = api_keys

    def __summarize_image(self, prompt, img_base64):
        for api_key in self.__api_keys:
            try:
                chat = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0,
                    google_api_key=api_key
                )
                msg = chat.invoke(
                    [
                        HumanMessage(
                            content=[
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_base64}"
                                    },
                                },
                            ]
                        )
                    ]
                )
                return msg.content
            except Exception as e:
                print(f"Error with API key {api_key}: {e}")

        raise RuntimeError("All API keys failed.")

    def generate_img_summaries(self, image_folder):
        print("---Summarizing images---")
        image_folders = [f"{image_folder}/{f}" for f in os.listdir(image_folder)]
        img_base64_list = []

        image_summaries = []
        for path in image_folders:

            prompt = """You are an assistant tasked with summarizing images for retrieval. \
            These summaries will be embedded and used to retrieve the raw image. \
            Give a concise summary of the image that is well optimized for retrieval."""

            for img_file in sorted(os.listdir(path)):
                extension = os.path.splitext(img_file)[1]
                if extension in IMAGE_EXTENSIONS:
                    img_path = os.path.join(path, img_file)
                    print(f"Summarizing image: {img_path}")
                    base64_image = encode_image(img_path)
                    img_base64_list.append(base64_image)
                    image_summaries.append(self.__summarize_image(prompt, base64_image))
        return img_base64_list, image_summaries

    def generate_tab_summaries(self, tab):
        print("---Summarizing tables---")
        prompt_text = """You are an assistant tasked with summarizing tables for retrieval. \
            These summaries will be embedded and used to retrieve the raw table elements. \
            Explain and give a summary of the table that is well optimized for retrieval. Table {element} """
        prompt = PromptTemplate(template=prompt_text, input_variables=["element"])
        summarize_chain = (
            {"element": lambda x: x} | prompt | self.__llm | StrOutputParser()
        )
        table_summaries = summarize_chain.batch(tab, {"max_concurrency": 2})
        return table_summaries

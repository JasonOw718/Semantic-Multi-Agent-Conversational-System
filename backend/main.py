from document_extraction.unstructured_extraction.unstruct_extraction import (
    UnstructuredDocumentExtraction,
)
from document_extraction.azure_table_extraction.azure_extraction import (
    AzureDocumentExtraction,
)
from document_extraction.azure_table_extraction.merge_document_table import (
    DocumentTableMerger,
)

from document_extraction.azure_table_extraction.merged_table_identifier import (
    MergedTableIdentifier,
)
from document_extraction.azure_table_extraction.table_organizer import TableOrganizer
from document_extraction.azure_table_extraction.process_table import TableProcessor
from document_extraction.azure_table_extraction.table_converter.html_table_converter import (
    HTMLTableConverter,
)
from document_extraction.azure_table_extraction.table_converter.csv_to_sql_converter import (
    CSVToSQLConverter,
)
from llm_config import (
    gemini,
    backup_gemini,
    groq,
    backup_groq,
    embeddings,
    gemini_backup,
    gemini_key,
    gemini_second_backup,
)
from rag.summarize_document import DocumentSummarizer
from rag.create_rag_chain import MultiModalRAGChain
from rag.create_retriever import MultiDocumentRetriever
import os
import base64
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from tools.sql_agent_factory import SQLAgentToolFactory
from tools.models import ResponseFormatter
from agent.graph_builder import GraphBuilder
import asyncio
import concurrent.futures
from fastapi.responses import JSONResponse
from PIL import Image
import io
from utils import (
    split_image_text_types,
    EXTENSIONS,
    IMAGE_EXTENSIONS,
    convert_to_pdf,
    copy_image_to_folder,
    delete_folder,
)
import pickle

load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXTRACTED_DATA_PATH = os.getenv("EXTRACTED_DATA_PATH")
INITIAL_DOCUMENT_PATH = os.getenv("INITIAL_DOCUMENT_PATH")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_DOCUMENT_INTELLEGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLEGENCE_KEY")
DATABASE_FOLDER_PATH = os.getenv("DATABASE_FOLDER_PATH")
CSV_FOLDER_PATH = os.getenv("CSV_FOLDER_PATH")

llm_with_fallbacks = gemini.with_fallbacks([backup_gemini, groq, backup_groq])
llm_with_fallbacks2 = groq.with_fallbacks([backup_groq, gemini, backup_gemini])


def extract_with_azure():
    # azure_document_extractor = AzureDocumentExtraction(
    #     endpoint=AZURE_ENDPOINT,
    #     key=AZURE_DOCUMENT_INTELLEGENCE_KEY,
    #     input_path=INITIAL_DOCUMENT_PATH,
    #     supported_extension=EXTENSIONS
    # )

    # extracted_content = azure_document_extractor.extract_content_from_folder()
    # table_processor = TableProcessor(
    #     merged_table_identifier=MergedTableIdentifier(),
    #     document_table_merger=DocumentTableMerger(),
    #     table_organizer=TableOrganizer(),
    #     content=extracted_content,
    #     html_table_converter=HTMLTableConverter(CSV_FOLDER_PATH, llm_with_fallbacks2),
    #     csv_to_sql_converter=CSVToSQLConverter(DATABASE_FOLDER_PATH, CSV_FOLDER_PATH),
    # )

    # table_processor.merge_and_organize_tables()

    factory = SQLAgentToolFactory(
        database_folder=DATABASE_FOLDER_PATH,
        llm=llm_with_fallbacks,
        response_structure=ResponseFormatter,
    )

    # Create all tools
    all_tools = factory.create_tools()
    return all_tools


def extract_with_partition():

    unstrcutured_document_extractor = UnstructuredDocumentExtraction(
        INITIAL_DOCUMENT_PATH, EXTRACTED_DATA_PATH
    )
    unstrcutured_document_extractor.extract_content_from_folder()
    doc_summarizer = DocumentSummarizer(llm_with_fallbacks, [gemini_key, gemini_second_backup, gemini_backup])
    img_base64_list, image_summaries = doc_summarizer.generate_img_summaries(
        EXTRACTED_DATA_PATH
    )

    def write_list_to_file(filename, data_list):
        """Writes a list of items to a text file, each on a new line."""
        with open(filename, "w", encoding="utf-8") as file:
            for item in data_list:
                file.write(str(item) + "\n")  # Convert item to string and write

    write_list_to_file("output.txt", image_summaries)
    print("List written to file successfully!")

    tab_summaries = doc_summarizer.generate_tab_summaries(
        unstrcutured_document_extractor.tab
    )
    retriever = MultiDocumentRetriever(
        embedding_model=embeddings,
        text=unstrcutured_document_extractor.NarrativeText,
        tab=unstrcutured_document_extractor.tab,
        base64_img=img_base64_list,
        tab_summaries=tab_summaries,
        image_summaries=image_summaries,
    ).create_retriever()

    rag_chain = MultiModalRAGChain(retriever, llm_with_fallbacks).create_chain()

    return retriever, rag_chain


def process_document_type():
    delete_folder(EXTRACTED_DATA_PATH)
    for file in os.listdir(INITIAL_DOCUMENT_PATH):
        ext = "." + file.split(".")[-1] if "." in file else ""
        filename = os.path.join(INITIAL_DOCUMENT_PATH, file)
        if ext not in EXTENSIONS:
            raise ValueError(f"Unsupported file format: {ext}")
        elif ext in IMAGE_EXTENSIONS:
            copy_image_to_folder(filename, EXTRACTED_DATA_PATH)
        elif ext == ".docx":
            convert_to_pdf(filename)


async def main():
    process_document_type()

    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        azure_task = loop.run_in_executor(executor, extract_with_azure)
        partition_task = loop.run_in_executor(executor, extract_with_partition)

        all_tools = await azure_task
        retriever, rag_chain = await partition_task

        model_with_tool = llm_with_fallbacks.bind_tools(all_tools)
        graph = GraphBuilder(
            model_with_tool, rag_chain, llm_with_fallbacks2, all_tools
        ).build()

        add_routes(
            app,
            graph,
            path="/agent",
        )

        @app.get("/query_image")
        async def query_image(query: str):
            docs = retriever.invoke(query)
            source_docs = split_image_text_types(docs)

            image_responses = []
            for base64_str in source_docs["images"]:
                try:
                    image_data = base64.b64decode(base64_str)
                    image = Image.open(io.BytesIO(image_data))

                    img_io = io.BytesIO()
                    image.save(img_io, format="PNG")
                    img_io.seek(0)

                    encoded_img = base64.b64encode(img_io.getvalue()).decode("utf-8")
                    image_responses.append(f"data:image/png;base64,{encoded_img}")

                except Exception as e:
                    return JSONResponse(content={"error": str(e)}, status_code=400)

            return {"images": image_responses}


if __name__ == "__main__":
    import uvicorn

    asyncio.run(main())

    uvicorn.run(app, host="localhost", port=8000)

"""

pip install -U 
langchain langgraph langchain_groq langchain_google_genai langchain_community langchain_core langgraph.prebuilt 
faiss-cpu "unstructured[all-docs]" transformers==4.37.2 pillow accelerate einops torchvision unstructured-pytesseract 
pytesseract nltk==3.9.1 fastapi uvicorn docx2pdf tiktoken azure-ai-documentintelligence azure-ai-formrecognizer PyPDF2   
langserve langchain_mongodb sse_starlette

need nltk, window word document for docx2pdf library, manually download pytesseract library and set as system variable
"""

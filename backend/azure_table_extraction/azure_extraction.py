import base64
import PyPDF2
import os
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

class AzureDocumentExtraction:

    def __init__(self, endpoint, key, input_path,supported_extension):
        self.__supported_extensions = supported_extension
        self.__document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            headers={"x-ms-useragent": "sample-code-merge-cross-tables/1.0.0"},
        )
        self.__input_path = input_path

    def extract_content_from_folder(self):
        print("---Extracting content from folder---")
        result_dict = {}
        for filename in os.listdir(self.__input_path):
            file_path = os.path.join(self.__input_path, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            print("Processing file:", filename)
            if (
                os.path.isfile(file_path)
                and file_extension in self.__supported_extensions
            ):
                result_dict[filename] = []
                total_pages = (
                    self.__get_pdf_page_count(file_path)
                    if file_extension == ".pdf"
                    else 1
                )
                page_result = self.__extract_content_per_doc(file_path, total_pages)
                result_dict[filename].append(page_result)
        return result_dict

    def __get_pdf_page_count(self, pdf_path):
        """Returns the total number of pages in a PDF file."""
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            print(f"Error: {e}")
            return 0

    def __file_to_base64(self,file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    def __extract_content_per_doc(self, file_path, total_pages):
        """Extracts tables from a document using Azure Document Intelligence."""
        page_result = None
        base64_data = self.__file_to_base64(file_path)

        for page_num in range(1, total_pages + 1):
            poller = self.__document_intelligence_client.begin_analyze_document(
                "prebuilt-layout",
                AnalyzeDocumentRequest(bytes_source=self.__file_to_base64(file_path)),
                output_content_format="markdown",
                pages=f"{page_num}",
            )

            result = poller.result()

            if page_result is None:
                page_result = result
                if total_pages > 1:
                    page_result.content += "<!-- PageBreak -->\n\n"
                    page_result.pages[0].spans[0].length = len(page_result.content)
                if "tables" not in page_result:
                    page_result.tables = []
            else:
                prev_offset = len(page_result.content)
                for table in result.tables or []:
                    table.spans[0].offset += prev_offset
                for paragraph in result.paragraphs or []:
                    paragraph.spans[0].offset += prev_offset

                page_result.pages.extend(result.pages)
                page_result.tables.extend(result.tables or [])
                page_result.paragraphs.extend(result.paragraphs or [])

                if page_num < total_pages:
                    result.content += "<!-- PageBreak -->\n\n"
                    result.pages[0].spans[0].length = len(result.content)

                page_result.content += result.content

        return page_result

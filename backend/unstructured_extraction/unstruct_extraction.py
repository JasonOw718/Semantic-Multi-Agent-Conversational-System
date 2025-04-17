import os
import shutil
from unstructured.partition.pdf import partition_pdf

class UnstructuredDocumentExtraction:
    def __init__(self,input_path,output_path):
        self.__Title = []
        self.__NarrativeText = []
        self.__Text = []
        self.__ListItem = []
        self.__img = []
        self.__tab = []
        self.__output_path = output_path
        self.__input_path = input_path

    def extract_content_from_folder(self):
        print("---Extracting content from folder---")

        pdf_files = [f for f in os.listdir(self.__input_path) if f.endswith("pdf")]
        index = 0
        for file in pdf_files:
            index += 1
            pdf_path = os.path.join(self.__input_path, file)

            raw_pdf_elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",
                extract_images_in_pdf=True,
                extract_image_block_types=["Image", "Table"],
                extract_image_block_to_payload=False,
                extract_image_block_output_dir=f"{self.__output_path}/pdf-{index}",
            )

            for element in raw_pdf_elements:
                if "unstructured.documents.elements.Title" in str(type(element)):
                    self.__Title.append(str(element))
                elif "unstructured.documents.elements.NarrativeText" in str(type(element)):
                    self.__NarrativeText.append(str(element))
                elif "unstructured.documents.elements.Text" in str(type(element)):
                    self.__Text.append(str(element))
                elif "unstructured.documents.elements.ListItem" in str(type(element)):
                    self.__ListItem.append(str(element))
                elif "unstructured.documents.elements.Image" in str(type(element)):
                    self.__img.append(str(element))
                elif "unstructured.documents.elements.Table" in str(type(element)):
                    self.__tab.append(str(element))
    
    
    @property
    def Title(self):
        return self.__Title

    @property
    def NarrativeText(self):
        return self.__NarrativeText

    @property
    def Text(self):
        return self.__Text

    @property
    def ListItem(self):
        return self.__ListItem

    @property
    def img(self):
        return self.__img

    @property
    def tab(self):
        return self.__tab

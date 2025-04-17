import base64
import os
import re
from langchain_core.documents import Document
from docx2pdf import convert
import shutil

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
EXTENSIONS = [".pdf", ".doc", ".docx"] + IMAGE_EXTENSIONS


def encode_image(image_path):
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def looks_like_base64(sb):
    """Check if the string looks like base64"""
    return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None


def is_image_data(b64data):
    """
    Check if the base64 data is an image by looking at the start of the data
    """
    image_signatures = {
        b"\xff\xd8\xff": "jpg",
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return True
        return False
    except Exception:
        return False


def split_image_text_types(docs):
    """
    Split base64-encoded images and texts
    """
    b64_images = []
    texts = []
    for doc in docs:
        # Check if the document is of type Document and extract page_content if so
        if isinstance(doc, Document):
            doc = doc.page_content
        if looks_like_base64(doc) and is_image_data(doc):
            b64_images.append(doc)
        else:
            texts.append(doc)
    return {"images": b64_images, "texts": texts}


def copy_image_to_folder(filename, dest_dir):
    dest_dir = os.path.join(dest_dir, "uploaded_images")
    os.makedirs(dest_dir, exist_ok=True)
    print(f"Created new '{dest_dir}' directory.")

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in IMAGE_EXTENSIONS:
        print(f"Unsupported file format: {ext}")
        return None

    if ext == ".jpeg":
        ext = ".jpg"

    try:
        destination = os.path.join(dest_dir, os.path.basename(filename))
        shutil.copy2(filename, destination)  # Copies instead of moving
        print(f"Copied '{filename}' to '{destination}'")
        return destination
    except Exception as e:
        print(f"Error copying file: {e}")
        return None


def convert_to_pdf(file_path):
    """Convert a DOCX file to PDF using python-docx and reportlab, then remove original DOCX"""

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        print(f"Converting {file_path} to PDF...")
        output_file = os.path.splitext(file_path)[0] + ".pdf"

        convert(file_path, output_file)

        if os.path.exists(output_file):
            print(f"Conversion successful: {output_file}")

            os.remove(file_path)
            print(f"Original file '{file_path}' has been removed.")
        else:
            print("Conversion failed: PDF file not created")
    except Exception as e:
        print(f"Conversion error: {e}")


def delete_folder(output_file):
    if os.path.exists(output_file):
        try:
            shutil.rmtree(output_file)  # Removes the folder and all its contents
            print(f"Folder '{output_file}' and its contents have been removed.")
        except Exception as e:
            print(f"Error removing folder: {e}")
    else:
        print(f"Folder '{output_file}' does not exist.")



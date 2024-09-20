import os
from pathlib import Path
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from sentence_transformers.quantization import quantize_embeddings
from typing import List
import requests
# from ocrmac import ocrmac
from PIL import Image
import PyPDF2
import easyocr

# Create an OCR reader object
reader = easyocr.Reader(['en'])


def image_to_ocr_tesseract():
    filename = "smartseekrepo.png"
    print("Processing => ", filename)
    temp_dir = Path("temp_ocr_folder")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / filename
    print(temp_file_path.resolve())
    # Open the image file using PIL
    image = Image.open(temp_file_path)
    # Use pytesseract to perform OCR on the image
    ocr_results = reader.readtext(str(temp_file_path))
    # Clean up the temporary file
    temp_file_path.unlink()
    ocr_text = ' '.join(result[1] for result in ocr_results)
    return {"raw_ocr": ocr_text}
    
image_to_ocr_tesseract()
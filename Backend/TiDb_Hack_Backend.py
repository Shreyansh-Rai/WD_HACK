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
from dotenv import load_dotenv

# Create an OCR reader object
reader = easyocr.Reader(['en'])
app = FastAPI()

# Load the model and specify preferred dimensions
dimensions = 2000
model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=dimensions)

class TextRequest(BaseModel):
    text: List[str]  # Accept a list of strings

@app.post("/embed/")
async def get_embedding(request: TextRequest):
    try:
        # Encode the input text
        embeddings = model.encode(request.text)
        
        # Optional: Quantize the embeddings
        binary_embeddings = quantize_embeddings(embeddings, precision="ubinary")
        
        return {"embeddings": binary_embeddings.tolist()}  # Convert numpy array to list for JSON serialization
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similarity/")
async def get_similarity(request: TextRequest):
    if len(request.text) < 2:
        raise HTTPException(status_code=400, detail="Please provide at least two sentences.")
    
    try:
        # Encode the input text
        embeddings = model.encode(request.text)
        
        # Compute cosine similarity
        similarities = cos_sim(embeddings[0], embeddings[1:])
        
        return {"similarities": similarities.tolist()}  # Convert to list for JSON serialization
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/image-to-caption/")
async def image_to_caption(file: UploadFile = File(...)):
    load_dotenv()
    hftoken = os.getenv("hftoken")
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f'Bearer {hftoken}'}

    try:
        # Read the image file
        image_bytes = await file.read()

        # Send the image to the Hugging Face API
        response = requests.post(API_URL, headers=headers, data=image_bytes)

        # Check for a successful response
        response.raise_for_status()
        
        # Return the API response
        return response.json()
    
    except requests.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# We can just use tesseract instead.
# @app.post("/image-to-OCR-macos/")
# async def image_to_ocr_macos(file: UploadFile = File(...)):

#     try:
#         print("Processing => ", file.filename)
#         temp_dir = Path("temp_ocr_folder")
#         temp_dir.mkdir(parents=True, exist_ok=True)
#         temp_file_path = temp_dir / file.filename

#         with temp_file_path.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         annotations = ocrmac.OCR(str(temp_file_path)).recognize()

#         temp_file_path.unlink()

#         ocr_data = []

#         for annotation in annotations :
#             ocr_data.append(annotation[0])

#         return {"annotations_with_position": annotations,
#                 "raw_ocr" : ocr_data}
    
#     except requests.HTTPError as e:
#         raise HTTPException(status_code=response.status_code, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/image-to-OCR-tesseract/")
async def image_to_ocr_tesseract(file: UploadFile = File(...)):

    try:
        print("Processing => ", file.filename)
        temp_dir = Path("temp_ocr_folder")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_dir / file.filename
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        temp_file_path = temp_file_path.resolve()
        # Use pytesseract to perform OCR on the image
        ocr_results = reader.readtext(str(temp_file_path))
        # Clean up the temporary file
        temp_file_path.unlink()
        ocr_text = ''.join(result[1] for result in ocr_results if result[1].strip())
        ret_text = ''
        for res in ocr_results :
            # print(res[1])
            ret_text += str(res[1]) + ' '
        print(ret_text)
        return {"raw_ocr": ret_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pdf-to-text/")
async def pdf_to_text(file: UploadFile = File(...)):
    try:
        print("Processing => ", file.filename)
        temp_dir = Path("temp_pdf_folder")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_dir / file.filename

        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Open the PDF file and extract text
        with open(temp_file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())

        # Clean up the temporary file
        temp_file_path.unlink()
        text = [line for line in "\n".join(text).split('\n') if line]
        return {"raw_text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

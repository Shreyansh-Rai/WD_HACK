import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

app = FastAPI()

API_BASE_URL = "http://localhost:8000"

class PathsRequest(BaseModel):
    paths: List[str]

async def process_file(client: httpx.AsyncClient, path: str) -> Dict[str, Any]:
    ext = os.path.splitext(path)[1].lower()
    result = {"path": path, "type": ext, "caption": "", "ocr_text": "", "embeddings": {}}
    
    try:
        if ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:  # Image files
            with open(path, "rb") as image_file:
                filename = os.path.basename(path)

                # Call image_to_caption API
                caption_response = await client.post(
                    f"{API_BASE_URL}/image-to-caption/",
                    files={"file": (filename, image_file, "image/jpeg")}
                )
                caption = caption_response.json()
                caption_text = caption[0].get('generated_text', "") if caption and isinstance(caption, list) else ""
                result["caption"] = caption_text

                # Reset file pointer
                image_file.seek(0)

                # Call image_to_ocr_tesseract API
                ocr_response = await client.post(
                    f"{API_BASE_URL}/image-to-OCR-tesseract/",
                    files={"file": (filename, image_file, "image/jpeg")}
                )
                ocr_text = ocr_response.json().get('raw_ocr', [])
                ocr_text_block = ocr_text
                result["ocr_text"] = ocr_text

                # Call embedding API for caption, OCR text, and combined text
                embeddings_caption = await client.post(
                    f"{API_BASE_URL}/embed/",
                    json={"text": [caption_text]}
                )

                embeddings_ocr = await client.post(
                    f"{API_BASE_URL}/embed/",
                    json={"text": [ocr_text_block]}
                )

                combined_text = caption_text + ocr_text_block
                embeddings_combined = await client.post(
                    f"{API_BASE_URL}/embed/",
                    json={"text": [combined_text]}
                )

                result["embeddings"] = {
                    "caption": embeddings_caption.json(),
                    "ocr": embeddings_ocr.json(),
                    "combined": embeddings_combined.json()
                }

        elif ext == ".pdf":  # PDF files
            with open(path, "rb") as pdf_file:
                filename = os.path.basename(path)

                # Call pdf_to_text API
                pdf_response = await client.post(
                    f"{API_BASE_URL}/pdf-to-text/",
                    files={"file": (filename, pdf_file, "application/pdf")}
                )
                pdf_text = pdf_response.json().get('raw_text', [])
                pdf_text_block = " ".join(pdf_text)
                result["ocr_text"] = pdf_text_block

                # Call embedding API for PDF text
                embeddings_pdf = await client.post(
                    f"{API_BASE_URL}/embed/",
                    json={"text": [pdf_text_block]}
                )

                result["embeddings"] = {
                    "pdf": embeddings_pdf.json()
                }

    except Exception as e:
        result["error"] = str(e)
    
    return result

async def traverse_directory(client: httpx.AsyncClient, path: str) -> Dict[str, Any]:
    result = {"directory": path, "files": []}
    
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_result = await process_file(client, file_path)
                result["files"].append(file_result)
    except Exception as e:
        result["error"] = str(e)
    
    return result

@app.post("/permit-list/")
async def permit_list(request: PathsRequest):
    results = []
    print("permit ",request)
    async with httpx.AsyncClient(timeout=100) as client:
        for path in request.paths:
            result = await traverse_directory(client, path)
            results.append(result)
    
    return {"results": results}

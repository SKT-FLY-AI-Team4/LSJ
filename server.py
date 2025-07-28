
import secrets
import os
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import shutil
import aiofiles
from google.cloud import storage

app = FastAPI(
    title="File Server API",
    description="An API to serve files with basic authentication.",
    version="1.0.0",
)

security = HTTPBasic()

class Message(BaseModel):
    text: str

# --- Configuration ---
# WARNING: In a real application, use a more secure way to handle credentials
# (e.g., environment variables, a secrets management system).
USERNAME = os.environ.get("SERVER_USERNAME", "admin")
PASSWORD = os.environ.get("SERVER_PASSWORD", "password")

# Directory where your files are served from
STATIC_DIR = "publicdata"

# GCS Bucket for file storage
GCS_BUCKET_NAME = "rational-autumn-467006-e2-lsj-files"

my_data = ["initial_item_1", "initial_item_2"]

# --- Helper Function ---
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- API Endpoints ---

@app.get("/files/{filename}", summary="Get a specific file")
async def get_file(filename: str, username: str = Depends(get_current_username)):
    """
    Retrieves a specific file from Google Cloud Storage after successful authentication.

    - **filename**: The name of the file to retrieve (e.g., `hot_dog.jpeg`).
    """
    client = storage.Client()
    bucket = client.get_bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)

    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found in GCS")

    # Download the file to a temporary location or directly stream it
    # For simplicity, we'll download to a temporary file and then return FileResponse
    # In a real application, consider streaming directly for large files
    temp_file_path = f"/tmp/{filename}"
    try:
        blob.download_to_filename(temp_file_path)
        return FileResponse(temp_file_path, media_type=blob.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve file from GCS: {e}")

@app.get("/files", summary="List all available files")
async def list_files(username: str = Depends(get_current_username)):
    """
    Lists all the files available in the Google Cloud Storage bucket.
    """
    client = storage.Client()
    bucket = client.get_bucket(GCS_BUCKET_NAME)
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs]
    return JSONResponse(content={"files": files}, media_type="application/json; charset=utf-8")

# Mount the static directory to serve files directly (optional, but useful)
# This part is not protected by the authentication middleware.
# To protect it, you would need to implement a custom middleware.
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return {"message": "lsj is running"}

@app.post("/send")
def send_message(message: Message):
    return {"lsj received_message": message.text}

@app.post("/uploadfile/", summary="Upload a file")
async def create_upload_file(
    file: UploadFile = File(...), username: str = Depends(get_current_username)
):
    """
    Uploads a file to Google Cloud Storage after successful authentication.

    - **file**: The file to upload.
    """
    client = storage.Client()
    bucket = client.get_bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(file.filename)

    try:
        # Upload the file directly to GCS
        await blob.upload_from_file(file.file, content_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file to GCS: {e}")
    finally:
        await file.close()
    return {"filename": file.filename, "message": "File uploaded successfully to GCS"}

@app.get("/info", summary="Get server information")
def get_info():
    """
    Returns a simple information message.
    """
    return {"info": "This is a functional endpoint on the LSJ server."}

@app.get("/data", summary="Get current data")
def get_data():
    """
    Returns the current in-memory data list.
    """
    return {"data": my_data}

@app.post("/data/add", summary="Add data to the list")
def add_data(item: str, username: str = Depends(get_current_username)):
    """
    Adds a new item to the in-memory data list. Requires authentication.

    - **item**: The string item to add.
    """
    my_data.append(item)
    return {"message": f"'{item}' added to data", "current_data": my_data}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server. Access the API docs at http://127.0.0.1:8000/docs")
    print(f"Username: {USERNAME}")
    print(f"Password: {PASSWORD}")
    uvicorn.run(app, host="0.0.0.0", port=8080)

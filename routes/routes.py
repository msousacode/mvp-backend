from fastapi import APIRouter

from schemas import schemas
from services import bucket, dynamodb

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Server is running"}


@router.post("/upload")
async def upload(uploaded_file: schemas.UploadRequest):
    response = bucket.upload_file(uploaded_file)
    return {"status": 200, "message": response}


@router.post("/salvar")
async def salvar(rag_request: schemas.RAGRequest):
    dynamodb.salvar_rag(rag_request)
    return {"status": 200}

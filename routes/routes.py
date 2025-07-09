from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services import bucket

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Server is running"}


@router.post("/upload")
async def upload(file: UploadFile = File(...), titulo: str = Form(...)):

    # Verificar se o arquivo existe
    if not file or not file.filename:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "Nenhum arquivo foi enviado"}
        )

    # Verificar se o arquivo é PDF
    if not file.filename.endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={"status": 400,
                     "message": "Apenas arquivos PDF são permitidos"}
        )

    # Ler o conteúdo do arquivo
    file_content = await file.read()
    file_size = len(file_content)

    print(f"Tamanho do arquivo: {file_size} bytes")

    # Fazer upload
    response = "xxx"  # bucket.upload_file(file_content)

    if not response:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": "Erro ao fazer upload do arquivo"}
        )

    return {
        "status": 200,
        "message": f"Arquivo {file.filename} enviado com sucesso",
        "file_id": str(response),
        "file_size": file_size,
        "titulo": titulo
    }

# @router.post("/salvar")
# async def salvar(rag_request: schemas.RAGRequest):
#    dynamodb.salvar_rag(rag_request)
#    return {"status": 200}

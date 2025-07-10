from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services.processa_arquivos import processa_arquivos

router = APIRouter()


@router.get("/ok")
async def root():
    return {"status": 200, "message": "Server is running"}


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
    result = processa_arquivos(file_content, file.filename, titulo)

    if result["success"]:
        return {
            "status": 200,
            "message": f"Arquivo {file.filename} processado com sucesso",
            "result": result
        }
    else:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": "Erro ao processar o arquivo",
                "error": result.get("error", "Erro desconhecido")
            }
        )

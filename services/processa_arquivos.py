from schemas import schemas


def processa_arquivos(upload_request: schemas.UploadRequest):

    print(f"Arquivo upload: {upload_request}")

from schemas import schemas
from uuid import UUID
from services import processa_arquivos


def upload_file(uploaded_file: schemas.UploadRequest):
    processa_arquivos(uploaded_file)
    return UUID.uuid4()


def download_file(file_id: str):
    """
        Função de teste para verificar o download de arquivos.
        """
    # Aqui você pode adicionar lógica para processar o download do arquivo
    # Retorna um UUID como string para simular o ID do arquivo baixado
    return UUID.uuid4()

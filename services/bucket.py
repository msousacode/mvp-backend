from schemas import schemas
from uuid import UUID


def upload_file(uploaded_file: schemas.UploadRequest):
    """
        Função de teste para verificar o upload de arquivos.
        """
    # Aqui você pode adicionar lógica para processar o arquivo enviado
    # Retorna um UUID como string para simular o ID do arquivo enviado
    return UUID.uuid4()

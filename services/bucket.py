from uuid import uuid4
from .processa_arquivos import processa_arquivos


def upload_file(file_content: bytes, filename: str, titulo: str = None):
    """
    Processa o upload de um arquivo PDF

    Args:
        file_content (bytes): Conteúdo do arquivo PDF
        filename (str): Nome do arquivo
        titulo (str): Título opcional do documento

    Returns:
        dict: Resultado do processamento
    """
    try:
        # Processar o arquivo PDF
        result = processa_arquivos(file_content, filename, titulo)

        if result["success"]:
            # Gerar ID único para o arquivo
            file_id = str(uuid4())
            result["file_id"] = file_id

            print(f"Upload processado com sucesso. ID: {file_id}")
            return result
        else:
            print(
                f"Erro no processamento do arquivo: {result.get('error', 'Erro desconhecido')}")
            return result

    except Exception as e:
        print(f"Erro no upload do arquivo: {e}")
        return {
            "success": False,
            "error": f"Erro no upload: {str(e)}",
            "filename": filename,
            "titulo": titulo
        }


def download_file(file_id: str):
    """
    Função de teste para verificar o download de arquivos.
    """
    # Aqui você pode adicionar lógica para processar o download do arquivo
    # Retorna um UUID como string para simular o ID do arquivo baixado
    return str(uuid4())

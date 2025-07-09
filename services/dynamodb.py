from schemas import schemas
from models import RAGRequestModel


def salvar_rag(rag_request: schemas.RAGRequest):

    try:
        rag = RAGRequestModel(
            arquivo_id=rag_request.id_arquivo,
            rags=rag_request.rags
        )
        rag.save()  # Salva o objeto no DynamoDB
        print(f"rag salvo com sucesso para o arquivo {rag_request.id_arquivo}")
    except Exception as e:
        print(f"Erro ao criar/atualizar usuário: {e}")
        return None

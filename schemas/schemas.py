from uuid import UUID


class UploadRequest:
    titulo: str
    file: bytes


# Este arquivo define os esquemas para o sistema RAG (Geração Aumentada por Recuperação).
class RAG:
    codigo: int
    titulo: str


class RAGRequest:
    id_arquivo: UUID
    rags: list[RAG]

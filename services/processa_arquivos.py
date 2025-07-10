import os
import fitz  # PyMuPDF
import tempfile
from uuid import uuid4

# Diretório de saída para arquivos processados
path_output = "data"


def processa_arquivos(file_content: bytes, filename: str, titulo: str = None):

    # Criar pasta de saída se não existir
    output_folder = os.path.join(path_output, "bucket-processados")
    os.makedirs(output_folder, exist_ok=True)

    # Definir número máximo de páginas a serem processadas
    MAX_PAGES = 5

    # Lista para armazenar os caminhos dos arquivos PNG gerados
    arquivos_png_gerados = []

    # ID único para este processamento
    process_id = str(uuid4())

    print(f"Iniciando processamento do PDF: {filename}")
    print(f"Título: {titulo}")
    print(f"ID do processo: {process_id}")

    try:
        # Criar arquivo temporário com o conteúdo do PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_pdf_path = temp_file.name

        # Abrir o PDF usando PyMuPDF
        doc = fitz.open(temp_pdf_path)
        print(f"PDF carregado: {doc.page_count} páginas encontradas")

        # Verificar se excede o limite de páginas
        if doc.page_count > MAX_PAGES:
            print(
                f"Aviso: PDF tem {doc.page_count} páginas. Processando apenas as primeiras {MAX_PAGES}")

        # Processar cada página até o limite
        pages_processed = min(doc.page_count, MAX_PAGES)

        for page_num in range(pages_processed):
            page = doc.load_page(page_num)

            # Matriz de zoom para alta resolução (2x)
            matriz = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=matriz)

            # Gerar nome do arquivo de saída
            base_name = os.path.splitext(filename)[0]
            output_image_name = f"{base_name}_{process_id}_pagina_{page_num}.png"
            full_output_path = os.path.join(output_folder, output_image_name)

            # Salvar a imagem
            pix.save(full_output_path)
            arquivos_png_gerados.append(full_output_path)

            print(f"Página {page_num + 1} processada: {output_image_name}")

        # Fechar o documento
        doc.close()

        # Remover arquivo temporário
        os.unlink(temp_pdf_path)

        print(
            f"Processamento concluído: {len(arquivos_png_gerados)} imagens geradas")

        compactar_imagens_geradas(arquivos_png_gerados, output_folder)

        return {
            "success": True,
            "process_id": process_id,
            "filename": filename,
            "titulo": titulo,
            "pages_processed": pages_processed,
            "total_pages": doc.page_count
        }

    except Exception as e:
        print(f"Erro ao processar o PDF '{filename}': {e}")

        # Cleanup em caso de erro
        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)

        return {
            "success": False,
            "error": str(e),
            "filename": filename,
            "titulo": titulo
        }


def compactar_imagens_geradas(arquivos_png_gerados, output_folder):
    """
    Função auxiliar para compactar as imagens geradas (opcional)
    """
    if not arquivos_png_gerados:
        return None

    try:
        import zipfile

        # Nome do arquivo ZIP
        zip_filename = f"imagens_processadas_{uuid4()}.zip"
        zip_path = os.path.join(output_folder, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for png_path in arquivos_png_gerados:
                if os.path.exists(png_path):
                    # Adicionar apenas o nome do arquivo, não o caminho completo
                    zipf.write(png_path, os.path.basename(png_path))

        print(f"Arquivo ZIP criado: {zip_filename}")

        # Opcional: remover arquivos PNG originais
        for png_path in arquivos_png_gerados:
            if os.path.exists(png_path):
                os.remove(png_path)

        return zip_path

    except Exception as e:
        print(f"Erro ao criar arquivo ZIP: {e}")
        return None

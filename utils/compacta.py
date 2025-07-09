import os
import zipfile
import uuid  # Módulo para gerar UUIDs


def compactar_e_renomear_com_uuid(caminho_dos_arquivos, nome_do_zip_temporario="imagens_processadas.zip"):
    """
    Compacta os arquivos especificados em um arquivo .zip e o renomeia com um UUID.

    Args:
        caminho_dos_arquivos (list): Uma lista de caminhos completos para os arquivos a serem compactados.
        nome_do_zip_temporario (str): O nome temporário do arquivo .zip antes de ser renomeado com o UUID.
                                      Por padrão, "imagens_processadas.zip".

    Returns:
        str: O nome do arquivo .zip final com o UUID, ou None se ocorrer um erro.
    """
    if not caminho_dos_arquivos:
        print("Nenhum arquivo especificado para compactar.")
        return None

    try:
        # Cria o arquivo .zip em modo de escrita ('w') com compressão DEFLATED
        with zipfile.ZipFile(os.path.join(os.path.dirname(caminho_dos_arquivos[0]), nome_do_zip_temporario), 'w', zipfile.ZIP_DEFLATED) as zipf:
            for arquivo in caminho_dos_arquivos:
                if os.path.exists(arquivo):
                    # Adiciona o arquivo ao zip, usando apenas o nome base para manter a estrutura limpa
                    zipf.write(arquivo, os.path.basename(arquivo))
                    print(
                        f"  Adicionado '{os.path.basename(arquivo)}' ao zip.")
                else:
                    print(
                        f"Aviso: Arquivo '{arquivo}' não encontrado e será ignorado para compactação.")
        print(
            f"\nArquivos compactados temporariamente em '{nome_do_zip_temporario}'.")

        # Gera um UUID e renomeia o arquivo .zip
        novo_nome_uuid = str(uuid.uuid4()) + ".zip"
        # O novo zip será criado na mesma pasta onde os arquivos .png foram gerados
        caminho_final_zip = os.path.join(os.path.dirname(
            caminho_dos_arquivos[0]), novo_nome_uuid)
        os.rename(os.path.join(os.path.dirname(
            caminho_dos_arquivos[0]), nome_do_zip_temporario), caminho_final_zip)
        print(
            f"Arquivo '{nome_do_zip_temporario}' renomeado para '{novo_nome_uuid}'.")
        return caminho_final_zip

    except FileNotFoundError as fnfe:
        print(f"Erro de arquivo não encontrado durante a compactação: {fnfe}")
        # Tenta limpar o arquivo temporário se ele foi criado e houve erro
        temp_zip_path = os.path.join(os.path.dirname(
            caminho_dos_arquivos[0]), nome_do_zip_temporario)
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        return None
    except Exception as e:
        print(f"Ocorreu um erro geral durante a compactação: {e}")
        # Tenta limpar o arquivo temporário se ele foi criado e houve erro
        temp_zip_path = os.path.join(os.path.dirname(
            caminho_dos_arquivos[0]), nome_do_zip_temporario)
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        return None

import boto3
import json
import os
from botocore.exceptions import ClientError
from typing import List, Dict, Any


def processar_arquivos_png(arquivos_png: List[str], aws_config: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Processa uma lista de arquivos PNG usando AWS Textract

    Args:
        arquivos_png: Lista de caminhos para arquivos PNG
        aws_config: Configurações AWS (bucket, região, etc.)

    Returns:
        Dict com resultados do processamento
    """

    if not arquivos_png:
        return {"success": False, "error": "Nenhum arquivo PNG fornecido"}

    # Configurações padrão (ajuste conforme necessário)
    if aws_config is None:
        aws_config = {
            "region": "us-east-1",
            "bucket_name": "seu-bucket-s3",  # Configure seu bucket
            "output_bucket": "seu-bucket-output"  # Configure seu bucket de saída
        }

        # Inicializar clientes AWS
        textract = boto3.client(
            "textract", region_name=aws_config.get("region", "us-east-1"))
        s3 = boto3.client(
            "s3", region_name=aws_config.get("region", "us-east-1"))

        resultados = []

        for i, arquivo_png in enumerate(arquivos_png):
            print(
                f"Processando arquivo {i+1}/{len(arquivos_png)}: {arquivo_png}")

            try:
                # Ler o arquivo PNG
                with open(arquivo_png, 'rb') as file:
                    arquivo_bytes = file.read()

                # Processar com Textract (usando bytes diretamente, sem S3)
                response = textract.analyze_document(
                    Document={
                        'Bytes': arquivo_bytes
                    },
                    FeatureTypes=["FORMS", "TABLES", "LAYOUT"]
                )

                print(
                    f"Detectados {len(response['Blocks'])} blocos no arquivo {os.path.basename(arquivo_png)}")

                if response:  # Verifica se response foi populado com sucesso

                    # -- Manter comentado só para ter como visão de que existem esses códigos disponíveis para serem usados.
                    # === BUSCA POR PALAVRAS-CHAVE ESPECÍFICAS ===
                    # print("\n=== BUSCANDO PALAVRAS-CHAVE ===")

                    # Busca por uma palavra específica
                    # cpf_blocks = find_keyword_blocks(response, "379.295.458-30")
                    # print(f"Encontrados {len(cpf_blocks)} blocos com '379.295.458/30':")
                    # for block in cpf_blocks:
                    #    coords = get_block_coordinates(block)
                    #    print(f"  - ID: {block['id']}")
                    #    print(f"  - Texto: '{block['text']}'")
                    #    print(f"  - Confiança: {block['confidence']:.2f}%")
                    #    print(f"  - Página: {block['page']}")
                    #    if coords:
                    #        print(
                    #            f"  - Posição: Left={coords['left']:.3f}, Top={coords['top']:.3f}")
                    #    print()

                    # Busca por múltiplas palavras-chave
                    # keywords_to_find = ["CPF/CNPJ:", "Nome",
                    #                    "Endereço", "Telefone", "Email"]
                    # multiple_results = find_multiple_keywords(response, keywords_to_find)

                    # print("=== RESULTADOS DE MÚLTIPLAS KEYWORDS ===")
                    # for keyword, blocks in multiple_results.items():
                    #    print(f"{keyword}: {len(blocks)} ocorrências encontradas")

                    # Pega todas as palavras e suas IDs.
                    word_map = map_word_id(response)

                    # === EXTRAÇÃO DE DADOS DA TABELA DE SEGUROS ===
                    print("\n=== EXTRAINDO DADOS DA TABELA DE SEGUROS ===")

                    # Extrai dados no formato solicitado
                    insurance_data = extract_insurance_table_data(response)

                    print(
                        f"Encontrados {len(insurance_data)} itens da tabela de seguros")

                    # Exibe o resultado no formato JSON solicitado
                    print("\n=== RESULTADO NO FORMATO SOLICITADO ===")
                    print(json.dumps(insurance_data, indent=2, ensure_ascii=False))

                    # === PROCESSAMENTO ORIGINAL (para comparação) ===
                    print("\n=== PROCESSAMENTO ORIGINAL (para comparação) ===")

                    # Passa as palavras chaves e os valores chaves para formar um objeto chave-valor.
                    final_map = get_kv_map(response, word_map)

                    # Print do JSON formatado de forma legível
                    print("JSON dos pares chave-valor (método tradicional):")
                    print(json.dumps(final_map, indent=2, ensure_ascii=False))

                    return {
                        "success": True,
                        "total_arquivos": len(arquivos_png),
                        "arquivos_processados": len([r for r in resultados if r.get("success", False)]),
                        "resultados": resultados
                    }

            except Exception as e:
                print(f"Erro geral no processamento: {e}")
                return {
                    "success": False,
                    "error": f"Erro no processamento: {str(e)}"
                }

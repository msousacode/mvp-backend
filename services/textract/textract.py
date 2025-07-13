import boto3
import json
import os
from typing import List, Dict, Any
from .parser import (
    map_word_id,
    get_kv_map,
    extract_insurance_table_data,  # Nova função para tabela de seguros
    # find_keyword_blocks,  # Nova função para buscar keywords
    # find_multiple_keywords,  # Nova função para buscar múltiplas keywords
    # get_block_coordinates  # Nova função para coordenadas
)
from utils.montar_json import montar_json


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

                    # Pega todas as palavras e suas IDs.
                    word_map = map_word_id(response)

                    # === EXTRAÇÃO DE DADOS DA TABELA DE SEGUROS ===
                    # print("\n=== EXTRAINDO DADOS DA TABELA DE SEGUROS ===")

                    # Extrai dados no formato solicitado
                    insurance_data = extract_insurance_table_data(response)

                    # print(f"Encontrados {len(insurance_data)} itens da tabela de seguros")

                    # Exibe o resultado no formato JSON solicitado
                    print("\n=== RESULTADO NO FORMATO SOLICITADO ===")
                    print(json.dumps(insurance_data, indent=2, ensure_ascii=False))

                    # === PROCESSAMENTO ORIGINAL (para comparação) ===
                    # print("\n=== PROCESSAMENTO ORIGINAL (para comparação) ===")

                    # Passa as palavras chaves e os valores chaves para formar um objeto chave-valor.
                    final_map = get_kv_map(response, word_map)
                    # print("\n=== FINAL MAP ===")
                    # print(json.dumps(final_map, indent=2, ensure_ascii=False))

                    # TODO Essas chaves devem ser dinâmicas, baseadas no conteúdo do PDF
                    keys = [
                        'N° Cotação',
                        'Vigência',
                        'N° Proposta/Negócio',
                        'Tipo Seguro',
                        'Empresa Parceira',
                        'Processo SUSEP n°',
                        'Deseja contratar cobertura do seguro para condutores na faixa etária de 18 a 25 anos que residem com O Principal Condutor?'
                    ]

                    # Print do JSON formatado de forma legível
                    print("\n\n=== JSON dos pares chave-valor (método tradicional):")
                    json_resultado = montar_json(keys, final_map)

                    # Converter string JSON de volta para objeto Python
                    resultado_objeto = json.loads(json_resultado)
                    resultados.append(resultado_objeto)

            except Exception as e:
                print(f"Erro ao processar {arquivo_png}: {e}")

        # Exibir resultados consolidados
        print("\n=== RESULTADOS CONSOLIDADOS ===")
        if resultados:
            # Se há apenas um resultado, mostrar diretamente
            if len(resultados) == 1:
                print(json.dumps(resultados[0], indent=2, ensure_ascii=False))
            else:
                # Se há múltiplos resultados, mostrar como array
                print(json.dumps(resultados, indent=2, ensure_ascii=False))

        # Retornar resultado consolidado
        return {
            "success": True,
            "total_arquivos": len(arquivos_png),
            "resultados": resultados
        }

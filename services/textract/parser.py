# parser.py

def extract_text(response, extract_by="LINE"):
    """
    Extrai texto da resposta do Textract.
    'extract_by' pode ser 'LINE' ou 'WORD'.
    """
    # Lógica para extrair texto
    # Exemplo simples (você precisará adaptar para sua necessidade):
    text = []
    for block in response['Blocks']:
        if block['BlockType'] == extract_by.upper():
            text.append(block['Text'])
    return "\n".join(text)


def map_word_id(response):
    """
    Cria um mapa de IDs de palavras para o conteúdo da palavra.
    """
    word_map = {}
    for block in response['Blocks']:
        if block['BlockType'] == 'WORD':
            word_map[block['Id']] = block['Text']
    return word_map


def get_key_map(response, word_map):
    """
    Cria um mapa de chaves (Key) encontradas em formulários.
    """
    key_map = {}
    for block in response['Blocks']:
        if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block['EntityTypes']:
            key_text = []
            for relationship in block.get('Relationships', []):
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        if child_id in word_map:
                            key_text.append(word_map[child_id])
            key_map[block['Id']] = " ".join(key_text)
    return key_map


def get_kv_map(response, word_map):
    """
    Cria um mapa de pares chave-valor a partir da resposta do Textract.
    """
    kv_map = {}

    # Percorre todos os blocos na resposta do Textract
    for block in response['Blocks']:
        # Identifica blocos que são KEY_VALUE_SET e são do tipo KEY
        if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block['EntityTypes']:
            # key_id = block['Id']
            key_text = ""

            # Encontra o texto da chave
            if 'Relationships' in block:
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        child_words = [word_map[id]
                                       for id in relationship['Ids'] if id in word_map]
                        key_text = " ".join(child_words)

            # Encontra o valor associado a esta chave
            value_text = ""
            if 'Relationships' in block:
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'VALUE' and len(relationship['Ids']) > 0:
                        value_block_id = relationship['Ids'][0]

                        # Encontra o bloco de valor correspondente
                        value_block = next(
                            (b for b in response['Blocks'] if b['Id'] == value_block_id), None)

                        if value_block and 'Relationships' in value_block:
                            for value_rel in value_block['Relationships']:
                                if value_rel['Type'] == 'CHILD':
                                    child_words = [
                                        word_map[id] for id in value_rel['Ids'] if id in word_map]
                                    value_text = " ".join(child_words)
                                    break  # Encontramos o valor, podemos sair

            if key_text:  # Apenas adiciona se a chave foi encontrada
                # Remove ':' da chave para um formato limpo
                kv_map[key_text.strip().replace(':', '')] = value_text.strip()

    return kv_map


def find_keyword_blocks(response, keyword):
    """
    Busca blocos que contêm uma palavra-chave específica.
    Retorna uma lista com informações dos blocos encontrados.
    """
    matching_blocks = []

    for block in response['Blocks']:
        if block['BlockType'] == 'WORD':
            # Busca exata (case-insensitive)
            if block['Text'].lower() == keyword.lower():
                matching_blocks.append({
                    'id': block['Id'],
                    'text': block['Text'],
                    'confidence': block['Confidence'],
                    'page': block['Page'],
                    'geometry': block['Geometry']
                })
            # Busca parcial (se a palavra contém a keyword)
            elif keyword.lower() in block['Text'].lower():
                matching_blocks.append({
                    'id': block['Id'],
                    'text': block['Text'],
                    'confidence': block['Confidence'],
                    'page': block['Page'],
                    'geometry': block['Geometry'],
                    'match_type': 'partial'
                })

    return matching_blocks


def find_multiple_keywords(response, keywords_list):
    """
    Busca múltiplas palavras-chave de uma só vez.
    Retorna um dicionário com os resultados para cada keyword.
    """
    results = {}

    for keyword in keywords_list:
        results[keyword] = find_keyword_blocks(response, keyword)

    return results


def get_block_coordinates(block):
    """
    Extrai as coordenadas de posição de um bloco.
    Útil para saber onde a palavra está localizada no documento.
    """
    if 'Geometry' in block and 'BoundingBox' in block['Geometry']:
        bbox = block['Geometry']['BoundingBox']
        return {
            'left': bbox['Left'],
            'top': bbox['Top'],
            'width': bbox['Width'],
            'height': bbox['Height']
        }
    return None


def extract_insurance_table_data(response):
    """
    Extrai dados específicos da tabela de seguros no formato solicitado.
    Retorna um array de objetos com Descrição, Limite Máximo Indenização e Prêmio Líquido.
    """

    # Mapeia todas as palavras e linhas
    word_map = {}
    line_map = {}

    for block in response['Blocks']:
        if block['BlockType'] == 'WORD':
            word_map[block['Id']] = block['Text']
        elif block['BlockType'] == 'LINE':
            line_map[block['Id']] = block['Text']

    insurance_data = []

    # Lista dos itens esperados baseado na imagem
    expected_items = [
        "Colisão, Incêndio e Roubo/Furto",
        "Despesa extraordinária",
        "RCF-V - Danos Materiais",
        "RCF-V - Danos Corporais",
        "RCF-V - Danos Morais",
        "APP - Morte (por passageiro)",
        "APP - Invalidez permanente (por passageiro)",
        "APP - DMHO (por passageiro)",
        "Assistência 24 horas",
        "Km adicional de reboque",
        "Kit Gás",
        "Blindagem",
        "Extensão para Garantia de 0km"
    ]

    # Procura por tabelas primeiro
    for block in response['Blocks']:
        if block['BlockType'] == 'TABLE':
            print(f"Processando tabela: {block['Id']}")

            # Coleta todas as células
            cells = []
            if 'Relationships' in block:
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        for cell_id in relationship['Ids']:
                            cell_block = next(
                                (b for b in response['Blocks'] if b['Id'] == cell_id), None)
                            if cell_block and cell_block['BlockType'] == 'CELL':

                                # Extrai texto da célula
                                cell_text = ""
                                if 'Relationships' in cell_block:
                                    for cell_rel in cell_block['Relationships']:
                                        if cell_rel['Type'] == 'CHILD':
                                            child_texts = []
                                            for child_id in cell_rel['Ids']:
                                                if child_id in word_map:
                                                    child_texts.append(
                                                        word_map[child_id])
                                                elif child_id in line_map:
                                                    child_texts.append(
                                                        line_map[child_id])
                                            cell_text = " ".join(
                                                child_texts).strip()

                                cells.append({
                                    'text': cell_text,
                                    'row': cell_block.get('RowIndex', 0),
                                    'col': cell_block.get('ColumnIndex', 0),
                                    'confidence': cell_block.get('Confidence', 0)
                                })

            # Organiza células por linha
            cells_by_row = {}
            for cell in cells:
                row = cell['row']
                if row not in cells_by_row:
                    cells_by_row[row] = {}
                cells_by_row[row][cell['col']] = cell['text']

            # Converte para o formato solicitado
            for row_num in sorted(cells_by_row.keys()):
                if row_num == 1:  # Pula linha de cabeçalho
                    continue

                row_data = cells_by_row[row_num]

                # Verifica se tem as 3 colunas esperadas
                if 1 in row_data and 2 in row_data and 3 in row_data:
                    descricao = row_data[1].strip()
                    limite = row_data[2].strip()
                    premio = row_data[3].strip()

                    # Pula se for linha de cabeçalho ou vazia
                    if (descricao and limite and premio and
                            descricao.lower() not in ['descrição', 'descricao']):

                        insurance_data.append({
                            "Descrição": descricao,
                            "Limite Máximo Indenização": limite,
                            "Prêmio Líquido": premio
                        })

    # Se não encontrou dados na tabela, tenta método alternativo baseado em linhas
    if not insurance_data:
        insurance_data = extract_insurance_data_from_lines(
            response, expected_items)

    return insurance_data


def extract_insurance_data_from_lines(response, expected_items):
    """
    Método alternativo para extrair dados baseado em linhas quando a tabela não é detectada.
    """
    line_blocks = []

    # Coleta todos os blocos LINE
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            geometry = block.get('Geometry', {}).get('BoundingBox', {})
            line_blocks.append({
                'id': block['Id'],
                'text': block['Text'],
                'page': block['Page'],
                'left': geometry.get('Left', 0),
                'top': geometry.get('Top', 0),
                'width': geometry.get('Width', 0),
                'confidence': block['Confidence']
            })

    # Ordena por página e posição
    line_blocks.sort(key=lambda x: (x['page'], x['top'], x['left']))

    insurance_data = []

    for item in expected_items:
        # Procura linha que contém a descrição
        desc_line = None
        for line in line_blocks:
            if item.lower() in line['text'].lower():
                desc_line = line
                break

        if desc_line:
            # Procura linhas na mesma altura para limite e prêmio
            limite_text = "Não contratada"  # Valor padrão
            premio_text = "R$ 0,00"  # Valor padrão

            same_height_lines = []
            for line in line_blocks:
                if (line['page'] == desc_line['page'] and
                    # Mesma altura
                    abs(line['top'] - desc_line['top']) < 0.01 and
                        line['left'] > desc_line['left']):  # À direita
                    same_height_lines.append(line)

            # Ordena por posição da esquerda para direita
            same_height_lines.sort(key=lambda x: x['left'])

            # Atribui valores encontrados
            if len(same_height_lines) >= 1:
                limite_text = same_height_lines[0]['text']
            if len(same_height_lines) >= 2:
                premio_text = same_height_lines[1]['text']

            insurance_data.append({
                "Descrição": item,
                "Limite Máximo Indenização": limite_text,
                "Prêmio Líquido": premio_text
            })

    return insurance_data

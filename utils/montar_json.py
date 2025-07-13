import json


def montar_json(keys: list, final_map: dict) -> str:

    # Criar um novo dicionário apenas com as chaves especificadas
    filtered_map = {}

    for k in keys:
        if k in final_map:
            filtered_map[k] = final_map[k]
        else:
            continue

    json_output = json.dumps(filtered_map, indent=2, ensure_ascii=False)

    return json_output

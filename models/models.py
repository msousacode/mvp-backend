from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, MapAttribute, ListAttribute
import os

# Defina as configurações para o DynamoDB local, se estiver usando
# Se estiver usando o DynamoDB na AWS, você pode remover essas linhas
# ou configurá-las para a sua região e credenciais.
# As credenciais da AWS serão pegas das suas variáveis de ambiente ou do ~/.aws/credentials
# A região será pega das suas variáveis de ambiente, ~/.aws/config ou default_region
if os.environ.get('DYNAMODB_LOCAL', 'false').lower() == 'true':
    # Credenciais fictícias para o DynamoDB local
    os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
    # Região pode ser qualquer uma para o local
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


class RAGRequestModel(Model):
    """
    Modelo de solicitação para o endpoint de RAG.
    """
    class Meta:
        # Nome da sua tabela no DynamoDB
        table_name = 'UsersTable'
        # Região da AWS onde a tabela está localizada
        # Se você não definir isso, PynamoDB tentará usar a variável de ambiente AWS_DEFAULT_REGION
        # ou a configuração do seu AWS CLI.
        region = 'us-east-1'

        # Endpoint URL para DynamoDB local (opcional)
        # Remova ou comente esta linha se estiver usando DynamoDB na AWS.
        host = 'http://localhost:8000'

        # Leia e escreva capacidades de provisionamento (opcional)
        # Útil para tabelas provisionadas, não para on-demand
        read_capacity_units = 1
        write_capacity_units = 1

    # Atributos da sua tabela DynamoDB
    arquivo_id = UnicodeAttribute(hash_key=True)
    rags = ListAttribute()

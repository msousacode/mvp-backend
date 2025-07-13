Start servidor:
uvicorn main:app --reload


Comando para rodar o servidor em uma porta específica
uvicorn main:app --port 8080 --reload


Comando para executar dentro a ec2 para aceitar requisições
uvicorn main:app --host 0.0.0.0 --port 8000


Requerimentos\Dependências do projeto
fastapi==0.116.0
uvicorn[standard]
python-multipart
PyMuPDF==1.26.3
boto3
pynamodb
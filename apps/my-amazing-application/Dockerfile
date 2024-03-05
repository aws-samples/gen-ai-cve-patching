# Usa a imagem base Python com Alpine para leveza
FROM python:3.8

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt /app/

# Instala as dependências do arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia os demais arquivos do seu projeto Python para o diretório de trabalho
COPY . /app/

# Comando padrão para executar a aplicação, ajuste conforme necessário
CMD ["python", "app.py"]

# Vturb Analytics API

## Visão Geral

A Vturb Analytics API permite acessar arquivos CSV de análise para diferentes vídeos processados pela plataforma VTurb. Esta API fornece endpoints simples para listar todos os vídeos disponíveis e baixar arquivos CSV específicos para cada vídeo.

## Base URL

Por padrão, a API é servida localmente em:

```
http://localhost:8000
```

## Autenticação

Atualmente, a API não requer autenticação.

## Endpoints

### Obter Documentação

```http
GET /
```

Acessa a documentação da API em formato HTML.

**Respostas:**
- **200 OK**: Retorna a página de documentação HTML

---

### Listar Vídeos Disponíveis

```http
GET /list
```

Este endpoint lista todos os vídeos disponíveis para análise no sistema.

**Parâmetros:** Nenhum

**Respostas:**
- **200 OK**: Retorna a lista de pastas de vídeos disponíveis
- **500 Internal Server Error**: Se ocorrer um erro ao listar as pastas

**Exemplo de Resposta:**
```json
{
  "folders": [
    "2.1 [VSL IA] - Assistente x Agentes - Com delay",
    "2.2 [VSL IA] - Assistente x Agentes - Sem delay",
    "2.3 [VSL IA] - Assistente x Agentes - Trilha.mp4"
  ],
  "count": 3
}
```

---

### Obter CSV de um Vídeo

```http
GET /analytics/{video_name}
```

Este endpoint retorna o primeiro arquivo CSV encontrado na pasta do vídeo especificado.

**Parâmetros:**
- `video_name`: Nome da pasta do vídeo contendo o arquivo CSV (obrigatório)
  - Deve ser o nome exato da pasta, incluindo espaços e caracteres especiais
  - A biblioteca requests cuida automaticamente da codificação dos caracteres especiais e espaços

**Respostas:**
- **200 OK**: Retorna o arquivo CSV para download
- **404 Not Found**: Se a pasta do vídeo não for encontrada ou se não houver arquivos CSV na pasta

**Exemplo de Requisição:**

```python
import requests

# A biblioteca requests codifica automaticamente os caracteres especiais na URL
video_name = "2.1 [VSL IA] - Assistente x Agentes - Com delay"
response = requests.get(f"http://localhost:8000/analytics/{video_name}")

# Verifica se a resposta foi bem-sucedida
if response.status_code == 200:
    # Salva o arquivo CSV localmente
    with open("metricas.csv", "wb") as f:
        f.write(response.content)
    print("Arquivo CSV baixado com sucesso!")
else:
    print(f"Erro: {response.status_code} - {response.text}")
```

## Estrutura de Diretórios

A API espera que os arquivos CSV estejam organizados no seguinte formato:

```
./analytics/
  ├── [Nome do Vídeo 1]/
  │   ├── metricas.csv
  │   └── (outros arquivos)
  ├── [Nome do Vídeo 2]/
  │   ├── metricas.csv
  │   └── (outros arquivos)
  └── ...
```

## Formatos de Resposta

### CSV

Os arquivos CSV retornados seguem um formato padrão de métricas de análise de vídeo. O conteúdo exato depende do tipo de análise realizada no vídeo.

## Tratamento de Erros

A API utiliza códigos de status HTTP padrão para indicar o sucesso ou falha de uma requisição:

| Código | Descrição |
|--------|-----------|
| 200    | OK - A requisição foi bem-sucedida |
| 404    | Not Found - O recurso solicitado não foi encontrado |
| 500    | Internal Server Error - Ocorreu um erro no servidor |

## Limitações

- A API retorna apenas o primeiro arquivo CSV encontrado em cada pasta de vídeo
- Não há suporte para paginação na listagem de vídeos
- O tamanho máximo dos arquivos CSV não está limitado explicitamente

## Exemplos de Uso

### Listar Todos os Vídeos Disponíveis

**Requisição:**
```python
import requests
import json

response = requests.get("http://localhost:8000/list")

if response.status_code == 200:
    videos = response.json()
    print(f"Total de vídeos disponíveis: {videos['count']}")
    print("Vídeos:")
    for video in videos['folders']:
        print(f"- {video}")
else:
    print(f"Erro ao listar vídeos: {response.status_code} - {response.text}")
```

**Resposta:**
```
Total de vídeos disponíveis: 2
Vídeos:
- 2.1 [VSL IA] - Assistente x Agentes - Com delay
- 2.2 [VSL IA] - Assistente x Agentes - Sem delay
```

### Baixar um Arquivo CSV Específico

**Requisição:**
```python
import requests

def baixar_csv(video_name, output_file="metricas.csv"):
    """
    Baixa o arquivo CSV de um vídeo específico.
    
    Args:
        video_name: Nome do vídeo
        output_file: Nome do arquivo de saída (padrão: metricas.csv)
    
    Returns:
        bool: True se o download foi bem-sucedido, False caso contrário
    """
    url = f"http://localhost:8000/analytics/{video_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Arquivo salvo como {output_file}")
        return True
    else:
        print(f"Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
        return False

# Exemplo de uso
video = "2.1 [VSL IA] - Assistente x Agentes - Com delay"
baixar_csv(video, "metricas_video_2_1.csv")
```

### Usando em um Script para Baixar Todos os CSVs

```python
import requests
import os

def baixar_todos_csvs(diretorio_saida="./csvs"):
    """
    Baixa os CSVs de todos os vídeos disponíveis.
    
    Args:
        diretorio_saida: Diretório onde os arquivos serão salvos
    """
    # Cria o diretório se não existir
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
    
    # Obtém a lista de vídeos
    response = requests.get("http://localhost:8000/list")
    
    if response.status_code != 200:
        print(f"Erro ao obter lista de vídeos: {response.status_code}")
        return
    
    videos = response.json()['folders']
    print(f"Encontrados {len(videos)} vídeos para download.")
    
    # Baixa cada arquivo CSV
    for video in videos:
        # Cria um nome de arquivo baseado no nome do vídeo
        nome_arquivo = video.replace(" ", "_").replace("[", "").replace("]", "").replace(".", "_") + ".csv"
        caminho_arquivo = os.path.join(diretorio_saida, nome_arquivo)
        
        # Baixa o arquivo
        print(f"Baixando CSV para '{video}'...")
        url = f"http://localhost:8000/analytics/{video}"
        
        csv_response = requests.get(url)
        if csv_response.status_code == 200:
            with open(caminho_arquivo, "wb") as f:
                f.write(csv_response.content)
            print(f"✓ Salvo como {caminho_arquivo}")
        else:
            print(f"✗ Erro ao baixar: {csv_response.status_code}")
    
    print("Download completo!")

# Executa o download
baixar_todos_csvs()
```

## Usando com Pandas

Se você quiser carregar os dados diretamente em um DataFrame do pandas:

```python
import requests
import pandas as pd
from io import StringIO

def carregar_csv_para_dataframe(video_name):
    """
    Baixa um CSV e carrega diretamente em um DataFrame pandas.
    
    Args:
        video_name: Nome do vídeo
        
    Returns:
        DataFrame pandas ou None em caso de erro
    """
    url = f"http://localhost:8000/analytics/{video_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Carrega o CSV diretamente em um DataFrame
        return pd.read_csv(StringIO(response.text))
    else:
        print(f"Erro {response.status_code}: {response.json().get('detail', 'Erro desconhecido')}")
        return None

# Exemplo de uso
video = "2.1 [VSL IA] - Assistente x Agentes - Com delay"
df = carregar_csv_para_dataframe(video)

if df is not None:
    print(f"CSV carregado com sucesso! Formato: {df.shape}")
    print(df.head())
```
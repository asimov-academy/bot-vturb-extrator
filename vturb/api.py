from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import os
from pathlib import Path
import markdown2  # Precisamos instalar esta biblioteca: pip install markdown2
import re


app = FastAPI(
    title="Vturb Analytics API",
    description="API para acessar arquivos CSV de análise do VTurb",
    version="1.0.0",
)

# Base directory for analytics files
ANALYTICS_DIR = "./analytics"
HTML_TEMPLATE_PATH = "./assets/doc.html"

def process_markdown_for_better_display(html_content):
    """
    Processa o HTML gerado pelo markdown para melhorar a exibição.
    Adiciona classes e estruturas adicionais para uma melhor aparência.
    """
    # Converte blocos de código HTTP em endpoints estilizados
    http_pattern = r'<pre><code>(GET|POST|PUT|DELETE|PATCH) (.*?)</code></pre>'
    html_content = re.sub(
        http_pattern,
        r'<div class="endpoint"><div class="endpoint-header"><span class="endpoint-method">\1</span><span class="endpoint-path">\2</span></div></div>',
        html_content
    )
    
    # Adiciona classes para códigos de resposta HTTP
    html_content = re.sub(
        r'(\d{3}) (OK|Not Found|Internal Server Error)',
        lambda m: f'<span class="response-code response-code-{"success" if m.group(1).startswith("2") else "error" if m.group(1).startswith("4") or m.group(1).startswith("5") else "neutral"}">{m.group(1)}</span> {m.group(2)}',
        html_content
    )
    
    # Adiciona classes para melhorar a aparência das tabelas
    html_content = html_content.replace('<table>', '<table class="styled-table">')
    
    # Adiciona classes para parâmetros
    param_pattern = r'<strong>([A-Za-z_]+):</strong>'
    html_content = re.sub(
        param_pattern,
        r'<div class="parameter"><div class="parameter-name">\1</div>',
        html_content
    )
    
    # Cria um sumário de navegação no topo
    headings = re.findall(r'<h2 id="(.*?)">(.*?)</h2>', html_content)
    if headings:
        toc = '<div class="toc"><div class="toc-title">Conteúdo</div><ul>'
        for id, title in headings:
            toc += f'<li><a href="#{id}">{title}</a></li>'
        toc += '</ul></div>'
        
        # Insere o sumário após o primeiro h1
        h1_end = html_content.find('</h1>') + 5
        html_content = html_content[:h1_end] + toc + html_content[h1_end:]
    
    return html_content

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Endpoint raiz para renderizar a documentação da API"""
    # Caminho para o arquivo markdown de documentação
    docs_path = "docs/api.md"
    
    try:
        # Lê o conteúdo do arquivo markdown
        with open(docs_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Documentação não encontrada</h1><p>O arquivo de documentação não foi encontrado. Por favor, verifique se o arquivo api_documentation.md existe.</p>",
            status_code=404
        )
    
    # Converte o markdown para HTML usando markdown2
    html_content = markdown2.markdown(
        markdown_content,
        extras=["tables", "code-friendly", "fenced-code-blocks", "header-ids"]
    )
    
    # Processa o HTML para melhorar a exibição
    html_content = process_markdown_for_better_display(html_content)
    
    try:
        # Carrega o template HTML
        with open(HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()
        
        # Substitui o marcador de conteúdo pelo HTML gerado
        complete_html = template.replace("{content}", html_content)
    except FileNotFoundError:
        # Fallback caso o template não seja encontrado
        return HTMLResponse(
            content=f"<h1>Template HTML não encontrado</h1><p>O arquivo de template HTML não foi encontrado em {HTML_TEMPLATE_PATH}.</p>",
            status_code=404
        )
    
    return HTMLResponse(content=complete_html)

@app.get("/analytics/{video_name}")
def get_csv_file(video_name: str):
    """
    Busca e retorna o arquivo CSV de uma pasta específica.
    
    Args:
        video_name: Nome da pasta contendo o arquivo CSV do video
        
    Returns:
        FileResponse: Arquivo CSV para download
    """
    # Sanitize folder name to prevent directory traversal
    folder_name = os.path.basename(video_name)
    folder_path = os.path.join(ANALYTICS_DIR, folder_name)
    
    # Check if folder exists
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail=f"Pasta '{folder_name}' não encontrada")
    
    # Find CSV files in the folder
    csv_files = list(Path(folder_path).glob("*.csv"))
    
    if not csv_files:
        raise HTTPException(status_code=404, detail=f"Nenhum arquivo CSV encontrado na pasta '{folder_name}'")
    
    # Return the first CSV file found (according to requirements)
    csv_file_path = str(csv_files[0])
    file_name = os.path.basename(csv_file_path)
    
    return FileResponse(
        path=csv_file_path, 
        filename=file_name,
        media_type="text/csv"
    )

@app.get("/list")
def list_available_videos():
    """
    Lista todos os videos disponíveis no diretório de analises
    
    Returns:
        dict: Lista de videos disponíveis
    """
    try:
        folders = [
            folder for folder in os.listdir(ANALYTICS_DIR) 
            if os.path.isdir(os.path.join(ANALYTICS_DIR, folder))
        ]
        return {"folders": folders, "count": len(folders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar pastas: {str(e)}")
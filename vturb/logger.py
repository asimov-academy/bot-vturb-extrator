import os
import time
import datetime
import glob

# Criar a pasta de logs se não existir
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging to file with timestamp
current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"logs/{current_time}.txt"

# Função para limitar o número de arquivos de log
def limit_log_files(max_files=10):
    log_files = glob.glob("logs/*.txt")
    if len(log_files) > max_files:
        # Ordena os arquivos por data de modificação (mais antigos primeiro)
        log_files.sort(key=os.path.getmtime)
        # Remove os arquivos mais antigos, deixando apenas os 'max_files' mais recentes
        for file_to_remove in log_files[:-max_files]:
            try:
                os.remove(file_to_remove)
            except Exception as e:
                print(f"Erro ao remover arquivo de log antigo {file_to_remove}: {e}")

# Limitar o número de arquivos de log para 10
limit_log_files(10)

# Cores para o terminal (não afetam o arquivo)
class TermColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Tipos de log
class LogType:
    INFO = "INFO"
    SUCCESS = "SUCESSO"
    WARNING = "AVISO"
    ERROR = "ERRO"
    STEP = "ETAPA"
    DEBUG = "DEBUG"

# Variáveis para controle de tempo
start_times = {}

# Função para iniciar timer de uma operação
def start_timer(operation_name):
    start_times[operation_name] = time.time()

# Função para encerrar timer e retornar tempo decorrido
def end_timer(operation_name):
    if operation_name in start_times:
        elapsed = time.time() - start_times[operation_name]
        del start_times[operation_name]
        return elapsed
    return 0

# Create a custom logging function
def log(message, log_type=LogType.INFO, indent_level=0, show_time=False, operation_name=None, add_timestamp=True, write_to_file=True):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Adiciona informação de tempo decorrido se solicitado
    time_info = ""
    if show_time and operation_name and operation_name in start_times:
        elapsed = end_timer(operation_name)
        time_info = f" [{elapsed:.2f}s]"
    
    # Formatação de indentação
    indent = "  " * indent_level
    
    # Preparar prefixo baseado no tipo de log
    if log_type == LogType.SUCCESS:
        prefix = f"[✓]"
        terminal_color = TermColors.GREEN
    elif log_type == LogType.WARNING:
        prefix = f"[!]"
        terminal_color = TermColors.YELLOW
    elif log_type == LogType.ERROR:
        prefix = f"[✗]"
        terminal_color = TermColors.RED
    elif log_type == LogType.STEP:
        prefix = f"[→]"
        terminal_color = TermColors.BLUE
    elif log_type == LogType.DEBUG:
        prefix = f"[•]"
        terminal_color = TermColors.CYAN
    else:  # INFO
        prefix = f"[•]"
        terminal_color = ""
    
    # Largura fixa para cada parte do log para manter o alinhamento
    prefix_width = 3      # [•], [✓], etc.
    
    # Formatar a mensagem completa com alinhamento adequado
    timestamp_part = f"[{timestamp}] " if add_timestamp else ""
    log_message = f"{timestamp_part}{indent}{prefix:<{prefix_width}} {message}{time_info}"
    
    # Mostrar no terminal com cores
    print(f"{terminal_color}{log_message}{TermColors.ENDC}")
    
    # Salvar no arquivo (sem cores) apenas se write_to_file for True
    if write_to_file:
        with open(log_filename, "a") as log_file:
            log_file.write(log_message + "\n")

# Função para criar cabeçalho de seção
def log_section(title, level=1):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if level == 1:
        separator = "=" * 80
        # Exibir no terminal, mas não escrever no arquivo
        log(separator, LogType.INFO, add_timestamp=False, write_to_file=False)
        log(f" {title.upper()} ", LogType.INFO, add_timestamp=False, write_to_file=False)
        log(separator, LogType.INFO, add_timestamp=False, write_to_file=False)
        
        # Escrever no arquivo com timestamp apenas uma vez
        with open(log_filename, "a") as log_file:
            log_file.write(f"[{timestamp}] {separator}\n")
            log_file.write(f"[{timestamp}]  {title.upper()} \n")
            log_file.write(f"[{timestamp}] {separator}\n")
    elif level == 2:
        separator = "-" * 70
        # Exibir no terminal, mas não escrever no arquivo
        log(separator, LogType.INFO, add_timestamp=False, write_to_file=False)
        log(f" {title} ", LogType.INFO, add_timestamp=False, write_to_file=False)
        log(separator, LogType.INFO, add_timestamp=False, write_to_file=False)
        
        # Escrever no arquivo com timestamp apenas uma vez
        with open(log_filename, "a") as log_file:
            log_file.write(f"[{timestamp}] {separator}\n")
            log_file.write(f"[{timestamp}]  {title} \n")
            log_file.write(f"[{timestamp}] {separator}\n")
    else:
        # Para outros níveis, usar o método simples
        log_message = "\n" + f"--- {title} ---"
        log(log_message, LogType.INFO)

# Função para formatar números
def format_number(number):
    try:
        num = float(number)
        if num.is_integer():
            return f"{int(num):,}".replace(",", ".")
        return f"{num:,.2f}".replace(",", ".")
    except:
        return number

# Obtém o nome do arquivo de log atual
def get_log_filename():
    return log_filename

# Função para obter a hora atual formatada
def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
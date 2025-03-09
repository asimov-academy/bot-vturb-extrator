# Extrator de Análises do VTurb

> Solução automatizada para extração e disponibilização de dados analíticos da plataforma VTurb

## Visão Geral

O Extrator de análises do VTurb é uma solução completa projetada para automatizar a extração de dados analíticos de vídeos da plataforma VTurb e disponibilizá-los através de uma interface de API limpa. O projeto consiste em dois componentes principais:

1. **Bot de Automação**: Um script baseado em Python que navega pela interface do VTurb, extrai dados analíticos e os organiza em um formato estruturado
2. **API REST**: Uma implementação FastAPI que disponibiliza os dados extraídos através de endpoints bem definidos

## Principais Funcionalidades

### Bot de Automação

- Controle automatizado de navegador com suporte para modo headless
- Navegação inteligente através da estrutura de pastas e vídeos do VTurb
- Filtragem de parâmetros UTM e automação de download de CSV
- Tratamento robusto de erros e mecanismos de tentativas
- Registro detalhado de todas as operações
- Gerenciamento de execução programada

### API de Analytics

- Interface RESTful para acessar os dados extraídos
- Estrutura clara de endpoints
- Recuperação de arquivos CSV por nome de vídeo
- Listagem de vídeos disponíveis
- Documentação detalhada com elementos interativos

## Fluxo de Operação do Bot

1. **Inicialização**: Carrega variáveis de ambiente e inicializa o navegador
2. **Autenticação**: Faz login na plataforma VTurb
3. **Navegação por Pastas**: Identifica e processa pastas de vídeos
4. **Processamento de Vídeos**: Para cada vídeo em cada pasta:
   - Navega para a seção de analytics
   - Filtra por parâmetros UTM
   - Baixa relatórios CSV
   - Organiza arquivos no diretório de analytics
5. **Finalização**: Registra resumo e fecha o navegador

### Fluxo da automação

O diagrama abaixo ilustra o fluxo de operação da automação:

![Diagrama de Fluxo da Automação](docs/flow-diagram.jpeg)

## Estrutura do Projeto

```
├── analytics/                  # Diretório para armazenamento dos arquivos CSV extraídos
├── assets/                     # Templates HTML e assets
├── docs/                       # Documentação do projeto
│   └── api.md                  # Documentação detalhada da API
├── vturb                       # Diretório de todo o código
|   ├── browser.py              # Módulo de automação do navegador
|   ├── execution_manager.py    # Agendamento e gerenciamento de execução
|   ├── files.py                # Manipulação de operações de arquivos
|   ├── logger.py               # Utilitários de log
|   ├── main.py                 # Script principal de execução do bot
|   └── api.py                  # Implementação FastAPI
└── .env                        # Arquivo de variáveis de ambiente (não incluído no repositório)
```

## Configuração

### Variáveis de Ambiente

Para o funcionamento correto da aplicação, é necessário criar um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
EMAIL_LOGIN=seu_email@exemplo.com
PASSWORD_LOGIN=sua_senha
```

Estas credenciais são utilizadas pelo bot para autenticar-se na plataforma VTurb.

## Uso da API

A API fornece acesso aos dados analíticos extraídos. Para documentação detalhada da API, consulte a [Documentação da API](docs/api.md).

Endpoints de referência rápida:

- `GET /` - Página inicial da documentação da API
- `GET /list` - Lista todas as pastas de vídeos disponíveis
- `GET /analytics/{video_name}` - Baixa analytics CSV para um vídeo específico

```markdown
# Pipeline de Análise Arquitetural com CrewAI

Este projeto executa um pipeline de agentes de IA locais para pesquisar, auditar e documentar ferramentas de infraestrutura. O sistema gera uma análise técnica comparativa baseada em fatos e trade-offs operacionais.

A execução ocorre de forma local utilizando Ollama para garantir privacidade dos dados. O projeto intercepta buscas via SerpAPI para referenciar as fontes utilizadas no documento final. A lógica de execução está separada das definições de agentes por meio de arquivos de configuração YAML.

## Estrutura do Projeto

Certifique-se de que seus arquivos estão organizados desta forma antes de iniciar:

```text
meu_projeto/
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
├── custom_tools.py
├── crew.py
├── main.py
└── .env

```

## 1. Instalação do Ollama

O Ollama é o motor de inferência necessário para rodar os modelos locais.

**Linux:**
Execute o comando no terminal para instalar via script oficial:

```bash
curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh

```

**Windows:**
Faça o download do instalador executável no site oficial: https://ollama.com/download/windows. Execute o instalador e siga o assistente padrão.

Após a instalação, certifique-se de que o serviço está rodando em `http://localhost:11434`.

## 2. Download dos Modelos Locais

O script utiliza dois modelos distintos para otimizar velocidade e capacidade de contexto. Execute os comandos abaixo no terminal.

Para o agente de pesquisa e auditoria de infraestrutura:

```bash
ollama pull qwen3.5

```

Para o agente escritor e validador de qualidade (QA):

```bash
ollama pull glm-4.7-flash

```

## 3. Configuração do Ambiente e Pacotes com uv

O `uv` gerencia o Python, o ambiente virtual e as dependências do projeto de forma unificada.

**Instalar o uv:**
No Linux/macOS:

```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

```

No Windows (via PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

```

**Inicializar o projeto e instalar dependências:**
Na pasta raiz do seu projeto, execute o comando abaixo para inicializar o controle de pacotes (isso criará o `pyproject.toml`):

```bash
uv init

```

Em seguida, adicione os pacotes necessários. O `uv` criará o ambiente virtual automaticamente e gerará o `uv.lock`:

```bash
uv add crewai requests python-dotenv

```

## 4. Configuração das Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do projeto. Ele armazenará a chave da API de busca.

Insira o seguinte conteúdo:

```env
SERPAPI_API_KEY=sua_chave_api_aqui

```

Você pode criar uma conta gratuita em https://serpapi.com/ para obter a sua chave.

## 5. Execução do Pipeline

Com o Ollama rodando e o `.env` configurado, execute o script principal usando o comando `uv run`. Ele resolve o ambiente virtual automaticamente sem precisar de ativação manual:

```bash
uv run python main.py

```

## Arquivos Gerados

Após a execução bem-sucedida, o script gerará três arquivos na raiz do projeto:

* **`guia_implementacao_pratico.md`**: O documento final contendo a análise arquitetural e as referências injetadas.
* **`referencias_pesquisa.txt`**: O log bruto de todas as URLs orgânicas acessadas durante a etapa de pesquisa.
* **`metrics_usage.json`**: O registro de consumo de tokens da execução para fins de auditoria.

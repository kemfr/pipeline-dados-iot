# Pipeline de Dados com IoT e Docker

Projeto acadêmico da disciplina **Disruptive Architectures: IoT, Big Data e IA**. O pipeline lê registros de temperatura do conjunto *Temperature Readings: IoT Devices*, valida e transforma os dados com Python/Pandas, armazena-os no PostgreSQL executado em Docker e disponibiliza três views SQL para um dashboard interativo com Streamlit e Plotly.

## Tecnologias

- **Python e Pandas:** leitura, validação e transformação do CSV.
- **Docker e PostgreSQL 16:** armazenamento relacional em contêiner.
- **SQLAlchemy e psycopg2:** conexão entre Python e PostgreSQL.
- **Views SQL:** consultas agregadas para análise.
- **Streamlit e Plotly:** dashboard interativo.
- **Git e GitHub:** versionamento e publicação do projeto.

## Estrutura do projeto

```text
pipeline-iot/
├── data/                 # IOT-temp.csv (baixado separadamente; não versionado)
├── docs/                 # roteiro de documentação
├── screenshots/          # capturas reais do dashboard
├── sql/views.sql         # definição das três views
├── src/load_data.py      # valida e carrega o CSV no PostgreSQL
├── src/create_views.py   # cria/atualiza as views
├── src/dashboard.py      # dashboard Streamlit
├── .env.example          # modelo de configuração local
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Pré-requisitos

- Windows com Python instalado.
- Git instalado.
- Docker Desktop instalado e iniciado.
- Conta no Kaggle para baixar a base de dados.

## 2. Obter a base de dados

Baixe o conjunto [Temperature Readings: IoT Devices no Kaggle](https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices), extraia o arquivo e coloque `IOT-temp.csv` dentro de `data/`.

A versão utilizada neste projeto apresenta as colunas `id`, `room_id/id`, `noted_date`, `temp` e `out/in`. O script interpreta `noted_date` no formato `%d-%m-%Y %H:%M`.

## 3. Criar o contêiner PostgreSQL

Se o contêiner `postgres-iot` ainda não existir e a porta `5432` estiver livre, execute no CMD do Windows, substituindo `SUA_SENHA` por uma senha local de sua escolha:

```cmd
docker run --name postgres-iot -e POSTGRES_USER=iot_user -e POSTGRES_PASSWORD=SUA_SENHA -e POSTGRES_DB=iot_db -p 5432:5432 -d postgres:16
```

Para verificar o contêiner:

```cmd
docker ps
docker exec postgres-iot pg_isready -U iot_user -d iot_db
```

Se o contêiner já existir mas estiver parado, inicie-o com:

```cmd
docker start postgres-iot
```

## 4. Configurar o ambiente Python

Na pasta raiz do projeto, execute:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configurar a conexão

Copie o arquivo de exemplo e abra o arquivo local:

```cmd
copy .env.example .env
notepad .env
```

No arquivo `.env`, configure a URL com a mesma senha local usada ao criar o contêiner:

```dotenv
DATABASE_URL=postgresql+psycopg2://iot_user:SUA_SENHA@localhost:5432/iot_db
CSV_PATH=data/IOT-temp.csv
```

Substitua `SUA_SENHA` pela sua senha local. O arquivo `.env` está excluído do Git pelo `.gitignore` e **não deve ser publicado**. Não inclua senhas reais no código, README, commits ou capturas de tela.

## 6. Carregar os dados e criar as views

Com o Docker em execução, o `.env` configurado e o CSV dentro de `data/`, execute na raiz do projeto:

```cmd
python src/load_data.py
python src/create_views.py
```

O carregador valida as colunas esperadas e substitui o conteúdo da tabela `temperature_readings` pelos registros presentes no CSV. Isso evita duplicação causada por recargas. IDs da origem não são usados como chave primária, pois a exploração do arquivo encontrou um identificador repetido.

## 7. Executar o dashboard

```cmd
streamlit run src/dashboard.py
```

Abra o endereço local indicado pelo Streamlit, normalmente `http://localhost:8501`.

## 8. Views SQL

1. **`avg_temp_por_categoria`**: calcula quantidade de leituras, média, mínima e máxima por categoria `In`/`Out`. Na base analisada, `room_id/id` contém `Room Admin` em todas as linhas, por isso não seria útil comparar ambientes diferentes.
2. **`leituras_por_hora`**: conta leituras em cada hora do dia (0 a 23) e ajuda a identificar períodos de maior volume.
3. **`temp_max_min_por_dia`**: calcula temperaturas máxima, mínima e média e o volume de leituras para cada dia.

## 9. Evidências do dashboard

As capturas reais estão disponíveis na pasta `screenshots/`:

- `dashboard_01_visao_geral.png`: indicadores e gráficos de temperatura média e volume por hora.
- `dashboard_02_evolucao_e_insights.png`: evolução diária e destaques analíticos.

## 10. Resultados observados

Na execução documentada, o CSV apresentou **97.606 registros**, sem valores ausentes nas cinco colunas verificadas. Foram observados **97.605 IDs distintos**, portanto há um ID repetido, e as categorias contêm **20.345 leituras `In`** e **77.261 leituras `Out`**. A coluna `room_id/id` apresentou um único valor (`Room Admin`).

O dashboard exibiu uma temperatura média geral de **35,06** na unidade original do arquivo, sem conversão. O volume de leituras agrupadas por hora teve seu maior valor às **14:00**, com **7.248 leituras**. A categoria `Out` apresentou média de **36,27**, e a maior máxima diária mostrada foi **51**, em **30/09/2018**. Como o CSV não declara explicitamente a unidade de temperatura, o projeto não a identifica como °C ou °F.

## 11. Comandos Git e publicação

Na pasta do projeto, configure a identidade do Git (use seu nome e e-mail associados à sua conta):

```cmd
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@example.com"
```

Depois, crie o repositório local e faça o primeiro commit:

```cmd
git init
git add .
git status
git commit -m "Projeto inicial: Pipeline de Dados IoT"
git branch -M main
```

Crie um repositório público vazio no GitHub, copie a URL HTTPS dele e conecte o repositório local:

```cmd
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

Antes de publicar, verifique com `git status` que `.env`, `.venv/` e `data/IOT-temp.csv` não serão enviados. O README mantém o link do Kaggle em vez de redistribuir a base de dados.

## 12. Limitações

- A coluna `room_id/id` apresenta somente `Room Admin` na versão explorada da base.
- Existe ao menos um `id` repetido; o script preserva os registros em vez de descartar silenciosamente uma linha.
- O cabeçalho do CSV não especifica a unidade de temperatura. Os valores são apresentados na unidade original.
- Os resultados numéricos acima refletem a execução documentada com a versão do arquivo usada no desenvolvimento.

# Roteiro do relatório acadêmico (preencher após executar e validar o projeto)

## 1. Contextualização
Apresente o desafio de ingerir leituras de temperatura de dispositivos IoT, armazená-las de forma estruturada e transformá-las em informação consultável. Descreva a proposta: CSV → Pandas/Python → PostgreSQL em Docker → views SQL → dashboard Streamlit/Plotly.

## 2. Objetivos
- Automatizar a leitura e validação do CSV.
- Persistir os registros no PostgreSQL.
- Criar três views para agregar os dados.
- Apresentar indicadores e gráficos interativos.

## 3. Tecnologias e ambiente
Registre as versões efetivamente utilizadas de Python, Git, Docker Desktop e PostgreSQL. Descreva a instalação das dependências, o ambiente virtual e a configuração por `.env`. Insira evidências reais, sem exibir senhas.

## 4. Conjunto de dados e preparação
O arquivo analisado localmente contém 97.606 linhas e cinco colunas (`id`, `room_id/id`, `noted_date`, `temp`, `out/in`). Foram observados 97.605 IDs distintos, nenhuma célula ausente nas colunas verificadas e apenas um valor distinto (`Room Admin`) em `room_id/id`. Explique que os IDs repetidos são preservados e não são usados como chave primária. Descreva o formato de data usado pelo script (`%d-%m-%Y %H:%M`).

## 5. Pipeline e armazenamento
Explique a validação das colunas, conversão de datas/temperaturas, tabela `temperature_readings`, conexão via SQLAlchemy/psycopg2 e recarga do conjunto. Insira uma captura do resultado bem-sucedido do carregamento e a contagem confirmada no banco.

## 6. Views SQL
### 6.1 avg_temp_por_categoria
Explique a agregação das leituras por `In`/`Out`, com contagem, média, mínimo e máximo.
### 6.2 leituras_por_hora
Explique a contagem de registros em cada hora (0–23).
### 6.3 temp_max_min_por_dia
Explique os máximos, mínimos, média e contagem por data.

## 7. Dashboard
Insira capturas reais de cada gráfico. Descreva a média por categoria, a quantidade de leituras por hora e as temperaturas máximas/mínimas por dia. Indique que a unidade da temperatura não está explicitada no cabeçalho do CSV e, portanto, não deve ser presumida.

## 8. Resultados e insights
Preencha somente após consultar os resultados reais. Possíveis perguntas orientadoras: qual categoria tem maior média? Em quais horas há mais leituras? Em quais dias ocorreu a maior amplitude entre máxima e mínima? Algum resultado pode ser afetado pela quantidade desigual de registros entre categorias?

## 9. Aplicações práticas e limitações
Sugira monitoramento ambiental, identificação de períodos de maior variação térmica e alertas quando limites definidos pelo usuário forem ultrapassados. Diferencie essas possibilidades de funcionalidades realmente implementadas. Registre limitações da base, como a coluna de ambiente sem variação e a unidade de temperatura não explicitada.

## 10. Conclusão
Resuma o que foi implementado e validado, os resultados realmente observados e possíveis evoluções.

## 11. Referências
- Conjunto de dados: https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices
- Documentação do PostgreSQL, Docker, Pandas e Streamlit consultadas durante a execução.

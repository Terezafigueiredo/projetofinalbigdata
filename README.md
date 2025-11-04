🏆 Dashboard Brasileirão – Vitórias & Aproveitamento (2020–2024)
📌 Objetivo
Este projeto tem como objetivo analisar o desempenho dos times da Série A do Campeonato Brasileiro entre 2020 e 2024, destacando vitórias como mandante e visitante, aproveitamento e evolução ao longo dos anos.
🗂️ Etapas do Projeto
1. Coleta de Dados
Fonte: Kaggle

Dataset: mundo_transfermarkt_competicoes_brasileirao_serie_a.csv

Contém informações de partidas, times, gols e ano do campeonato.

2. Ambiente de Desenvolvimento
IDE: PyCharm e Jupyter Notebook

Frameworks e bibliotecas:

PySpark para processamento distribuído

Pandas para manipulação de dados tabulares

Plotly para visualizações interativas

Streamlit para criação da interface web

3. Limpeza e Transformação dos Dados
Filtro para partidas entre 2020 e 2024

Criação da coluna vencedor com base nos gols
Agrupamento por ano e time para calcular:

Vitórias como mandante e visitante

Total de jogos disputados

Aproveitamento (%) = vitórias / jogos × 100
4. Conversão para Pandas
Após o processamento com PySpark, os DataFrames foram convertidos para Pandas para facilitar a visualização com Plotly e Streamlit.

5. Visualizações Interativas
Gráficos de barras com os Top 10 times em vitórias como mandante e visitante.

Tabelas com os melhores aproveitamentos.

Gráfico de linha com a evolução de vitórias por time ao longo dos anos.

6. Interface com Streamlit
Interface responsiva com sidebar para seleção de ano e time.

Estilização com HTML/CSS embutido.

Layout dividido em colunas para melhor organização visual.

Autoria
Desenvolvido por Tereza Figueiredo como projeto de Big Data para a faculdade.

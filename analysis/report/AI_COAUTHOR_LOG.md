# AI Co-Author Log

## Ferramentas utilizadas

Durante o desenvolvimento foram utilizados ChatGPT e agentes de código para acelerar discovery, modelagem e implementação.

## Contexto fornecido para a IA

- Descrição do desafio.
- Estrutura dos cinco datasets.
- Requisitos da Seazone.
- Hipóteses de negócio.
- Objetivos de investimento e ROI.

## Onde a IA acelerou

### Discovery dos dados

Ajudou na identificação das chaves entre Airbnb, Price_AV, Mesh e VivaReal.

### Modelagem

Auxiliou na definição das métricas:

- Receita média.
- ROI.
- Payback.
- Impacto das amenities.
- Segmentação por região.

### Implementação

Acelerou a construção dos scripts em Polars e a organização da análise em módulos independentes.

## Onde a IA errou

### Price_AV

Inicialmente a IA tratou os preços como snapshot único.

Correção:
Foi considerada a dupla temporalidade (aquisição x estadia), conforme indicado pelo desafio.

### Receita absoluta x ROI

Inicialmente a recomendação privilegiava Meia Praia por possuir maior receita.

Correção:
A análise final priorizou ROI e payback, levando à recomendação de Tabuleiro dos Oliveiras.

## Speedup estimado

Entre 3x e 5x em relação ao desenvolvimento manual.

# AI Session 01 — Discovery dos dados

## Objetivo
Entender os datasets disponíveis para a análise de Itapema e identificar as principais chaves de relacionamento entre Airbnb, localização, preço, hosts e VivaReal.

## Contexto entregue para a IA
Foram apresentados os arquivos:
- Details_Itapema.csv
- Hosts_ids_Itapema.csv
- Mesh_Ids_Data_Itapema.csv
- Price_AV_Itapema.csv
- VivaReal_Itapema.csv

## Descobertas principais
- Mesh_Ids_Data_Itapema.csv foi tratado como fonte mais confiável para localização por conter latitude, longitude e suburb.
- Price_AV_Itapema.csv possui dupla temporalidade: data de aquisição e data de estadia.
- VivaReal_Itapema.csv foi usado para estimar custo de aquisição por região.
- Details_Itapema.csv concentrou atributos do imóvel, descrição e amenities.

## Decisões tomadas
- Usar região/bairro como unidade principal de análise.
- Usar Polars para processamento.
- Evitar Jupyter Notebook.
- Persistir outputs intermediários em CSV/Parquet dentro de analysis/output.

## Onde a IA ajudou
A IA acelerou o entendimento inicial das tabelas, sugeriu chaves de junção e ajudou a transformar perguntas abertas do desafio em métricas mensuráveis.

## Onde a IA precisou de correção
A IA inicialmente tendia a simplificar Price_AV como preço atual único. A correção foi tratar aquisição e estadia separadamente, respeitando o alerta do desafio.

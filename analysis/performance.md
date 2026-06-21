# Eficiência Computacional — Parte 1

Execução local usando Python + uv + Polars, sem Jupyter Notebook.

| Etapa | Script | Tempo real |
|---|---|---:|
| Amenities, perfil, regressão e feature importance | src/amenities_analysis.py | 7.017s |
| ROI por região 2025-2027 | src/roi_by_region_analysis.py | 0.483s |
| Análise de vista mar | src/sea_view_analysis.py | 0.598s |
| Projeção de ROI do empreendimento | src/roi_projection.py | 0.082s |
| Perfil por localização | src/location_profile_analysis.py | 0.335s |

## Tempo total medido

8.515s

## Observações

- O maior tempo de execução ficou em amenities_analysis.py, pois concentra enriquecimento de features, análise por distância da praia, regressão linear e Random Forest.
- O cálculo de ROI regional executou em menos de 1 segundo.
- A abordagem com Polars manteve o processamento simples, reproduzível e adequado ao volume do desafio.
- Como a execução foi local sobre CSV/Parquet, não houve custo de query em BigQuery ou Athena.

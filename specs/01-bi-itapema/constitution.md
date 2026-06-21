# Constitution — BI Itapema

- Toda análise deve ser reproduzível via linha de comando, sem Jupyter Notebook.
- Specs e plano devem existir antes do código de análise.
- O processamento deve usar Python com uv e pyproject.toml.
- Polars é a ferramenta padrão para wrangling tabular.
- Outputs intermediários devem ser versionáveis ou regeneráveis.
- Price_AV deve respeitar a dupla temporalidade: data de aquisição e data de estadia.
- Recomendações devem priorizar métricas explícitas: receita, ROI, payback e risco.
- Nenhuma decisão deve ser baseada apenas em receita absoluta quando ROI e custo de aquisição estiverem disponíveis.
- Limitações e hipóteses devem estar documentadas.

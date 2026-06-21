# Seazone AI Builder Challenge

Este repositório contém minha solução para o desafio técnico de Senior AI Builder da Seazone.

O objetivo foi abordar o problema sob diferentes perspectivas: análise de dados, especificação de produto, code review e liderança técnica, utilizando um fluxo de trabalho orientado por specs e acelerado por IA.

---

# Stack utilizada

- Python
- uv + pyproject.toml
- Polars
- Parquet
- DuckDB
- Git
- Claude / ChatGPT como AI Co-author

Sem Jupyter Notebook.

---

# Estrutura do projeto

```text
.
├── analysis/
├── ai-sessions/
├── data/
├── plano-squad/
├── report/
├── reviews/
├── specs/
│   ├── 01-bi-itapema/
│   └── 02-inteligencia-brasil/
└── README.md
```

---

# Parte 1 — BI Itapema

Objetivo:

Responder, com base nos dados fornecidos, as seguintes perguntas:

- Qual o melhor perfil de imóvel para investir?
- Qual a melhor localização em termos de receita?
- Quais características explicam as melhores receitas?
- Onde construir um prédio de 50 apartamentos?
- Qual o ROI projetado para 2025, 2026 e 2027?

## Principais análises

- Perfil dos imóveis
- Impacto das amenities
- Vista para o mar
- Distância da praia
- Regressão linear
- Random Forest
- Ranking das regiões
- Projeção de ROI
- Perfil ideal do empreendimento

## Tecnologias

- Python
- Polars
- Parquet

## Scripts

Todos os scripts estão em:

```text
analysis/src/
```

Os outputs gerados encontram-se em:

```text
analysis/output/
```

---

# Parte 2 — Inteligência Brasil

Especificação de um produto nacional para apoiar:

- Revenue Management
- Acquisition
- Origination

Documentos produzidos:

```text
specs/02-inteligencia-brasil/

constitution.md
spec.md
plan.md
```

O objetivo é transformar análises pontuais por cidade em uma plataforma escalável para o Brasil inteiro.

---

# Parte 3 — Code Review

Foi realizado o review do PR sintético `feature-system-price-v2`.

Entregas:

- Comentários inline no Pull Request.
- Documento de revisão:

```text
reviews/01-system-price-v2.md
```

Os principais pontos abordados foram:

- Confiança das métricas.
- Idempotência.
- Dependências desnecessárias.
- Segurança.
- Reprodutibilidade.

---

# Parte 4 — Plano 30/60/90

Plano de atuação como líder técnico contemplando:

- Primeiros 30 dias.
- Dias 30-60.
- Dias 60-90.
- Gestão de underperformance.

Arquivo:

```text
plano-squad/30-60-90.md
```

---

# Spec-driven Development

Todas as entregas foram orientadas por especificações.

## Parte 1

```text
specs/01-bi-itapema/

constitution.md
spec.md
plan.md
```

## Parte 2

```text
specs/02-inteligencia-brasil/

constitution.md
spec.md
plan.md
```

---

# AI Co-author

A IA foi utilizada como aceleradora do processo, principalmente para:

- Discovery dos dados;
- Exploração de hipóteses;
- Estruturação das análises;
- Discussões sobre modelagem;
- Revisão dos resultados;
- Code review;
- Elaboração dos documentos.

As sessões estão documentadas em:

```text
ai-sessions/
```

E os aprendizados e limitações encontram-se em:

```text
report/

AI_COAUTHOR_LOG.md
LIMITATIONS.md
```

---

# Reprodutibilidade

Instalação:

```bash
cd analysis

uv sync
```

Execução:

```bash
uv run src/amenities_analysis.py

uv run src/roi_by_region_analysis.py

uv run src/sea_view_analysis.py

uv run src/roi_projection.py

uv run src/location_profile_analysis.py
```

---

# Observações

O foco da solução foi priorizar:

- Clareza das decisões.
- Reprodutibilidade.
- Simplicidade.
- Pensamento de produto.
- Uso responsável de IA.
- Entregas incrementais.

Mais do que buscar a arquitetura mais complexa, o objetivo foi construir uma solução que pudesse ser compreendida, evoluída e operada por um time de forma sustentável.

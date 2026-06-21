# AI Session 02 — Modelagem da resposta principal

## Objetivo
Transformar as perguntas abertas do desafio em análises quantitativas reproduzíveis.

## Perguntas modeladas
1. Melhor perfil de imóvel para investir.
2. Melhor localização em termos de receita.
3. Características associadas às melhores receitas.
4. Recomendação para prédio de 50 apartamentos.
5. ROI projetado para 2025, 2026 e 2027.

## Métricas definidas
- Diária média e mediana por região.
- Receita potencial por região.
- Preço médio e mediano de venda por região.
- Preço por m².
- ROI.
- Payback.
- Impacto de amenities.
- Impacto de vista mar.
- Configuração recomendada por quartos/capacidade.

## Decisões de modelagem
- Receita foi estimada a partir dos preços disponíveis no Airbnb.
- Custo de aquisição foi estimado com base nos anúncios do VivaReal.
- A análise regional cruzou Airbnb e VivaReal usando suburb/region normalizado.
- Para recomendação de investimento, ROI e payback foram priorizados sobre receita absoluta.

## Onde a IA ajudou
A IA ajudou a organizar os scripts em análises separadas:
- amenities_analysis.py
- sea_view_analysis.py
- vivareal_roi_analysis.py
- roi_by_region_analysis.py
- roi_projection.py

## Onde a IA precisou de correção
A IA inicialmente sugeriu escolher Meia Praia por maior receita absoluta. A análise mostrou que Tabuleiro dos Oliveiras tinha melhor ROI e menor payback, portanto a recomendação foi ajustada.

# BI Itapema — Especificação de Análise

## Contexto

A Seazone avalia continuamente novas regiões para expansão de sua operação de short stay. O objetivo desta análise é determinar se Itapema (SC) representa uma oportunidade atrativa para aquisição e desenvolvimento de ativos imobiliários destinados à locação de curta temporada.

A análise utilizará dados de Airbnb, hosts, localização geográfica e mercado imobiliário residencial para identificar padrões de receita, demanda e potencial de retorno sobre investimento.

---

# Objetivos de Negócio

Responder às seguintes questões:

1. Qual o melhor perfil de imóvel para investimento em Itapema?
2. Qual a melhor localização em termos de geração de receita?
3. Quais características explicam os imóveis com melhor desempenho?
4. Onde construir um novo empreendimento com 50 apartamentos?
5. Qual o ROI projetado para 2025, 2026 e 2027?

---

# Entidades de Dados

## Listings Airbnb

Fonte: Details_Itapema.csv

Representa os imóveis anunciados na plataforma Airbnb.

Principais atributos:

* Tipo do imóvel
* Quantidade de quartos
* Quantidade de banheiros
* Capacidade de hóspedes
* Avaliação média
* Número de reviews
* Taxa de limpeza

---

## Hosts

Fonte: Hosts_ids_Itapema.csv

Representa os anfitriões responsáveis pelos imóveis.

Principais atributos:

* Tempo como host
* Status de Superhost
* Taxa de resposta
* Quantidade de reviews do host

---

## Geografia

Fonte: Mesh_Ids_Data_Itapema.csv

Representa a localização dos imóveis.

Principais atributos:

* Bairro
* Latitude
* Longitude

---

## Precificação

Fonte: Price_AV_Itapema.csv

Representa preços observados em múltiplas datas de aquisição para o mesmo período de estadia.

Observação crítica:

O dataset contém simultaneamente:

* Data de aquisição (aquisition_date)
* Data de estadia (date)

Essas dimensões temporais devem ser tratadas separadamente para evitar interpretações incorretas de receita e comportamento de preço.

---

## Mercado Imobiliário

Fonte: VivaReal_Itapema.csv

Representa imóveis disponíveis para venda.

Principais atributos:

* Preço de venda
* Área útil
* Bairro
* Quantidade de quartos
* Quantidade de banheiros

---

# Hipóteses

## H1 — Capacidade e receita

Imóveis com maior capacidade de hóspedes apresentam receita anual superior devido ao aumento do ticket médio por reserva.

---

## H2 — Qualidade operacional

Imóveis administrados por Superhosts apresentam melhor desempenho financeiro do que imóveis administrados por hosts comuns.

---

## H3 — Localização

Existem bairros significativamente superiores em potencial de receita devido à proximidade de áreas turísticas e concentração de demanda.

---

## H4 — Tipologia ideal

Apartamentos de médio porte (2 a 3 quartos) apresentam a melhor relação entre custo de aquisição e geração de receita.

---

## H5 — Desenvolvimento imobiliário

A combinação entre dados de receita Airbnb e preços de venda permite identificar regiões onde novos empreendimentos apresentam ROI superior à média da cidade.

---

# Métricas de Avaliação

## Receita

* Receita anual estimada
* Receita média por imóvel
* Receita média por bairro
* Receita média por tipologia

## Precificação

* ADR (Average Daily Rate)
* Distribuição de preços por temporada
* Evolução do preço por data de aquisição

## Qualidade

* Rating médio
* Reviews médios
* Receita por faixa de avaliação

## Mercado

* Preço médio de aquisição
* Preço por metro quadrado
* Receita anual por real investido

## Investimento

* ROI anual
* ROI acumulado
* Payback estimado

---

# Critérios para Definição do Melhor Investimento

Um investimento será considerado superior quando apresentar simultaneamente:

1. Receita anual elevada.
2. Boa recorrência de demanda.
3. Custo de aquisição competitivo.
4. Potencial de escalabilidade operacional.
5. ROI superior à média da cidade.

Nenhuma métrica isolada será utilizada para tomada de decisão.

---

# Estratégia Analítica

A análise será conduzida em quatro etapas:

1. Consolidação das fontes em uma camada analítica única.
2. Identificação dos fatores que explicam receita.
3. Avaliação geográfica dos bairros.
4. Simulação de um empreendimento com 50 unidades e projeção financeira para 2025–2027.

---

# Riscos e Limitações

* Os dados representam um recorte temporal específico.
* Não há confirmação de ocupação efetiva dos imóveis.
* Custos de construção não estão presentes na base e exigirão premissas externas.
* Mudanças macroeconômicas futuras não podem ser previstas a partir do dataset.
* A receita observada em Airbnb não garante repetição futura do mesmo desempenho.

---

# Definição de Sucesso

A análise será considerada concluída quando for possível recomendar:

* O melhor bairro para investimento.
* O melhor perfil de imóvel.
* O desenho recomendado para um empreendimento de 50 unidades.
* Uma estimativa justificada de ROI para os anos de 2025, 2026 e 2027.
